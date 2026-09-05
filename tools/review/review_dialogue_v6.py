"""対話台本（めたん・ずんだもん紙芝居版）のセリフを、別モデル（GPT。Codex CLI 経由）に
「セリフとして自然か・キャラらしいか・表情タグが合っているか・読点の位置」の観点で
レビューさせるツール。

**一時的な作業用コピー**（2026-09-05）。`review_dialogue.py` に観点6「読点の位置
（TTSで不自然な間になる読点・不要な読点・不足）」を追加しただけの版。元の
`review_dialogue.py` は変更しない。20260904-dopagaki-kamishibai 台本のレビューに
ユーザーが追加で指定した観点（違和感・分かりやすさ・面白さに加えて読点）に対応する
ためのもの。

`review_holistic.py`（面白さ・視聴維持等の総合レビュー）を雛形にした対話特化版
（2026-09-04）。ユーザー指摘: 「元の台本を継承しすぎて、ずんだもんやめたんのセリフっぽく
ないところが多い」への対応。**台本の文言はこのツールでは一切編集しない**（指摘の生成のみ）。
採否判断と反映は人／Claude が行う。

codex exec の呼び出し方式（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、
`-o` で応答ファイル出力、クォータ超過時60秒待ち1回リトライ）は `review_script.py` の実装を
そのまま import して再利用する。

## 対象とする台本の書式

対話台本は `## シーンN: タイトル` でシーンを区切り、各シーンは 1 行 1 発話
`**話者**（表情）: 本文` が並ぶ（表情省略行は今のところ存在しない前提。あれば直前の
表情を引き継ぐ想定だが、このツールでは表情列に「(直前を維持)」とだけ入れて渡す）。
続く `**画面**` セクション（`- テロップ: ...` 等の箇条書き）は `**話者**（表情）: ` の
形と一致しないため、抽出時に自然に除外される。`## 出典リスト` 以降は対象外。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_dialogue_v6.py scripts/20260904-dopagaki-kamishibai/20260904-dopagaki-kamishibai.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-dialogue-review.md`
（`review_dialogue.py` と同じ既定パス）。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- セリフ全文＋観点6つ（自然さ・キャラらしさ・テンポ・表情タグ・面白さ・読点）を渡すため
  出力が長くなりやすい。「usage limit」「at capacity」等のクォータ超過で失敗することが
  あり、その場合は60秒待って1回だけ再試行する。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# review_script.py と同じディレクトリにあるため、そのまま import して再利用する
# （codex exe 解決・レート制限リトライ付き codex exec 呼び出し）。
from review_script import (
    DEFAULT_TIMEOUT_S,
    ReviewScriptError,
    resolve_codex_exe,
    run_codex_review,
)

# ============================================================
# 定数
# ============================================================

TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
SCENE_HEADING_RE = re.compile(r"^## (シーン\d+.*)$", re.MULTILINE)
SOURCE_LIST_MARKER_RE = re.compile(r"^## 出典リスト", re.MULTILINE)

# `**ずんだもん**（confused）: 本文` / `**めたん**（explain）: 本文` の1発話1行。
# 「**画面**」セクションの箇条書き（`- テロップ: ...` 等）はこの形に一致しないため
# 自然に除外される。
DIALOGUE_LINE_RE = re.compile(
    r"^\*\*(ずんだもん|めたん)\*\*（([^）]+)）:\s*(.+)$", re.MULTILINE
)

# 決め文の保持時間メモ「（間 2.0）」はセリフ本文ではなく演出メモなので、抽出時に取り除く。
PAUSE_NOTE_RE = re.compile(r"（間\s*[\d.]+）\s*$")

ZUNDAMON_EXPRESSIONS = (
    "normal / smile / delighted / surprised / confused / thinking / angry / "
    "sad / sleepy / shy / smug / point / whisper"
)
METAN_EXPRESSIONS = (
    "normal / explain（指差し・口開き） / point（指差し・口閉じ） / serious（引き締めた顔） / "
    "smile / delighted / surprised / confused / thinking / angry / sad / sleepy / shy / smug / whisper"
)

CHARACTER_PROFILE = (
    "- **ずんだもん**（聞き手）: 語尾は「〜のだ」「〜なのだ」。無邪気・素直・時々ボケる。"
    "自分自身を「ドパガキ」だと思っている当事者として、疑問・驚き・言い換え・ツッコミで"
    "掛け合いの節目を作る。\n"
    "- **四国めたん**（解説役）: 落ち着いた丁寧語に少しお嬢様の余裕（「〜のよ」「〜かしら」。"
    "「〜ですわ」は多用しない）。ずんだもんに向かって話しかける口調で、講義調にはならない。"
)

OBSERVATION_POINTS = (
    "1. **セリフの自然さ**: 地の文・書き言葉・説明文の残骸（例:「〜なの。」で終わる長い複文、"
    "名詞の羅列、論文的な言い回し、一人語りの「〜だ。」調が残っている行）を指摘し、"
    "**口から出る言葉としての言い直し案**を示してください。事実・数値・固有名詞は変えないこと。\n"
    "2. **キャラらしさ**: 上記のキャラクター設定から外れている行（ずんだもんが当事者性を"
    "失っている、めたんが講義調になっている等）、逆に語尾（「〜のだ」「〜のよ」）が機械的に"
    "付いているだけで中身がキャラらしくない行を指摘してください。\n"
    "3. **掛け合いのテンポ**: めたんの独白が長く続いてずんだもんが相づちマシンになっている"
    "箇所、同じ受け方（例:「〜なのだ？」で聞き返すだけ）が続く箇所、ずんだもんに言わせた方が"
    "面白くなる説明を指摘してください。\n"
    "4. **表情タグの妥当性**: 各行の（表情）がセリフの感情と合っているか判定し、合わない行には"
    "代替の表情名を提案してください。使える表情名は次の通り（この一覧以外は使わないこと）。\n"
    f"   - ずんだもん: {ZUNDAMON_EXPRESSIONS}\n"
    f"   - めたん: {METAN_EXPRESSIONS}\n"
    "5. **面白さ**: 笑いどころ・可愛げが足りない箇所に、キャラを壊さない範囲での一言の提案を"
    "3〜5箇所出してください。\n"
    "6. **読点の位置**: この台本は機械音声（TTS）で読み上げられます。読点「、」がTTSで"
    "不自然な間になる箇所（例: 主語と述語の間に不要な読点が入っている、修飾語の直後で"
    "不要に切れる）、逆に長い一文で読点が不足して息継ぎ・意味の区切りが分かりにくい箇所を"
    "指摘し、読点の追加・削除・移動の具体案を示してください。"
)

PROMPT_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画のセリフレビュアーです。対象は「{title}」。四国めたん"
    "（VOICEVOX、解説役）とずんだもん（VOICEVOX、聞き手）の二人による対話劇で、絵は紙芝居風"
    "（緑の黒板・木枠の額縁・棒付きの紙人形）です。視聴者は一般層で、専門知識は仮定しません。"
    "セリフは機械音声（TTS）でそのまま読み上げられます。\n\n"
    "この台本は、元は一人語りの解説台本だったものを、二人の対話に組み替えたものです。"
    "そのため「元の台本を継承しすぎて、ずんだもんやめたんのセリフっぽくない」行が"
    "残っている疑いがあります。以下のキャラクター設定を踏まえて、セリフごとに"
    "レビューしてください。\n\n"
    "## キャラクター設定\n"
    f"{CHARACTER_PROFILE}\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "Markdown の表で出力してください。列は「シーン／行／話者／種別（1〜6）／該当セリフ"
    "（短く引用）／指摘／言い直し案（表情変更案・読点の直し方を含む）」としてください。"
    "指摘は多くてよく、全行を対象に、該当するものは漏らさず挙げてください（表を複数の観点で"
    "分けても構いません）。行番号は各シーン内の通し番号（下記の入力に付けた番号）を使って"
    "ください。\n\n"
    "表の後に、次の2つを追加してください。\n"
    "- 「## シーン別の総評」: 各シーン2〜3行\n"
    "- 「## 全体で最優先で直すべき5点」: 5件、優先度をつけて\n\n"
    "台本の書き換えはせず、指摘と言い直し案の提示のみを行ってください。ファイルは編集しない"
    "でください。"
)


# ============================================================
# 台本 md からシーン・発話抽出
# ============================================================


def extract_title(md_text: str, fallback: str) -> str:
    match = TITLE_RE.search(md_text)
    return match.group(1).strip() if match else fallback


def extract_scenes_with_lines(
    md_text: str,
) -> list[tuple[str, list[tuple[int, str, str, str]]]]:
    """シーン見出しごとに (シーンタイトル, [(シーン内通し番号, 話者, 表情, セリフ本文), ...]) を抽出する。

    `## 出典リスト` 以降は除外する。`**画面**` セクションの箇条書きは DIALOGUE_LINE_RE に
    一致しないため、明示的な除外処理なしで自然に除かれる。
    """

    source_match = SOURCE_LIST_MARKER_RE.search(md_text)
    body = md_text[: source_match.start()] if source_match else md_text

    headings = list(SCENE_HEADING_RE.finditer(body))
    scenes: list[tuple[str, list[tuple[int, str, str, str]]]] = []
    for i, m in enumerate(headings):
        title = m.group(1).strip()
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section = body[start:end]

        lines: list[tuple[int, str, str, str]] = []
        for line_no, dm in enumerate(DIALOGUE_LINE_RE.finditer(section), start=1):
            speaker, expression, text = dm.group(1), dm.group(2), dm.group(3).strip()
            text = PAUSE_NOTE_RE.sub("", text).strip()
            lines.append((line_no, speaker, expression, text))

        if lines:
            scenes.append((title, lines))
    return scenes


def build_prompt(
    video_title: str, scenes: list[tuple[str, list[tuple[int, str, str, str]]]]
) -> str:
    body_parts = []
    for scene_title, lines in scenes:
        line_texts = [
            f"{line_no}. {speaker}（{expression}）: {text}"
            for line_no, speaker, expression, text in lines
        ]
        part = f"### {scene_title}\n" + "\n".join(line_texts)
        body_parts.append(part)
    dialogue_doc = "\n\n".join(body_parts)
    header = PROMPT_HEADER_TEMPLATE.format(title=video_title)
    return f"{header}\n\n---\n\n{dialogue_doc}\n"


# ============================================================
# 出力
# ============================================================


def default_out_path(md_path: Path, references_dir: Path) -> Path:
    folder_name = md_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-dialogue-review.md"


def build_output(
    video_title: str,
    md_path: Path,
    md_text: str,
    n_scenes: int,
    n_lines: int,
    response: str,
) -> str:
    sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# 「{video_title}」対話セリフレビュー（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"セリフの自然さ・キャラらしさ・掛け合いのテンポ・表情タグの妥当性・面白さ・読点の位置"
        f"の6観点でレビュー。Codex CLI（GPT）経由。読点の観点は 2026-09-05 にユーザー指定で"
        f"追加（`review_dialogue_v6.py`。TTSで不自然な間になる読点／不要な読点／不足の指摘）。\n\n"
        f"- 日時: {now}\n"
        f"- 対象台本: `{md_path}`（全{n_scenes}シーン・{n_lines}発話）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。カスタムプロンプトで実行。\n"
        f"- 依頼した観点: 1.セリフの自然さ 2.キャラらしさ 3.掛け合いのテンポ "
        f"4.表情タグの妥当性 5.面白さ 6.読点の位置（TTSで不自然な間になる読点・不要な読点・不足）\n\n"
        f"台本の書き換えは行わせていない（指摘・言い直し案の提示のみ）。\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="対話台本（めたん・ずんだもん）のセリフを GPT（Codex CLI）に自然さ・キャラらしさ・表情タグ・読点の観点でレビューさせる"
    )
    parser.add_argument("md_path", help="対話台本 Markdown のパス")
    parser.add_argument(
        "--out",
        default=None,
        help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-dialogue-review.md）",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_S,
        help=f"codex exec のタイムアウト秒（既定 {DEFAULT_TIMEOUT_S:.0f}）",
    )
    parser.add_argument("--codex-path", default=None, help="codex 実行ファイルのパス（既定: 自動検出）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    md_path = Path(args.md_path)
    if not md_path.is_file():
        print(f"台本ファイルが見つかりません: {md_path}", file=sys.stderr)
        return 1
    md_text = md_path.read_text(encoding="utf-8")

    video_title = extract_title(md_text, fallback=md_path.stem)
    scenes = extract_scenes_with_lines(md_text)
    if not scenes:
        print(
            "シーン（## シーンN + **話者**（表情）: 本文 形式の発話）が見つかりませんでした",
            file=sys.stderr,
        )
        return 2
    n_lines = sum(len(lines) for _, lines in scenes)
    print(f"{len(scenes)} シーン・{n_lines} 発話を抽出しました（タイトル: {video_title}）")

    try:
        codex_exe = resolve_codex_exe(args.codex_path)
    except ReviewScriptError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    prompt_text = build_prompt(video_title, scenes)

    start = time.time()
    try:
        response = run_codex_review(prompt_text, codex_exe=codex_exe, timeout=args.timeout)
    except ReviewScriptError as exc:
        print(f"レビューに失敗しました: {exc}", file=sys.stderr)
        return 1
    elapsed = time.time() - start

    # tools/review/ から見て ../../references（draft-explanation-video/references）を既定にする。
    references_dir = Path(__file__).resolve().parents[2] / "references"
    out_path = Path(args.out) if args.out else default_out_path(md_path, references_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        build_output(video_title, md_path, md_text, len(scenes), n_lines, response),
        encoding="utf-8",
    )

    n_table_lines = sum(1 for line in response.splitlines() if line.strip().startswith("|"))
    print(f"保存しました: {out_path}（表 {n_table_lines} 行、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
