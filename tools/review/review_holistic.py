"""台本ドラフト（Markdown）を「面白さ・視聴維持・見やすさ・タイトル」の観点で総合的に
別モデル（GPT。Codex CLI 経由）にレビューさせるツール。

`review_script.py`（用語初出順・論理の飛躍など7観点の分かりやすさレビュー）とは別軸の、
企画レビュー寄りのチェック。先行実験（`references/20260901-dopagaki-holistic-review.md`）で
アドホックに実行したカスタムプロンプトをツール化したもの（2026-09-01）。**台本の文言はこの
ツールでは一切編集しない**（指摘の生成のみ）。採否判断と反映は人／Claude が行う。

codex exec の呼び出し方式（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、
`-o` で応答ファイル出力、クォータ超過時60秒待ち1回リトライ）は `review_script.py` の実装を
そのまま import して再利用する。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_holistic.py scripts/20260827-cynicism/20260827-cynicism.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-holistic.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 1回の呼び出しに3〜8分程度かかる（7観点レビューよりプロンプトが長く出力も長いため）。
  「usage limit」「at capacity」等のクォータ超過で失敗することがあり、その場合は60秒待って
  1回だけ再試行する。
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
# （codex exe 解決・レート制限リトライ付き codex exec 呼び出し・台本 md のシーン境界抽出）。
from review_script import (
    APPENDIX_MARKER_RE,
    DEFAULT_TIMEOUT_S,
    NARRATION_RE,
    SCENE_HEADING_RE,
    ReviewScriptError,
    resolve_codex_exe,
    run_codex_review,
)

# ============================================================
# 定数
# ============================================================

TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
SCREEN_MARKER_RE = re.compile(r"\*\*画面\*\*\s*\n")
TRAILING_SEPARATOR_RE = re.compile(r"\n-{3,}\s*$")

PROMPT_HEADER_TEMPLATE = (
    "あなたは解説動画（YouTube、機械音声ナレーション）の企画・レビュアーです。以下は台本"
    "「{title}」のシーンごとのナレーション全文と画面指示（テロップ・ビジュアル意図・章タイトル等）"
    "です。視聴者は一般の視聴者で、動画テーマの予備知識は仮定しません。\n\n"
    "台本の面白さ・視聴維持・見やすさ・タイトル妥当性を、次の5観点で総合的にレビューしてください。"
    "分かりやすさ（用語初出順・論理の飛躍等）は別のレビューで扱うため、ここでは扱わなくてよい。\n\n"
    "## 1. 面白さの総合採点\n"
    "10点満点で総合点をつけ、根拠を述べてください。加えて次を個別に採点・評価してください。\n"
    "- 冒頭15秒のフックの強さ（10点満点）\n"
    "- 中だるみが起きそうな箇所（シーン番号を挙げて具体的に）\n"
    "- 決め台詞（強調して見せる・間を置く文）の効き（該当する文ごとに10点満点で個別採点）\n\n"
    "## 2. 視聴維持の危険箇所\n"
    "視聴者が離脱しそうな箇所を挙げてください。各指摘に**シーン番号と該当文の引用を必須**とします。\n\n"
    "## 3. 見やすさ\n"
    "章構成のリズム、図解・画面転換の頻度がナレーションの情報密度と合っているかを、各シーンの"
    "「画面」欄（テロップ・ビジュアル意図・章タイトル等）から判断してください。\n\n"
    "## 4. タイトル・サムネ文言の妥当性\n"
    "現在のタイトル「{title}」を10点満点で評価し、理由を述べてください。加えて代案を3つ提示し、"
    "**各代案の根拠として台本中の該当文を引用**してください。\n\n"
    "## 5. 改善提案\n"
    "改善提案を**最低5件**、優先度（S/A/B/C）付きで挙げてください。全体を褒めるだけの出力は"
    "禁止します。既存の強みに触れるのは構いませんが、必ず具体的な改善余地を示してください。\n\n"
    "出力は日本語 Markdown で、上記5つの見出し（## 1.〜## 5.）に沿って構成してください。"
    "台本の書き換えはせず、指摘と評価のみを行ってください。ファイルは編集しないでください。"
)

OBSERVATION_POINTS_SUMMARY = (
    "1. 面白さの総合採点（10点満点）と根拠（フックの強さ・中だるみ箇所・決め台詞の効き）\n"
    "2. 視聴維持の危険箇所（シーン番号・該当文の引用付き）\n"
    "3. 見やすさ（章構成のリズム、図解・画面転換の頻度とナレーションの整合）\n"
    "4. タイトル・サムネ文言の妥当性（代案3つ、根拠となる台本中の文の引用付き）\n"
    "5. 改善提案（最低5件、優先度つき）"
)


# ============================================================
# 台本 md からシーン抽出（ナレーション＋画面）
# ============================================================


def extract_title(md_text: str, fallback: str) -> str:
    """台本 md の先頭 `# 見出し` を動画タイトルとして取り出す。無ければ fallback。"""

    match = TITLE_RE.search(md_text)
    return match.group(1).strip() if match else fallback


def extract_scenes_with_screen(md_text: str) -> list[tuple[str, str, str]]:
    """シーン見出しごとに (タイトル, ナレーション本文, 画面欄本文) を抽出する。

    `review_script.extract_scenes` と同じシーン境界（`## シーンN...` 〜 次見出し、
    「## 付録」以降は除外）を使うが、見やすさ観点の判断に必要な「画面」欄も併せて返す。
    """

    appendix_match = APPENDIX_MARKER_RE.search(md_text)
    body = md_text[: appendix_match.start()] if appendix_match else md_text

    headings = list(SCENE_HEADING_RE.finditer(body))
    scenes: list[tuple[str, str, str]] = []
    for i, m in enumerate(headings):
        title = m.group(1).strip()
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section = body[start:end]

        narration_match = NARRATION_RE.search(section)
        if narration_match is None:
            continue
        narration = narration_match.group(1).strip()
        if not narration:
            continue

        screen_match = SCREEN_MARKER_RE.search(section)
        screen_text = ""
        if screen_match:
            screen_text = section[screen_match.end():].strip()
            screen_text = TRAILING_SEPARATOR_RE.sub("", screen_text).strip()

        scenes.append((title, narration, screen_text))
    return scenes


def build_prompt(video_title: str, scenes: list[tuple[str, str, str]]) -> str:
    body_parts = []
    for scene_title, narration, screen_text in scenes:
        part = f"### {scene_title}\n**ナレーション**\n{narration}"
        if screen_text:
            part += f"\n\n**画面**\n{screen_text}"
        body_parts.append(part)
    narration_doc = "\n\n".join(body_parts)
    header = PROMPT_HEADER_TEMPLATE.format(title=video_title)
    return f"{header}\n\n---\n\n{narration_doc}\n"


# ============================================================
# 出力
# ============================================================


def default_out_path(md_path: Path, references_dir: Path) -> Path:
    folder_name = md_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-holistic.md"


def build_output(
    video_title: str, md_path: Path, md_text: str, n_scenes: int, response: str
) -> str:
    sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# 「{video_title}」総合レビュー（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"面白さ・視聴維持・見やすさ・タイトル妥当性の総合レビュー。Codex CLI（GPT）経由。\n\n"
        f"- 日時: {now}\n"
        f"- 対象台本: `{md_path}`（全{n_scenes}シーン）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。7観点レビューではなくカスタムプロンプトで実行。\n"
        f"- 依頼した観点:\n"
        + "\n".join(f"  {line}" for line in OBSERVATION_POINTS_SUMMARY.splitlines())
        + "\n\n"
        f"台本の書き換えは行わせていない（指摘・改善案の提示のみ）。\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="台本ドラフト（md）を面白さ・視聴維持・見やすさ・タイトルの観点で GPT（Codex CLI）に総合レビューさせる"
    )
    parser.add_argument("md_path", help="台本 Markdown のパス")
    parser.add_argument(
        "--out", default=None, help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-holistic.md）"
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT_S, help=f"codex exec のタイムアウト秒（既定 {DEFAULT_TIMEOUT_S:.0f}）"
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
    scenes = extract_scenes_with_screen(md_text)
    if not scenes:
        print("シーン（## シーンN + **ナレーション**/**画面**）が見つかりませんでした", file=sys.stderr)
        return 2
    print(f"{len(scenes)} シーンのナレーション・画面指示を抽出しました（タイトル: {video_title}）")

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
        build_output(video_title, md_path, md_text, len(scenes), response), encoding="utf-8"
    )

    n_heading_lines = sum(1 for line in response.splitlines() if line.strip().startswith("##"))
    print(f"保存しました: {out_path}（見出し {n_heading_lines} 件、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
