"""台本ドラフト（Markdown）の事実主張（年号・人名・組織名・制度・数値・書誌）を、別モデル
（GPT。Codex CLI 経由）に**独立して**ファクトチェックさせるツール。

台本はすでに一次資料で裏取り済みだが、見落としの検出が目的。`review_holistic.py`（面白さ・
視聴維持観点）、`review_script.py`（分かりやすさ観点）とは別軸のレビュー。**台本の文言はこの
ツールでは一切編集しない**（指摘の生成のみ）。採否判断と反映は人／Claude が行う。

codex exec の呼び出し方式（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、
`-o` で応答ファイル出力、クォータ超過時60秒待ち1回リトライ）とシーン抽出（`## シーンN...` 〜
次見出し、「## 付録」以降は除外）は `review_script.py` の実装をそのまま import して再利用する。
タイトル抽出（先頭 `# 見出し`）は `review_holistic.py` の実装を再利用する。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_factcheck.py scripts/20260902-pro-emergence/20260902-pro-emergence.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-factcheck.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 「usage limit」「at capacity」等のクォータ超過で失敗することがあり、その場合は60秒待って
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

# review_script.py / review_holistic.py と同じディレクトリにあるため、そのまま import して
# 再利用する（codex exe 解決・レート制限リトライ付き codex exec 呼び出し・台本 md のシーン
# 境界抽出・タイトル抽出）。
from review_script import (
    DEFAULT_TIMEOUT_S,
    ReviewScriptError,
    extract_scenes,
    resolve_codex_exe,
    run_codex_review,
)
from review_holistic import extract_title

# ============================================================
# 定数
# ============================================================

# 出典一覧セクションの開始位置（このセクションの見出し文言は台本テンプレ・既存台本と揃える。
# `## 出典一覧` で始まる見出しなら細かい括弧書きの違いは問わない）。
APPENDIX_SOURCES_RE = re.compile(r"^## 出典一覧.*$", re.MULTILINE)

PROMPT_HEADER_TEMPLATE = (
    "あなたは解説動画（YouTube、機械音声ナレーション）の台本のファクトチェッカーです。以下は台本"
    "「{title}」のシーンごとのナレーション全文（{n_scenes}シーン）と、執筆者が用意した出典一覧・"
    "要確認事項です。台本は執筆時に一次資料で裏取り済みですが、あなたには**独立した第三者チェック**"
    "として、見落としがないかを検証してほしい。\n\n"
    "ナレーション中の事実主張（年号・人名・組織名・制度・数値・書誌〔著者・誌名・巻号・年〕・"
    "因果関係の言い切りを重点的に見てください）を一つずつ抽出し、次の3種類に分類してください。\n\n"
    "1. **誤りと考えられるもの**（あなたの知識と明確に矛盾する）\n"
    "2. **疑わしい・要確認のもの**（誤りとは断定できないが、根拠が薄い／出典との整合が取れない／"
    "確度に疑問がある）\n"
    "3. **正しいと確認できるもの**（あなたの知識で裏付けが取れる）\n\n"
    "## 出力形式\n\n"
    "1と2について、それぞれ以下の列を持つ Markdown の表で示してください。\n"
    "| 該当文の引用 | 何が問題か | 正しいと思われる内容 | 根拠（知識ベースの場合はその旨と確度） |\n\n"
    "1と2の該当箇所が0件の場合は、表の代わりに「なし」と明記してください。\n\n"
    "3については、表は不要です。特に重要な確認済み事実（年号・数値・書誌など）を箇条書きで"
    "5〜10件程度、簡潔に挙げてください。\n\n"
    "## 注意事項\n\n"
    "- 台本の書き換えはせず、指摘と評価のみを行ってください。ファイルは編集しないでください。\n"
    "- 断定的な誤り指摘は、あなたの知識に基づく推測ではなく、確度の高いものに限ってください。"
    "確度が低い場合は2（要確認）に分類し、根拠欄にその旨を明記してください。\n"
    "- 執筆者が「要確認事項」として断定を避けた箇所（末尾に列挙）は、その配慮が妥当かどうかも"
    "含めて評価してください。\n"
    "- 出典一覧に挙がっていない独自の事実主張（数値・年号など）が本文中にあれば、それも"
    "チェック対象に含めてください。\n"
)


# ============================================================
# 台本 md から出典一覧・要確認事項を抽出
# ============================================================


def extract_sources_appendix(md_text: str) -> str:
    """「## 出典一覧」以降（出典一覧＋要確認事項）を丸ごと取り出す。見つからなければ空文字。"""

    match = APPENDIX_SOURCES_RE.search(md_text)
    if not match:
        return ""
    return md_text[match.start():].strip()


def build_prompt(video_title: str, scenes: list[tuple[str, str]], sources_appendix: str) -> str:
    body_parts = [f"### {title}\n**ナレーション**\n{narration}" for title, narration in scenes]
    narration_doc = "\n\n".join(body_parts)
    header = PROMPT_HEADER_TEMPLATE.format(title=video_title, n_scenes=len(scenes))
    parts = [header, "---", narration_doc]
    if sources_appendix:
        parts.append("---")
        parts.append(sources_appendix)
    return "\n\n".join(parts) + "\n"


# ============================================================
# 出力
# ============================================================


def default_out_path(md_path: Path, references_dir: Path) -> Path:
    folder_name = md_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-factcheck.md"


def build_output(
    video_title: str, md_path: Path, md_text: str, n_scenes: int, response: str
) -> str:
    sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# 「{video_title}」ファクトチェック（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"年号・人名・組織名・制度・数値・書誌の事実主張を、別モデル（GPT）に独立検証させたもの。"
        f"台本は一次資料で裏取り済みだが、見落とし検出が目的。Codex CLI（GPT）経由。\n\n"
        f"- 日時: {now}\n"
        f"- 対象台本: `{md_path}`（全{n_scenes}シーン）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。ナレーション全文＋出典一覧＋要確認事項をカスタムプロンプトで渡している。\n"
        f"- 分類: ①誤りと考えられるもの ②疑わしい・要確認のもの ③正しいと確認できるもの\n\n"
        f"台本の書き換えは行わせていない（指摘の提示のみ）。\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="台本ドラフト（md）の事実主張（年号・人名・組織名・数値・書誌）を GPT（Codex CLI）に独立ファクトチェックさせる"
    )
    parser.add_argument("md_path", help="台本 Markdown のパス")
    parser.add_argument(
        "--out", default=None, help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-factcheck.md）"
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
    scenes = extract_scenes(md_text)
    if not scenes:
        print("シーン（## シーンN + **ナレーション**/**画面**）が見つかりませんでした", file=sys.stderr)
        return 2
    sources_appendix = extract_sources_appendix(md_text)
    if not sources_appendix:
        print("警告: 「## 出典一覧」セクションが見つかりませんでした（出典なしでチェックを続行します）", file=sys.stderr)
    print(f"{len(scenes)} シーンのナレーションを抽出しました（タイトル: {video_title}）")

    try:
        codex_exe = resolve_codex_exe(args.codex_path)
    except ReviewScriptError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    prompt_text = build_prompt(video_title, scenes, sources_appendix)

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

    n_table_lines = sum(1 for line in response.splitlines() if line.strip().startswith("|"))
    print(f"保存しました: {out_path}（表 {n_table_lines} 行、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
