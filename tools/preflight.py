"""紙芝居モード（めたん×ずんだもん）のシーン YAML を、レンダ前に一括で検査するツール。

冷笑ずんだもん版（2026-09-05〜06）の試写で見つかった不具合のうち、機械的に検出できる種類
（試写10回中4回の原因）を、レンダ前に1コマンドでまとめて検出する（2026-09-06 追加）。

検出項目（詳細は各チェック関数のdocstring）:
    1. 読みの突合   — narration を VOICEVOX（audio_query）に投げ、返る kana と fugashi
       （形態素解析。import 不可時のみ pykakasi）による読みを比較する。差分候補を
       列挙する（ASR を通さないので決定的）。
    2. 長いキュー   — 字幕キュー（`text_cues.split_into_sentences`）が50字を超えるもの。
    3. 板だけの区間 — `board` ビートの推定尺が10秒を超えるもの（参考として image/diagram の
       45秒超も列挙）。
    4. 文字の警告   — telop・図解ラベルに en dash 等フォントで描けない可能性のある文字。
    5. ラベル長     — sketch/narrative の要素ラベルが仕様上限を超えるもの（validate でも
       弾かれるが、まとめて見たい）。
    6. 素材ファイル — `--assets-dir` 指定時、image ビートの `scene_NN_beat{slot}.*` の有無。

使い方:
    PYTHONUTF8=1 C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe ^
        tools/preflight.py <yaml> [--assets-dir <dir>] [--out references/xxx-preflight.md] ^
        [--skip-tts] [--voicevox-url http://127.0.0.1:50021]

終了コードは、1〜6のいずれかに該当があれば1（レンダ前に直す）。`--skip-tts` で1（VOICEVOX
突合）を飛ばせる（VOICEVOXを起動していない環境向け）。

前提:
    - Python は script-to-video の venv を使う（Bash の `python` は Microsoft Store のスタブ
      では動かない）。fugashi・unidic-lite（形態素解析。無ければ pykakasi にフォール
      バック）・PyYAML・script_to_video を import できること。
    - 1を実行するには VOICEVOX ENGINE（http://127.0.0.1:50021）が起動していること。
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pykakasi

STV_ROOT = Path(r"C:\Users\shuya\Projects\script-to-video")
sys.path.insert(0, str(STV_ROOT / "src"))

from script_to_video.lint import build_beat_numbering  # noqa: E402
from script_to_video.loader import load_scene_yaml  # noqa: E402
from script_to_video.render import resolve_beat_asset  # noqa: E402
from script_to_video.schema import (  # noqa: E402
    NARRATIVE_CAPTION_MAX_LENGTH,
    NARRATIVE_LABEL_MAX_LENGTH,
    NARRATIVE_RESULT_MAX_LENGTH,
    SKETCH_TEXT_MAX_LENGTH,
    SKETCH_VALUE_MAX_LENGTH,
    DiagramSketch,
    NarrativeCaption,
    NarrativeChain,
    NarrativeConverge,
    NarrativeRadiate,
    NarrativeResult,
    NarrativeRow,
    Reading,
    Scene,
    VideoDocument,
)
from script_to_video.text_cues import split_into_sentences  # noqa: E402
from script_to_video.tts import (  # noqa: E402
    DEFAULT_BASE_URL,
    VoicevoxClient,
    VoicevoxConnectionError,
    resolve_voices,
)

# ============================================================
# 定数
# ============================================================

LONG_CUE_MAX_CHARS = 50
"""字幕キューがこれを超えると2行に収まらず末尾が切れる（CLAUDE.md 指定の目安）。"""

BOARD_MAX_SECONDS = 10.0
"""`board` ビート（黒板・人形だけの区間）の推定尺がこれを超えると単調に見える目安。"""

IMAGE_DIAGRAM_REFERENCE_MAX_SECONDS = 45.0
"""`image`/`diagram` ビートの推定尺がこれを超える箇所は参考として列挙する（警告ではない）。"""

SUSPECT_CHARS: dict[str, str] = {
    "–": "en dash（–）",
    "—": "em dash（—）",
    "―": "水平線（―）",
    "−": "minus sign（−）",
    "‐": "hyphen（‐）",
    "‑": "non-breaking hyphen（‑）",
}
"""既知の「フォントで描けない可能性がある文字」（2026-09 に「1983–84」の en dash が
□ になった実例あり。紙芝居モードの黒板テロップは UD デジタル教科書体系フォント
`kamishibai.CHALK_FONT_CANDIDATES` を使い、教科書体は Web 記事からのコピペで混入しがちな
欧文タイポグラフィ記号（ダッシュ類）を持たないことが多い）。

**注意**: 「→」「①」のような矢印・丸数字は、複数の既公開動画
（例: scripts/20260904-dopagaki-kamishibai）の telop で常用されておりレンダ実績があるため
ここには含めない（一般句読点ブロックを丸ごと疑うと大量の誤検出になる。2026-09-06 確認）。
実際に描けなかった実例（ダッシュ・マイナス記号）にスコープを絞る。
"""


def find_suspect_chars(text: str) -> list[tuple[str, str]]:
    """`text` 中の「フォントで描けない可能性がある文字」を列挙する（(文字, 説明) のリスト）。

    `SUSPECT_CHARS` に載っている既知の記号（欧文ダッシュ類）に加え、絵文字（U+1F000以降）と
    私用領域（U+E000-F8FF。文字化け・アイコンフォント文字の混入の疑い）だけを検出する。
    矢印・丸数字・一般的な日本語記号は既に常用実績があるため対象外（上記コメント参照）。
    """

    found: list[tuple[str, str]] = []
    for ch in text:
        if ch in SUSPECT_CHARS:
            found.append((ch, SUSPECT_CHARS[ch]))
        elif ord(ch) >= 0x1F000:
            found.append((ch, f"絵文字等（U+{ord(ch):04X}）"))
        elif 0xE000 <= ord(ch) <= 0xF8FF:
            found.append((ch, f"私用領域の文字（U+{ord(ch):04X}）"))
    return found


# ============================================================
# チェック1: 読みの突合（VOICEVOX ⇄ 辞書）
# ============================================================

try:
    import fugashi

    _TAGGER = fugashi.Tagger()
    _FUGASHI_AVAILABLE = True
except Exception:
    _TAGGER = None
    _FUGASHI_AVAILABLE = False
"""参照側（narration テキストの「あるべき読み」）の取得は fugashi（MeCab + UniDic-lite）を
既定にする（2026-09-06、オーケストレーター指示で pykakasi から差し替え）。pykakasi は
形態素解析器ではなく漢字→かな変換ツールに過ぎず、複合語・活用語の読み取り違え
（「力」→りき、「断った」→た、「棘」→なつめ、「優れ」→まさ 等）が差分の大半を占めて
実運用で埋もれてしまっていた。fugashi は実際の形態素解析結果の `pron`（発音どおりの読み。
助詞「は」「を」の音便化も込み）を返すため、これらの誤りが解消される。fugashi が
import できない環境（未インストール等）でのみ pykakasi にフォールバックする
（`_dict_side_kana_pykakasi`）。
"""

_KKS = pykakasi.kakasi()
"""pykakasi は fugashi 不使用時のフォールバック専用（既定経路では使わない）。"""

_KANA_PUNCT_RE = re.compile(r"[’'_/、。？！?!「」…〜・\s　]")
_KANA_ONLY_RE = re.compile(r"^[ぁ-んァ-ヶー]+$")

_NUMBER_MASK_RE = re.compile(r"\d+(?:[.,]\d+)*%?")
_NUMBER_MASK_TOKEN = "スウジ"
"""数字（「数字」は CLAUDE.md 指定の既知ノイズ）を比較前にマスクするためのプレースホルダ。

fugashi・pykakasi のどちらも算用数字はかな化できず（`fugashi` は該当トークンの
`pron`/`kana` が None になる）、逆に VOICEVOX 側の数の読み方には「400=よんひゃく」
「50%=ごじゅっパーセント」等の例外が多く、両者を同じ規則で完全一致させるのは割に合わない
（実際どちらの読みで喋っているかを一致させたいのではなく、数字が原因のノイズを除きたいだけ）。
そこで数字部分を固定の仮名語（`スウジ`）に置き換えてから両側を比較する: 同じプレースホルダは
VOICEVOX にも参照側にも同じ「すうじ」としか読めないため、実際の読み方によらず必ず一致し、
数字起因の差分だけを機械的に消せる。"""


_LATIN_MASK_RE = re.compile(r"[A-Za-z]+")
_LATIN_MASK_TOKEN = "ローマジ"
"""アルファベット表記（SNS・OECD 等）の英字連続を比較前にマスクするためのプレースホルダ。

CLAUDE.md が列挙した既知ノイズには含まれないが、英字は fugashi・pykakasi のどちらでも
かな化できずそのまま素通しする一方、VOICEVOX は「エスエヌエス」のように必ず音読みするため、
英字略語が登場するたびに機械的な差分が発生してしまう（誤読ではなくツールの限界による
ノイズ）。数字と同じ理由・同じ手法でマスクする。"""


def _mask_noise_tokens(text: str) -> str:
    text = text.replace("%", "パーセント")
    text = _NUMBER_MASK_RE.sub(_NUMBER_MASK_TOKEN, text)
    return _LATIN_MASK_RE.sub(_LATIN_MASK_TOKEN, text)


def _kata_to_hira(s: str) -> str:
    """カタカナをひらがなへ変換する（「ー」等の記号はそのまま。範囲外の文字も素通し）。"""

    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


_SEION_ROWS = {
    "ア": "アイウエオ",
    "カ": "カキクケコ",
    "ガ": "ガギグゲゴ",
    "サ": "サシスセソ",
    "ザ": "ザジズゼゾ",
    "タ": "タチツテト",
    "ダ": "ダヂヅデド",
    "ナ": "ナニヌネノ",
    "ハ": "ハヒフヘホ",
    "バ": "バビブベボ",
    "パ": "パピプペポ",
    "マ": "マミムメモ",
    "ラ": "ラリルレロ",
}
_KANA_VOWEL_TABLE: dict[str, str] = {}
for _row in _SEION_ROWS.values():
    for _ch, _v in zip(_row, "アイウエオ"):
        _KANA_VOWEL_TABLE[_ch] = _v
_KANA_VOWEL_TABLE.update({"ヤ": "ア", "ユ": "ウ", "ヨ": "オ", "ワ": "ア", "ヲ": "オ"})
_KANA_VOWEL_TABLE.update(
    {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ャ": "ア", "ュ": "ウ", "ョ": "オ"}
)


def _expand_chouon(kana: str) -> str:
    """長音記号「ー」を、直前モーラの母音そのもの（カタカナ）に展開する。

    fugashi の `feature.pron` は長音を「ー」記号で返す（例:「投稿」→「トーコー」）が、
    VOICEVOX の `audio_query` の kana は長音を使わず、常に母音を綴った表記で返す
    （例:「投稿」→「トオコオ」、「先生」→「センセエ」。2026-09-06 に実機の
    `/audio_query` で実測して確認）。「ー」は本来「直前の母音を繰り返す」という記号の
    定義そのものなので、直前モーラの母音（ア/イ/ウ/エ/オ）へ機械的に置き換えれば
    VOICEVOX の表記と一致する。促音「ッ」・撥音「ン」は母音を持たないため、
    直前の母音追跡を変えずに素通しする。
    """

    out: list[str] = []
    last_vowel: str | None = None
    for ch in kana:
        if ch == "ー":
            out.append(last_vowel or "ー")
            continue
        vowel = _KANA_VOWEL_TABLE.get(ch)
        if vowel is not None:
            last_vowel = vowel
        elif ch not in ("ッ", "ン"):
            last_vowel = None
        out.append(ch)
    return "".join(out)


_PLACEHOLDER_BASE = 0xE000
"""`readings` の読み修正を fugashi のトークナイズに通さず直接差し込むための私用領域
（Private Use Area）プレースホルダの開始コードポイント。"""


def _dict_side_kana_fugashi(text: str, readings: list[Reading] | None) -> str:
    """narration テキストの「あるべき読み」を fugashi（形態素解析）でひらがな化する。

    `readings`（YAML の読み修正指定。surface→カタカナ読み）は、対象語を1文字の私用領域
    プレースホルダに一時的に置き換えてから形態素解析にかける。指定読みは「無力感」の
    ように小書き文字（ゃゅょ等）を含むことがあり、ひらがな文字列としてそのまま
    形態素解析に通すと文字種の変わり目でしか区切れない fugashi の未知語処理が
    「りょ」を「り」＋「ょ」に分割し、「ょ」を独立の「ヨ」と誤読することがある
    （2026-09-06 実データで確認）。プレースホルダなら1文字の未知語として必ず単独の
    トークンになるため、指定読みをそのまま（かな化・チェック抜きで）差し込める。

    数字・英字略語は `_mask_noise_tokens` で先にマスクする（fugashi はどちらも
    `pron` が取れない）。各トークンの読みは `pron`（発音どおり。助詞「は」「を」の
    音便化も含む）を優先し、`pron` が取れない未知語はサーフェス自体がかな
    （ひらがな／カタカナ）ならそれをそのまま使う（例: 数字・英字マスクの
    プレースホルダ「スウジ」「ローマジ」はこの経路で正しく拾われる）。それでも
    読みが取れない場合（辞書に無い漢字等）は諦めて無視する。
    """

    placeholder_map: dict[str, str] = {}
    for index, reading in enumerate(readings or []):
        if reading.surface not in text:
            continue
        placeholder = chr(_PLACEHOLDER_BASE + index)
        placeholder_map[placeholder] = reading.reading
        text = text.replace(reading.surface, placeholder)
    text = _mask_noise_tokens(text)

    parts: list[str] = []
    for word in _TAGGER(text):
        surface = word.surface
        if surface in placeholder_map:
            parts.append(placeholder_map[surface])
            continue
        pron = word.feature.pron
        if pron:
            parts.append(pron)
        elif pron == "":
            continue
        elif surface and _KANA_ONLY_RE.fullmatch(surface):
            parts.append(surface)
        # else: pron が取れない未知語（辞書に無い漢字等）。稀なので諦めて無視する。

    kana = _expand_chouon("".join(parts))
    kana = _kata_to_hira(kana)
    return _KANA_PUNCT_RE.sub("", kana)


_NOISE_GROUPS: tuple[frozenset[str], ...] = (frozenset({"", "ひと", "にん", "じん"}),)
"""pykakasi フォールバック専用の既知ノイズ（CLAUDE.md 指定。「人」のひと／にん）。「人」は
「有名人（じん）」のように複合語内では別の読みになるため、特定の読みへ強制変換はせず、
ひと・にん・じん を丸ごと同値として扱う。fugashi 経路では形態素解析で複合語の文脈ごと
読みが決まる（辞書に無い複合語は fugashi 側も誤ることがあるが、それは差分として出して
人が判断する対象なのでここでは揉み消さない。2026-09-06 オーケストレーター指示）。"""


def _is_known_noise(a: str, b: str) -> bool:
    return any(a in group and b in group for group in _NOISE_GROUPS)


def _dict_side_kana_pykakasi(text: str, readings: list[Reading] | None) -> str:
    """`_dict_side_kana_fugashi` が使えない場合のフォールバック（fugashi 差し替え前の実装）。

    pykakasi は真の形態素解析器ではなく文字種の変わり目でしか語を区切れないため、
    助詞「は」「を」を独立トークンとして単独判定できないことが多い（例:「人はもっと」の
    「はもっと」）。そのため助詞単位の変換では取りこぼしが大きく、かな化した文字列
    全体に対する一括の文字置換（「は」→「わ」・「を」→「お」）で妥協する。
    """

    for reading in readings or []:
        text = text.replace(reading.surface, reading.reading)
    text = _mask_noise_tokens(text)

    kana = "".join(item["hira"] for item in _KKS.convert(text))
    kana = kana.replace("は", "わ").replace("を", "お")
    kana = _KANA_PUNCT_RE.sub("", kana)
    return kana.replace("ー", "")


def _dict_side_kana(text: str, readings: list[Reading] | None) -> str:
    """narration テキストの「あるべき読み」をひらがなで返す（比較対象の一方）。

    既定は fugashi（`_dict_side_kana_fugashi`）。import に失敗した環境でのみ
    pykakasi（`_dict_side_kana_pykakasi`）にフォールバックする。
    """

    if _FUGASHI_AVAILABLE:
        return _dict_side_kana_fugashi(text, readings)
    return _dict_side_kana_pykakasi(text, readings)


def _vv_side_kana(client: VoicevoxClient, text: str, style_id: int) -> str:
    """narration テキストを VOICEVOX の audio_query に投げ、実際の読み（kana）をひらがなで返す。

    `_dict_side_kana` と同じく数字・英字略語は `_mask_noise_tokens` で先にマスクする
    （マスクしないと VOICEVOX 側だけ実際の読み方〔「2400」→「にせんよんひゃく」等〕になり、
    対象外のはずのこのチェックで無意味な差分が大量に出てしまう）。VOICEVOX の kana は
    長音を使わず母音を綴る表記で返すため（`_expand_chouon` のdocstring参照）、
    `_dict_side_kana` 側の「ー」展開と表記を揃えられる。
    """

    text = _mask_noise_tokens(text)
    query = client.audio_query(text, style_id)
    kana = _KANA_PUNCT_RE.sub("", query["kana"])
    kana = _kata_to_hira(kana)
    return kana.replace("ー", "")


def _diff_fragments(vv_kana: str, dict_kana: str, *, apply_noise_filter: bool) -> list[tuple[str, str]]:
    """2文字以上のずれだけを差分として拾う（1文字のゆらぎはノイズが多すぎるため。
    参考実装 kana_diff.py と同じ閾値）。`apply_noise_filter` が真のとき（pykakasi
    フォールバック時のみ）、既知ノイズ（`_is_known_noise`）を除外する。fugashi 経路では
    揉み消さず全差分をそのまま返す（2026-09-06 オーケストレーター指示）。
    """

    sm = difflib.SequenceMatcher(None, vv_kana, dict_kana)
    diffs = [
        (vv_kana[i1:i2], dict_kana[j1:j2])
        for tag, i1, i2, j1, j2 in sm.get_opcodes()
        if tag != "equal" and (i2 - i1 >= 2 or j2 - j1 >= 2)
    ]
    if not apply_noise_filter:
        return diffs
    return [(a, b) for a, b in diffs if not _is_known_noise(a, b)]


def check_reading_diffs(document: VideoDocument, base_url: str) -> list[str]:
    """narration 全セグメントを VOICEVOX へ投げ、参照側（fugashi。フォールバック時 pykakasi）の
    読みとの差分を列挙する。

    先に YAML の `readings` を VOICEVOX のユーザー辞書へ登録する（レンダ時と同じ状態で
    読みを確認するため）。VOICEVOX に接続できない場合はその旨を1行だけ返す。
    """

    try:
        client = VoicevoxClient(base_url=base_url)
        for scene in document.scenes:
            for reading in scene.readings or []:
                client.upsert_user_dict_word(reading.surface, reading.reading)
        voice_map = resolve_voices(client, document)
    except VoicevoxConnectionError as exc:
        return [f"VOICEVOXに接続できません（{exc}）。エンジンを起動するか --skip-tts を使ってください。"]

    findings: list[str] = []
    if not _FUGASHI_AVAILABLE:
        findings.append(
            "警告: fugashi が import できないため pykakasi にフォールバックしています"
            "（読みの精度が下がります。`uv pip install fugashi unidic-lite` を確認してください）。"
        )
    for scene in document.scenes:
        for index, segment in enumerate(scene.narration, start=1):
            style_id = voice_map.get(segment.speaker, voice_map.get(None))
            if style_id is None:
                continue
            vv_kana = _vv_side_kana(client, segment.text, style_id)
            dict_kana = _dict_side_kana(segment.text, scene.readings)
            if vv_kana == dict_kana:
                continue
            diffs = _diff_fragments(vv_kana, dict_kana, apply_noise_filter=not _FUGASHI_AVAILABLE)
            if not diffs:
                continue
            speaker = f"[{segment.speaker}] " if segment.speaker else ""
            diff_text = " ; ".join(f"VV:{a}/辞書:{b}" for a, b in diffs)
            findings.append(
                f"シーン{scene.id} セグメント{index} {speaker}| {segment.text[:40]} | {diff_text}"
            )
    return findings

# ============================================================
# チェック2: 長いキュー（50字超）
# ============================================================


def check_long_cues(document: VideoDocument) -> list[str]:
    """字幕キュー（`split_into_sentences` の1文）が `LONG_CUE_MAX_CHARS` を超えるものを列挙する。"""

    findings: list[str] = []
    for scene in document.scenes:
        for seg_index, segment in enumerate(scene.narration, start=1):
            for cue in split_into_sentences(segment.text):
                cue = cue.strip()
                if len(cue) > LONG_CUE_MAX_CHARS:
                    findings.append(
                        f"シーン{scene.id} セグメント{seg_index}: {len(cue)}字 — 「{cue}」"
                    )
    return findings


# ============================================================
# チェック3: 板だけの区間（board 10秒超・image/diagram 45秒超は参考）
# ============================================================


@dataclass
class DurationFindings:
    board_over: list[str]
    image_diagram_over: list[str]


def check_beat_durations(document: VideoDocument) -> DurationFindings:
    """`build_beat_numbering` の推定尺（350字/分換算の近似。`validate` と同じ計算）から、
    `board` ビートが `BOARD_MAX_SECONDS` を超えるものと、参考として `image`/`diagram` が
    `IMAGE_DIAGRAM_REFERENCE_MAX_SECONDS` を超えるものを列挙する。
    """

    board_over: list[str] = []
    image_diagram_over: list[str] = []
    for row in build_beat_numbering(document):
        cue = f"キュー{row.cue_number}" if row.cue_number is not None else "キュー-"
        line = (
            f"シーン{row.scene_id}: {cue} {row.kind} 約{row.estimated_seconds:.1f}秒"
            f" — {row.cut_reason_prefix}"
        )
        if row.kind == "board" and row.estimated_seconds > BOARD_MAX_SECONDS:
            board_over.append(line)
        elif row.kind in ("image", "diagram") and row.estimated_seconds > IMAGE_DIAGRAM_REFERENCE_MAX_SECONDS:
            image_diagram_over.append(line)
    return DurationFindings(board_over=board_over, image_diagram_over=image_diagram_over)


# ============================================================
# テロップ・図解ラベルの抽出（チェック4・5共用）
# ============================================================


@dataclass
class TextSurface:
    scene_id: int
    location: str
    text: str
    max_length: int | None = None
    """診断対象の文字数上限（sketch/narrative ラベルのみ設定。telop 等は None＝チェック5対象外）。"""


def _diagram_label_surfaces(scene_id: int, prefix: str, diagram: object) -> list[TextSurface]:
    """1件の図解（sketch/narrative）から、ラベル文字列（(位置, 文字列, 上限) 付き）を集める。

    sketch/narrative 以外の型（旧ピル図解 buildup/flow/comparison・chart）は対象外
    （CLAUDE.md の対象記述どおり。旧ピル図解は新規台本では非推奨のため）。
    """

    surfaces: list[TextSurface] = []
    if isinstance(diagram, DiagramSketch):
        for cell in diagram.cells:
            if cell.text:
                surfaces.append(
                    TextSurface(scene_id, f"{prefix} sketchセル({cell.id}).text", cell.text, SKETCH_TEXT_MAX_LENGTH)
                )
            if cell.value:
                surfaces.append(
                    TextSurface(scene_id, f"{prefix} sketchセル({cell.id}).value", cell.value, SKETCH_VALUE_MAX_LENGTH)
                )
        if diagram.caption is not None:
            surfaces.append(
                TextSurface(scene_id, f"{prefix} sketch caption", diagram.caption.text, NARRATIVE_CAPTION_MAX_LENGTH)
            )
    elif isinstance(diagram, (NarrativeRadiate, NarrativeConverge, NarrativeRow, NarrativeChain)):
        for node in diagram.nodes:
            text = getattr(node, "text", None)
            if not text:
                continue
            if isinstance(node, NarrativeResult):
                limit = NARRATIVE_RESULT_MAX_LENGTH
            elif isinstance(node, NarrativeCaption):
                limit = NARRATIVE_CAPTION_MAX_LENGTH
            else:
                limit = NARRATIVE_LABEL_MAX_LENGTH
            node_id = getattr(node, "id", "")
            surfaces.append(
                TextSurface(scene_id, f"{prefix} narrative/{diagram.layout}({node_id}).text", text, limit)
            )
    return surfaces


def collect_text_surfaces(document: VideoDocument) -> list[TextSurface]:
    """telop・chapter_title・emphasis・beatのtelop・図解ラベルを1つのリストへ集約する。

    チェック4（要確認文字）はこの全件を対象にし、チェック5（ラベル長）は `max_length`
    が設定されている（＝sketch/narrative ラベル）ものだけを対象にする。
    """

    surfaces: list[TextSurface] = []
    for scene in document.scenes:
        if scene.telop:
            surfaces.append(TextSurface(scene.id, "scene.telop", scene.telop))
        if scene.chapter_title:
            surfaces.append(TextSurface(scene.id, "chapter_title", scene.chapter_title))
        for item in scene.emphasis or []:
            surfaces.append(TextSurface(scene.id, f"emphasis(at={item.at})", item.text))
        for beat in scene.beats or []:
            if beat.type in ("image", "board") and beat.telop:
                surfaces.append(
                    TextSurface(scene.id, f"beats[{beat.type} from={beat.from_}].telop", beat.telop)
                )

        for diagram in scene.diagram_specs:
            surfaces.extend(_diagram_label_surfaces(scene.id, "diagram", diagram))
        for beat in scene.beats or []:
            if beat.type == "diagram":
                surfaces.extend(
                    _diagram_label_surfaces(scene.id, f"beats[diagram from={beat.from_}]", beat.diagram)
                )
    return surfaces


def check_suspect_characters(surfaces: list[TextSurface]) -> list[str]:
    """チェック4: telop・図解ラベルに含まれる「フォントで描けない可能性がある文字」を列挙する。"""

    findings: list[str] = []
    for surface in surfaces:
        chars = find_suspect_chars(surface.text)
        if chars:
            chars_desc = " / ".join(f"{ch}（{desc}）" for ch, desc in chars)
            findings.append(f"シーン{surface.scene_id} {surface.location}: 「{surface.text}」— {chars_desc}")
    return findings


def check_label_lengths(surfaces: list[TextSurface]) -> list[str]:
    """チェック5: sketch/narrative のラベルが仕様上限を超えるものを列挙する。

    `validate`（pydantic の `Field(max_length=...)`）が実際には既に弾くため、正常に読み込めた
    YAML では通常ヒットしない。それでも「まとめて見たい」という要望（CLAUDE.md）どおり、
    独立したチェックとして残す。
    """

    findings: list[str] = []
    for surface in surfaces:
        if surface.max_length is not None and len(surface.text) > surface.max_length:
            findings.append(
                f"シーン{surface.scene_id} {surface.location}: {len(surface.text)}字"
                f"（上限{surface.max_length}字）— 「{surface.text}」"
            )
    return findings


# ============================================================
# チェック6: 写真ファイルの存在確認
# ============================================================


def check_asset_files(document: VideoDocument, assets_dir: Path) -> list[str]:
    """`image` ビートの採用素材（`scene_NN_beat{slot}.*`）が `assets_dir` に無いものを列挙する。"""

    findings: list[str] = []
    for scene in document.scenes:
        for beat in scene.beats or []:
            if beat.type != "image":
                continue
            resolved = resolve_beat_asset(assets_dir, scene.id, beat.slot)
            if resolved is None:
                findings.append(
                    f"シーン{scene.id}: scene_{scene.id:02d}_beat{beat.slot}.* が見つかりません"
                    f"（from={beat.from_}）"
                )
    return findings


# ============================================================
# レポート組み立て
# ============================================================


def build_report(
    yaml_path: Path,
    *,
    reading_diffs: list[str] | None,
    long_cues: list[str],
    durations: DurationFindings,
    suspect_chars: list[str],
    label_lengths: list[str],
    asset_findings: list[str] | None,
) -> str:
    lines: list[str] = [f"# Preflight: {yaml_path.name}", ""]

    def section(title: str, findings: list[str] | None, skipped_note: str | None = None) -> None:
        lines.append(f"## {title}")
        if findings is None:
            lines.append(skipped_note or "スキップ")
        elif not findings:
            lines.append("該当なし")
        else:
            lines.extend(f"- {f}" for f in findings)
        lines.append("")

    section("1. 読みの突合（VOICEVOX ⇄ 辞書）", reading_diffs, "スキップ（--skip-tts）")
    section(f"2. 長いキュー（{LONG_CUE_MAX_CHARS}字超）", long_cues)
    section(f"3. 板だけの区間（board が {BOARD_MAX_SECONDS:.0f}秒超）", durations.board_over)
    lines.append(f"### 参考: image/diagram が{IMAGE_DIAGRAM_REFERENCE_MAX_SECONDS:.0f}秒超")
    if durations.image_diagram_over:
        lines.extend(f"- {f}" for f in durations.image_diagram_over)
    else:
        lines.append("該当なし")
    lines.append("")
    section("4. テロップ・図解ラベルの文字（要確認文字）", suspect_chars)
    section("5. ラベル長超過（sketch/narrative）", label_lengths)
    section(
        "6. 写真ファイルの存在確認",
        asset_findings,
        "スキップ（--assets-dir 未指定）",
    )

    total = sum(
        len(x)
        for x in (
            reading_diffs or [],
            long_cues,
            durations.board_over,
            suspect_chars,
            label_lengths,
            asset_findings or [],
        )
    )
    lines.append(f"## まとめ: 検出 {total} 件")
    return "\n".join(lines)


# ============================================================
# selftest（軽量なユニットテスト代わり。tests/ が無いため --selftest で代替）
# ============================================================


def _selftest() -> int:
    failures = 0

    def check(name: str, condition: bool) -> None:
        nonlocal failures
        status = "OK" if condition else "NG"
        if not condition:
            failures += 1
        print(f"[{status}] {name}")

    # 長いキュー検出: split_into_sentences が返す1文の文字数で判定する。
    long_text = "あ" * 51 + "。"
    cues = split_into_sentences(long_text)
    check("長いキュー検出: 51字の1文が50字超と判定される", len(cues) == 1 and len(cues[0]) > LONG_CUE_MAX_CHARS)

    short_text = "あ" * 10 + "。"
    cues2 = split_into_sentences(short_text)
    check("長いキュー検出: 11字の1文は50字超にならない", len(cues2[0]) <= LONG_CUE_MAX_CHARS)

    # ダッシュ検出: en dash / em dash を検出し、通常の日本語記号は誤検出しない。
    found = find_suspect_chars("1983–84年")
    check("ダッシュ検出: en dash を検出する", any(ch == "\u2013" for ch, _ in found))

    found_safe = find_suspect_chars("「本当に？」……そうなのだ〜。")
    check("ダッシュ検出: 通常の日本語記号は誤検出しない", found_safe == [])

    # 既知ノイズ判定
    check("既知ノイズ: ひと/にん は除外される", _is_known_noise("ひと", "にん"))
    check("既知ノイズ以外: 明確な誤読は除外されない", not _is_known_noise("さくぶん", "さくもん"))

    # 数字・英字のマスク（両側とも同じプレースホルダに正規化されるので必ず一致する）
    check("数字マスク: 「2400」は数字プレースホルダに正規化される", _mask_noise_tokens("2400年前") == "スウジ年前")
    check("英字マスク: 「SNS」はローマ字プレースホルダに正規化される", _mask_noise_tokens("SNSでは") == "ローマジでは")

    # 長音記号の展開（fugashi の pron「トーコー」→ VOICEVOX 表記「トオコオ」に揃える）
    check("長音展開: 「トーコー」は「トオコオ」になる（お段）", _expand_chouon("トーコー") == "トオコオ")
    check("長音展開: 「センセー」は「センセエ」になる（え段）", _expand_chouon("センセー") == "センセエ")

    if _FUGASHI_AVAILABLE:
        # fugashi 差し替えのきっかけになった誤読4件（2026-09-06、pykakasi では
        # 力→りき、断った→た、棘→なつめ、優れ→まさ になっていた）が正しく読めることを確認する。
        check("fugashi読み: 「力」はちから", _dict_side_kana_fugashi("力を込めて", None) == "ちからおこめて")
        check("fugashi読み: 「断った」はことわった", _dict_side_kana_fugashi("断った人のほうが", None) == "ことわったひとのほおが")
        check("fugashi読み: 「棘」はとげ", _dict_side_kana_fugashi("棘を抜く", None) == "とげおぬく")
        check("fugashi読み: 「優れ」はすぐれ", _dict_side_kana_fugashi("優れている", None) == "すぐれている")
        # 助詞「は」「を」は fugashi の pron が発音どおり返す（わ／お）。
        check("助詞: 「は」は発音どおり「わ」になる", _dict_side_kana_fugashi("人はもっと少ない", None) == "ひとわもっとすくない")
        check("助詞: 「を」は発音どおり「お」になる", _dict_side_kana_fugashi("投稿を見る", None) == "とおこおおみる")
    else:
        # フォールバック時は pykakasi の一括置換で「は」「を」を発音へ寄せる。
        check("助詞変換（フォールバック）: 「は」は発音どおり「わ」になる", _dict_side_kana_pykakasi("人はもっと少ない", None) == "にんわもっとすくない")
        check("助詞変換（フォールバック）: 「を」は発音どおり「お」になる", _dict_side_kana_pykakasi("投稿を見る", None) == "とうこうおみる")

    return 1 if failures else 0


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="紙芝居モードのシーン YAML をレンダ前に一括検査する（読み・長キュー・板だけ"
        "の区間・要確認文字・ラベル長・素材ファイルの存在）。"
    )
    parser.add_argument("yaml", type=Path, nargs="?", help="シーン YAML ファイルのパス")
    parser.add_argument("--assets-dir", type=Path, default=None, help="採用素材ディレクトリ（チェック6用）")
    parser.add_argument("--out", type=Path, default=None, help="Markdown レポートの保存先（省略時は標準出力のみ）")
    parser.add_argument("--skip-tts", action="store_true", help="チェック1（VOICEVOX突合）を飛ばす")
    parser.add_argument(
        "--voicevox-url", default=DEFAULT_BASE_URL, help=f"VOICEVOX ENGINE の base URL（既定: {DEFAULT_BASE_URL}）"
    )
    parser.add_argument("--selftest", action="store_true", help="軽量な自己テストを実行して終了する")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    if args.yaml is None:
        parser.error("yaml パスが必要です（--selftest 以外）")

    result = load_scene_yaml(args.yaml)
    if not result.ok or result.document is None:
        for message in result.errors:
            print(f"エラー: {message}", file=sys.stderr)
        return 1
    document = result.document

    reading_diffs = None if args.skip_tts else check_reading_diffs(document, args.voicevox_url)
    long_cues = check_long_cues(document)
    durations = check_beat_durations(document)
    surfaces = collect_text_surfaces(document)
    suspect_chars = check_suspect_characters(surfaces)
    label_lengths = check_label_lengths(surfaces)
    asset_findings = None if args.assets_dir is None else check_asset_files(document, args.assets_dir)

    report = build_report(
        args.yaml,
        reading_diffs=reading_diffs,
        long_cues=long_cues,
        durations=durations,
        suspect_chars=suspect_chars,
        label_lengths=label_lengths,
        asset_findings=asset_findings,
    )
    print(report)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report + "\n", encoding="utf-8")

    has_findings = any(
        [
            reading_diffs,
            long_cues,
            durations.board_over,
            suspect_chars,
            label_lengths,
            asset_findings,
        ]
    )
    return 1 if has_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
