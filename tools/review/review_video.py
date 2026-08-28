"""レンダ済み動画（script-to-video 出力）を、ビート単位の静止画＋ナレーション＋テロップで
別モデル（GPT。Codex CLI 経由）にレビューさせるツール。

draft-explanation-video の台本執筆フローに「別モデルによる自動レビュー」を組み込む一環
（2026-08-27）。台本レビュー（review_script.py）に続く②映像レビュー。加えて **決定論的な
事前チェック**（ナレーションにない文字がテロップに出ていないか等）を GPT を呼ばずに行う。

**台本・YAML の文言はこのツールでは一切編集しない**（指摘の生成のみ）。採否判断と反映は
人／Claude が行う。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_video.py ^
        scripts/20260827-cynicism/20260827-cynicism.yaml ^
        C:/Users/shuya/Projects/script-to-video/build/cynicism-v1-codex ^
        --timings-dir C:/Users/shuya/Projects/script-to-video/build/cynicism-audio ^
        --mp4 C:/Users/shuya/Projects/script-to-video/build/cynicism-v1-codex/cynicism-v1-codex.mp4 ^
        --scenes 1,3

`--skip-gpt` を付けると静止画抽出と決定論チェックだけを行う（GPT 呼び出しなし）。

## 前提

- script-to-video のライブラリ（`src/script_to_video`）を import する。このスクリプトを
  script-to-video の venv python で実行すること。
- ffmpeg（既定: winget インストール先にフォールバック）。
- Codex CLI にログイン済みであること（`--skip-gpt` を使わない場合）。1回の呼び出しに
  1〜3分程度。「usage limit」「at capacity」等で失敗した場合は60秒待って1回だけ再試行する。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

STV_ROOT = Path(r"C:\Users\shuya\Projects\script-to-video")
sys.path.insert(0, str(STV_ROOT / "src"))

from script_to_video.beats import beat_windows  # noqa: E402
from script_to_video.loader import load_scene_yaml  # noqa: E402
from script_to_video.render import build_scene_srt_cues, resolve_ffmpeg_path  # noqa: E402
from script_to_video.schema import Scene  # noqa: E402
from script_to_video.tts import SceneTiming  # noqa: E402

# ============================================================
# 定数
# ============================================================

WINGET_CODEX_FALLBACK = (
    Path.home()
    / "AppData"
    / "Local"
    / "Microsoft"
    / "WinGet"
    / "Packages"
    / "OpenAI.Codex_Microsoft.Winget.Source_8wekyb3d8bbwe"
    / "codex.bat"
)

DEFAULT_TIMEOUT_S = 900.0
DEFAULT_PER_CALL = 6
RATE_LIMIT_PATTERNS = (
    "rate limit",
    "rate_limit",
    "quota",
    "usage limit",
    "at capacity",
    "try again later",
    "too many requests",
    "429",
)
RATE_LIMIT_WAIT_S = 60.0
MAX_RATE_LIMIT_RETRIES = 1
TAIL_MAX_CHARS = 2000

STILL_WIDTH = 960
LONG_IMAGE_BEAT_SECONDS = 20.0
REPEAT_TELOP_WINDOW_SECONDS = 10.0

CHAPTER_MID_OFFSET = 1.5
"""chapter ビートの静止画抽出時刻: 窓の開始 + この秒数（CLAUDE.md の指定どおり）。"""

DIAGRAM_MID_OFFSET_FROM_END = 1.0
"""diagram ビートの静止画抽出時刻: 窓の終了 - この秒数。"""

CITATION_RE = re.compile(
    r"\(\d{4}\)|（\d{4}）|\d{4}年|et al\.|『[^』]*』|"
    r"[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+"
)
"""テロップが出典表記らしいと判定する簡易パターン（年の括弧・et al.・『』・英語の固有名詞列）。"""

NUMBER_UNIT_RE = re.compile(
    r"\d+(?:\.\d+)?\s*(?:%|パーセント|人|件|カ国|か国|カ月|ヶ月|年|倍|万|億)"
)
"""テロップが数値＋単位の提示らしいと判定する簡易パターン。"""

ENGLISH_TEXT_RE = re.compile(r"[A-Za-z]{2,}")
"""テロップに研究名・書名・原語など英字（固有名詞）が含まれるかの簡易パターン（2文字以上の連続）。"""

SECTION_MARKER_RE = re.compile(r"[：／]")
"""テロップが「見出し：本体」「A／B」のような章の区切り表現かの簡易パターン。"""

GPT_OBSERVATION_POINTS = (
    "①ナレーション・出典以外の読める文字が画に写っている\n"
    "②顔のクローズアップ・正面の顔\n"
    "③画とナレーションの不一致（ナレーションで述べた物・人物・場面が描かれていない）\n"
    "④二者比較や before/after が一枚に描かれている\n"
    "⑤字幕・テロップのはみ出し・重なり・行数過多\n"
    "⑥画風の不統一（時代・光の温度が場面と合わない）\n"
    "⑦意図しない含意（特定の人物・団体・性別・人種を連想させる等）"
)

# 指摘の粒度（2026-08-28 ユーザー指示: 画像は細かいレビューをせず、大きい視点で間違っている場合だけ指摘する）
GPT_SCOPE_RULES = (
    "【指摘の粒度】画像については「大きい視点で間違っている」場合だけ指摘してください。"
    "視聴者が一目見て「ナレーションと別の話をしている」「時代や場所が明らかに違う」「読める偽の文字が目立つ」"
    "「正面の顔が大きく写っている」「誤解を招く含意がはっきりある」と感じるレベルが対象です。\n"
    "次のような細部は報告しないでください: 生成プロンプトとの逐語的な差（小物の有無、人数や姿勢・視線の違い、"
    "服装の色）、構図や照明のわずかな差、遠景に小さく写る程度の要素、字幕・テロップの軽微な体裁、"
    "「〜の方が望ましい」程度の改善提案。迷ったら報告しない側に倒してください。"
    "一方、⑤（字幕・テロップの物理的な崩れ）は細かくても報告して構いません。"
)


class ReviewVideoError(RuntimeError):
    """レビュー実行に失敗したときのエラー。"""


# ============================================================
# codex exe の解決・呼び出し（review_script.py と同方式）
# ============================================================


def resolve_codex_exe(explicit: str | None) -> str:
    if explicit:
        return explicit
    which = shutil.which("codex") or shutil.which("codex.bat")
    if which:
        return which
    if WINGET_CODEX_FALLBACK.exists():
        return str(WINGET_CODEX_FALLBACK)
    raise ReviewVideoError(
        "codex 実行ファイルが見つかりません。PATH に codex を通すか --codex-path で指定してください。"
    )


def _detect_rate_limit(text: str) -> str | None:
    lowered = text.lower()
    for pattern in RATE_LIMIT_PATTERNS:
        if pattern in lowered:
            return pattern
    return None


def _tail(text: str, max_chars: int = TAIL_MAX_CHARS) -> str:
    text = text.strip()
    return text[-max_chars:] if len(text) > max_chars else text


def _run_codex_once(
    codex_exe: str, prompt_text: str, image_paths: list[Path], *, timeout: float, cwd: Path
) -> str:
    out_file = cwd / "response.md"
    cmd = [codex_exe, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(cwd)]
    for image_path in image_paths:
        cmd += ["-i", str(Path(image_path).resolve())]  # codex は -C の一時 dir で動くので絶対パスに
    cmd += ["-o", str(out_file), "-"]

    try:
        result = subprocess.run(
            cmd,
            input=prompt_text,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise ReviewVideoError(f"codex exec がタイムアウトしました（{timeout:.0f}秒）") from exc

    combined = f"{result.stdout or ''}\n{result.stderr or ''}"
    rate_limit = _detect_rate_limit(combined)

    if result.returncode != 0:
        if rate_limit:
            raise ReviewVideoError(f"__RATE_LIMIT__:{rate_limit}")
        raise ReviewVideoError(
            f"codex exec が失敗しました（終了コード {result.returncode}）。出力末尾:\n{_tail(combined)}"
        )
    if not out_file.exists():
        if rate_limit:
            raise ReviewVideoError(f"__RATE_LIMIT__:{rate_limit}")
        raise ReviewVideoError(
            f"codex exec の最終応答ファイルが生成されませんでした。出力末尾:\n{_tail(combined)}"
        )
    return out_file.read_text(encoding="utf-8").strip()


def run_codex_review(
    prompt_text: str, image_paths: list[Path], *, codex_exe: str, timeout: float
) -> str:
    attempt = 0
    while True:
        attempt += 1
        with tempfile.TemporaryDirectory(prefix="review_video_") as tmp:
            try:
                return _run_codex_once(codex_exe, prompt_text, image_paths, timeout=timeout, cwd=Path(tmp))
            except ReviewVideoError as exc:
                message = str(exc)
                if message.startswith("__RATE_LIMIT__") and attempt <= MAX_RATE_LIMIT_RETRIES:
                    pattern = message.split(":", 1)[1]
                    print(
                        f"    レート制限/クォータ超過を検知しました（文言: \"{pattern}\"）。"
                        f"{RATE_LIMIT_WAIT_S:.0f}秒待って再試行します",
                        file=sys.stderr,
                    )
                    time.sleep(RATE_LIMIT_WAIT_S)
                    continue
                if message.startswith("__RATE_LIMIT__"):
                    raise ReviewVideoError("レート制限/クォータ超過のため断念しました（1回再試行済み）") from exc
                raise


# ============================================================
# ビート単位の情報収集
# ============================================================


@dataclass
class BeatRecord:
    scene_id: int
    beat_num: int  # 1始まり
    beat_type: str
    start: float  # シーン内相対秒
    end: float
    abs_time: float  # 動画全体での抽出時刻（秒）
    narration: str
    telop: str | None
    chapter_title: str | None
    visual_intent: str | None
    gen_prompt: str | None
    cut_reason: str
    still_path: Path | None = None
    still_error: str | None = None


def load_timeline_scene_starts(out_dir: Path) -> dict[int, float]:
    timeline_path = out_dir / "timeline.json"
    if not timeline_path.is_file():
        raise ReviewVideoError(f"timeline.json が見つかりません: {timeline_path}")
    data = json.loads(timeline_path.read_text(encoding="utf-8"))
    starts: dict[int, float] = {}
    for entry in data.get("entries", []):
        if entry.get("kind") == "scene":
            starts[entry["scene_id"]] = entry["start"]
    return starts


def load_scene_timing(timings_dir: Path, scene_id: int) -> SceneTiming | None:
    path = timings_dir / f"scene_{scene_id:02d}.timing.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return SceneTiming.from_dict(data)


def _clip_mid(beat_type: str, start: float, end: float) -> float:
    """静止画を抽出する時刻（シーン内相対秒）。CLAUDE.md の指定どおり chapter/diagram は
    ビート中間時刻ではなくオフセット付きにする。どの場合も [start, end) の内側に収める。"""

    duration = max(end - start, 0.0)
    if duration <= 0:
        return start

    if beat_type == "chapter":
        mid = start + CHAPTER_MID_OFFSET
    elif beat_type == "diagram":
        mid = end - DIAGRAM_MID_OFFSET_FROM_END
    else:
        mid = (start + end) / 2

    margin = min(0.1, duration / 2)
    lo, hi = start + margin, end - margin
    if lo > hi:
        return (start + end) / 2
    return min(max(mid, lo), hi)


def collect_beat_records(
    scene: Scene, timing: SceneTiming, scene_abs_start: float
) -> list[BeatRecord]:
    """1シーン分のビートレコードを組み立てる（静止画抽出前。narration はキュー本文の結合）。"""

    beats = scene.beats or []
    if not beats:
        return []

    windows = beat_windows(scene, timing)
    cues = build_scene_srt_cues(timing)

    records: list[BeatRecord] = []
    for i, (beat, (start, end)) in enumerate(zip(beats, windows)):
        narration_text = "".join(cue.text for cue in cues if start <= cue.start < end)
        mid = _clip_mid(beat.type, start, end)
        record = BeatRecord(
            scene_id=scene.id,
            beat_num=i + 1,
            beat_type=beat.type,
            start=start,
            end=end,
            abs_time=scene_abs_start + mid,
            narration=narration_text,
            telop=getattr(beat, "telop", None),
            chapter_title=scene.chapter_title if beat.type == "chapter" else None,
            visual_intent=getattr(beat, "visual_intent", None),
            gen_prompt=getattr(beat, "gen_prompt", None),
            cut_reason=beat.cut_reason,
        )
        records.append(record)
    return records


# ============================================================
# 静止画抽出（ffmpeg）
# ============================================================


def extract_still(ffmpeg_exe: str, mp4_path: Path, abs_time: float, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss",
        f"{max(abs_time, 0.0):.3f}",
        "-i",
        str(mp4_path),
        "-frames:v",
        "1",
        "-vf",
        f"scale={STILL_WIDTH}:-1",
        "-q:v",
        "3",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0 or not out_path.is_file():
        raise ReviewVideoError(f"ffmpeg での静止画抽出に失敗しました: {_tail(result.stderr)}")


# ============================================================
# 決定論チェック
# ============================================================


def run_deterministic_checks(
    scenes_with_records: list[tuple[Scene, list[BeatRecord]]]
) -> list[str]:
    """テロップを2区分でチェックし、加えて「同一telopの10秒以内再出現」「20秒超のimageビート」を
    検出する。

    - **区分A「ナレーションにない文字」**（捏造検出）: telop がそのシーンのナレーション本文に
      含まれず、出典表記パターン（年の括弧・et al.・『』・英語の固有名詞列）にも数値＋単位
      パターンにも該当しない場合。telop が「読み上げていない・出典でも数値でもない」独自の
      文言になっている＝捏造・誤情報のリスクがあるため、原則対応が必要な指摘として扱う。
    - **区分B「字幕の写し」**（要判断）: telop がナレーション本文の一部と一致し、かつ数値・
      英字の固有名詞・章の区切り記号（「：」「／」）のいずれも含まない場合。ナレーション（字幕）
      と同じ日本語文をそのまま別枠で大きく出しているだけ＝情報として無駄になっている疑い。
      ただし問いの強調表示など意図的なケースもあるため、問題として断定せず「要判断」として
      列挙するだけにする（例: v1 の YAML シーン3の telop「人間を探している」はナレーションの
      引用と完全一致するため区分Bに列挙される）。

    戻り値は Markdown 表の行文字列のリスト（見出し行を含まない）。
    """

    rows: list[str] = []

    for scene, records in scenes_with_records:
        full_narration = "".join(segment.text for segment in scene.narration)

        for r in records:
            if r.beat_type not in ("image", "diagram"):
                continue
            telop = (r.telop or "").strip()
            if not telop:
                continue

            if telop not in full_narration:
                if CITATION_RE.search(telop) or NUMBER_UNIT_RE.search(telop):
                    continue
                rows.append(
                    f"| {scene.id} | {r.beat_num}（{r.beat_type}） | 区分A: ナレーションにない文字 | "
                    f"telop=「{telop}」がシーンのナレーション本文に見当たらず、出典表記／数値でもない |"
                )
                continue

            # ここから telop はナレーション本文に含まれる（捏造ではない）。
            if NUMBER_UNIT_RE.search(telop) or ENGLISH_TEXT_RE.search(telop) or SECTION_MARKER_RE.search(telop):
                continue
            rows.append(
                f"| {scene.id} | {r.beat_num}（{r.beat_type}） | 区分B: 字幕の写し（要判断） | "
                f"telop=「{telop}」はナレーションと同じ日本語文をそのまま表示しているだけの可能性 |"
            )

        for r in records:
            if r.beat_type == "image" and (r.end - r.start) > LONG_IMAGE_BEAT_SECONDS:
                rows.append(
                    f"| {scene.id} | {r.beat_num}（{r.beat_type}） | 20秒超のimageビート | "
                    f"一枚絵の保持が {r.end - r.start:.1f} 秒（目安8〜15秒・20秒超は警告） |"
                )

    # 同一telopの10秒以内再出現は動画全体（シーンをまたぐ）で見る。
    telop_occurrences: list[tuple[str, int, int, float]] = []
    for scene, records in scenes_with_records:
        for r in records:
            telop = (r.telop or "").strip()
            if telop:
                telop_occurrences.append((telop, scene.id, r.beat_num, r.abs_time))
    telop_occurrences.sort(key=lambda item: item[3])
    for i in range(len(telop_occurrences) - 1):
        text_a, scene_a, beat_a, time_a = telop_occurrences[i]
        for j in range(i + 1, len(telop_occurrences)):
            text_b, scene_b, beat_b, time_b = telop_occurrences[j]
            if time_b - time_a > REPEAT_TELOP_WINDOW_SECONDS:
                break
            if text_a == text_b:
                rows.append(
                    f"| {scene_a}/{scene_b} | {beat_a}/{beat_b} | 同一telopの10秒以内再出現 | "
                    f"「{text_a}」が {time_b - time_a:.1f} 秒差で再出現 |"
                )

    return rows


# ============================================================
# GPT 画像レビュー
# ============================================================


def build_gpt_prompt(batch: list[BeatRecord]) -> str:
    lines = [
        "あなたは解説動画（YouTube、機械音声ナレーション）の映像レビュアーです。"
        "以下は、動画の各ビート（画面が切り替わる単位）の静止画です。画像は入力順に画像1、画像2…と"
        "番号を振ってあります。各画像に対応する情報を示します。",
        "",
        "次の観点でチェックしてください。",
        GPT_OBSERVATION_POINTS,
        "",
        GPT_SCOPE_RULES,
        "",
        "出力は日本語で、Markdown の表（画像／問題種別／説明／推奨）にしてください。"
        "問題なしの画像は表に出さず省略してください。指摘が一つもなければ「指摘なし」とだけ書いてください。"
        "動画・台本のファイルは編集しないでください。",
        "",
        "---",
        "",
    ]
    for i, r in enumerate(batch, start=1):
        info = [f"### 画像{i}（シーン{r.scene_id} ビート{r.beat_num}・{r.beat_type}）"]
        if r.narration:
            info.append(f"- ナレーション: {r.narration}")
        if r.telop:
            info.append(f"- テロップ: {r.telop}")
        if r.chapter_title:
            info.append(f"- 章タイトル: {r.chapter_title}")
        if r.visual_intent:
            info.append(f"- ビジュアル意図: {r.visual_intent}")
        if r.gen_prompt:
            info.append(f"- 生成プロンプト: {r.gen_prompt}")
        lines.append("\n".join(info))
        lines.append("")
    return "\n".join(lines)


def run_gpt_review(
    records: list[BeatRecord], *, codex_exe: str, per_call: int, timeout: float
) -> tuple[list[str], list[str]]:
    """GPT 画像レビューを --per-call 枚ずつのバッチで実行する。

    戻り値: (成功したバッチの応答テキストのリスト, 失敗したバッチの説明メッセージのリスト)。
    """

    reviewable = [r for r in records if r.still_path is not None]
    responses: list[str] = []
    failures: list[str] = []

    for start in range(0, len(reviewable), per_call):
        batch = reviewable[start : start + per_call]
        image_paths = [r.still_path for r in batch if r.still_path is not None]
        labels = ", ".join(f"s{r.scene_id:02d}_b{r.beat_num:02d}" for r in batch)
        print(f"  GPT画像レビュー呼び出し: {labels}（{len(batch)}枚）")
        prompt = build_gpt_prompt(batch)
        try:
            response = run_codex_review(prompt, image_paths, codex_exe=codex_exe, timeout=timeout)
            header = f"### バッチ: {labels}\n\n"
            responses.append(header + response)
        except ReviewVideoError as exc:
            print(f"    失敗: {exc}", file=sys.stderr)
            failures.append(f"未レビュー: {labels}（理由: {exc}）")

    return responses, failures


# ============================================================
# メイン処理
# ============================================================


def find_default_mp4(out_dir: Path) -> Path:
    candidates = sorted(out_dir.glob("*.mp4"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ReviewVideoError(f"*.mp4 が見つかりません: {out_dir}")
    listed = ", ".join(p.name for p in candidates)
    raise ReviewVideoError(f"*.mp4 が複数見つかりました（--mp4 で明示してください）: {listed}")


def find_default_timings_dir(out_dir: Path) -> Path:
    candidate = out_dir / "audio"
    if candidate.is_dir():
        return candidate
    raise ReviewVideoError(
        f"既定の timings ディレクトリ（{candidate}）が見つかりません。--timings-dir で指定してください。"
    )


def parse_scene_filter(raw: str | None) -> set[int] | None:
    if not raw:
        return None
    return {int(x.strip()) for x in raw.split(",") if x.strip()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="レンダ済み動画をビート単位でGPTレビューする")
    parser.add_argument("yaml_path", help="シーン YAML のパス")
    parser.add_argument("out_dir", help="レンダ出力ディレクトリ（timeline.json 等がある場所）")
    parser.add_argument("--timings-dir", default=None, help="scene_XX.timing.json の場所（既定: out_dir/audio）")
    parser.add_argument("--mp4", default=None, help="完成 MP4 のパス（既定: out_dir 直下の唯一の *.mp4）")
    parser.add_argument("--scenes", default=None, help="対象シーン番号（カンマ区切り。例: 1,3）省略時は全シーン")
    parser.add_argument("--per-call", type=int, default=DEFAULT_PER_CALL, help=f"1回のcodex呼び出しに載せる画像数（既定 {DEFAULT_PER_CALL}）")
    parser.add_argument("--skip-gpt", action="store_true", help="決定論チェックと静止画抽出だけ行い、GPTレビューは呼ばない")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help=f"codex exec 1回あたりのタイムアウト秒（既定 {DEFAULT_TIMEOUT_S:.0f}）")
    parser.add_argument("--ffmpeg-path", default=None, help="ffmpeg 実行ファイルのパス（既定: 自動検出）")
    parser.add_argument("--codex-path", default=None, help="codex 実行ファイルのパス（既定: 自動検出）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    yaml_path = Path(args.yaml_path)
    out_dir = Path(args.out_dir)

    result = load_scene_yaml(yaml_path)
    if not result.ok or result.document is None:
        print("YAML の読み込みに失敗しました:", file=sys.stderr)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    document = result.document

    try:
        timings_dir = Path(args.timings_dir) if args.timings_dir else find_default_timings_dir(out_dir)
        mp4_path = Path(args.mp4) if args.mp4 else find_default_mp4(out_dir)
        scene_starts = load_timeline_scene_starts(out_dir)
        ffmpeg_exe = resolve_ffmpeg_path(args.ffmpeg_path)
    except ReviewVideoError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    scene_filter = parse_scene_filter(args.scenes)
    scenes = [s for s in document.scenes if scene_filter is None or s.id in scene_filter]
    if not scenes:
        print("対象シーンがありません（--scenes の指定を確認してください）", file=sys.stderr)
        return 2

    review_dir = out_dir / "review"
    stills_dir = review_dir / "stills"

    scenes_with_records: list[tuple[Scene, list[BeatRecord]]] = []
    skipped_scenes: list[str] = []

    for scene in scenes:
        timing = load_scene_timing(timings_dir, scene.id)
        if timing is None:
            skipped_scenes.append(f"シーン{scene.id}: timing json が見つかりません（{timings_dir}）")
            continue
        if scene.id not in scene_starts:
            skipped_scenes.append(f"シーン{scene.id}: timeline.json に見つかりません")
            continue
        if not scene.beats:
            skipped_scenes.append(f"シーン{scene.id}: beats未使用（v5互換）のためスキップ")
            continue

        records = collect_beat_records(scene, timing, scene_starts[scene.id])
        for r in records:
            still_path = stills_dir / f"s{scene.id:02d}_b{r.beat_num:02d}_{r.beat_type}.jpg"
            try:
                extract_still(ffmpeg_exe, mp4_path, r.abs_time, still_path)
                r.still_path = still_path
            except ReviewVideoError as exc:
                r.still_error = str(exc)
        scenes_with_records.append((scene, records))

    total_beats = sum(len(records) for _, records in scenes_with_records)
    total_stills = sum(1 for _, records in scenes_with_records for r in records if r.still_path)
    print(f"静止画抽出: {total_stills}/{total_beats} 枚（{stills_dir}）")
    if skipped_scenes:
        for msg in skipped_scenes:
            print(f"  skip: {msg}")

    deterministic_rows = run_deterministic_checks(scenes_with_records)

    gpt_responses: list[str] = []
    gpt_failures: list[str] = []
    if not args.skip_gpt:
        all_records = [r for _, records in scenes_with_records for r in records]
        try:
            codex_exe = resolve_codex_exe(args.codex_path)
        except ReviewVideoError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        start_time = time.time()
        gpt_responses, gpt_failures = run_gpt_review(
            all_records, codex_exe=codex_exe, per_call=args.per_call, timeout=args.timeout
        )
        print(f"GPT画像レビュー所要: {time.time() - start_time:.0f}秒")

    review_dir.mkdir(parents=True, exist_ok=True)
    out_md = review_dir / "video-review.md"
    out_md.write_text(
        build_video_review_markdown(
            yaml_path=yaml_path,
            out_dir=out_dir,
            mp4_path=mp4_path,
            deterministic_rows=deterministic_rows,
            gpt_responses=gpt_responses,
            gpt_failures=gpt_failures,
            skipped_scenes=skipped_scenes,
            skipped_gpt=args.skip_gpt,
        ),
        encoding="utf-8",
    )
    print(f"保存しました: {out_md}")
    return 0


def build_video_review_markdown(
    *,
    yaml_path: Path,
    out_dir: Path,
    mp4_path: Path,
    deterministic_rows: list[str],
    gpt_responses: list[str],
    gpt_failures: list[str],
    skipped_scenes: list[str],
    skipped_gpt: bool,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [
        "# GPT（Codex CLI 経由）による映像レビュー\n",
        f"- 日時: {now}",
        f"- YAML: {yaml_path}",
        f"- レンダ出力: {out_dir}",
        f"- MP4: {mp4_path}",
        "",
    ]
    if skipped_scenes:
        parts.append("## スキップしたシーン\n")
        for msg in skipped_scenes:
            parts.append(f"- {msg}")
        parts.append("")

    parts.append("## 決定論チェック\n")
    parts.append(
        "テロップを区分A「ナレーションにない文字」（捏造検出。要対応）と区分B「字幕の写し」"
        "（ナレーションと同じ日本語文をそのまま表示しているだけの疑い。要判断）に分けて検出。"
        "加えて「同一telopの10秒以内再出現」「20秒超のimageビート」を検出。"
    )
    parts.append("")
    if deterministic_rows:
        parts.append("| シーン | ビート | 問題種別 | 説明 |")
        parts.append("|---|---|---|---|")
        parts.extend(deterministic_rows)
    else:
        parts.append("該当なし。")
    parts.append("")

    parts.append("## GPT 画像レビュー\n")
    if skipped_gpt:
        parts.append("`--skip-gpt` のため未実行。")
    elif not gpt_responses and not gpt_failures:
        parts.append("対象ビートがありませんでした。")
    else:
        for response in gpt_responses:
            parts.append(response)
            parts.append("")
        if gpt_failures:
            parts.append("### 未レビュー\n")
            for msg in gpt_failures:
                parts.append(f"- {msg}")
            parts.append("")

    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
