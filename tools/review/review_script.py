"""台本ドラフト（Markdown）のナレーション全文を、別モデル（GPT。Codex CLI 経由）で
レビューするツール。

draft-explanation-video の台本執筆フローに「別モデルによる自動レビュー」を組み込む一環
（2026-08-27）。ナレーションの分かりやすさを7観点でチェックし、指摘と修正案を表形式で
受け取る。**台本の文言はこのツールでは一切編集しない**（指摘の生成のみ）。採否判断と
反映は人／Claude が行う。

先行実験（scratchpad/gptreview/prompt.txt・references/20260827-reisho-gptreview.md）と
同じ7観点・同じ codex exec の呼び出し方式をそのままツール化したもの。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_script.py scripts/20260827-cynicism/20260827-cynicism.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-gptreview.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 1回の呼び出しに1〜3分程度かかる。「usage limit」「at capacity」等のクォータ超過で
  失敗することがあり、その場合は60秒待って1回だけ再試行する。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

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
"""PATH 上に codex が見つからない場合のフォールバック先（script-to-video/tools/codex_imagegen
と同じ探索方針）。"""

DEFAULT_TIMEOUT_S = 900.0

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

APPENDIX_MARKER_RE = re.compile(r"^## 付録", re.MULTILINE)
SCENE_HEADING_RE = re.compile(r"^## (シーン\d+.*)$", re.MULTILINE)
NARRATION_RE = re.compile(r"\*\*ナレーション\*\*\s*\n(.*?)\n\s*\*\*画面\*\*", re.DOTALL)

OBSERVATION_POINTS = (
    "1. 用語が説明される前に使われていないか（初出順の問題）\n"
    "2. まだ語っていない話を前提にした言い回しがないか（前振りのない参照）\n"
    "3. 一文が長すぎる／同音異義で聞き間違えやすい／機械音声で読みにくい箇所\n"
    "4. 論理の飛躍、つながりの弱い段落間の接続\n"
    "5. 同じ構文・同じ語の反復が3回以上続く箇所\n"
    "6. 冗長で削れる文\n"
    "7. 結論が、冒頭で提示した問いに対してきちんと着地しているか"
)

PROMPT_HEADER = (
    "あなたは解説動画（YouTube、機械音声ナレーション）の台本レビュアーです。以下の narration.md は、"
    "動画のナレーション全文（シーンごと）です。視聴者は一般の視聴者で、動画のテーマに関する予備知識は"
    "仮定しません。\n\n"
    "次の観点で、分かりにくい箇所・不自然な箇所を洗い出してください。\n"
    f"{OBSERVATION_POINTS}\n\n"
    "出力は日本語で、Markdown の表（シーン／該当文（短い引用）／問題の種類／修正案）にしてください。"
    "最大20行。問題がない観点はその旨を1行で。台本の書き換えはせず、指摘と修正案のみ。"
    "ファイルは編集しないでください。"
)


class ReviewScriptError(RuntimeError):
    """レビュー実行に失敗したときのエラー。"""


# ============================================================
# codex exe の解決
# ============================================================


def resolve_codex_exe(explicit: str | None) -> str:
    if explicit:
        return explicit
    which = shutil.which("codex") or shutil.which("codex.bat")
    if which:
        return which
    if WINGET_CODEX_FALLBACK.exists():
        return str(WINGET_CODEX_FALLBACK)
    raise ReviewScriptError(
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


# ============================================================
# 台本 md からナレーション抽出
# ============================================================


def extract_scenes(md_text: str) -> list[tuple[str, str]]:
    """シーン見出しごとに (タイトル, ナレーション本文) を抽出する。「## 付録」以降は除外する。"""

    appendix_match = APPENDIX_MARKER_RE.search(md_text)
    body = md_text[: appendix_match.start()] if appendix_match else md_text

    headings = list(SCENE_HEADING_RE.finditer(body))
    scenes: list[tuple[str, str]] = []
    for i, m in enumerate(headings):
        title = m.group(1).strip()
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section = body[start:end]
        narration_match = NARRATION_RE.search(section)
        if narration_match is None:
            continue
        narration = narration_match.group(1).strip()
        if narration:
            scenes.append((title, narration))
    return scenes


def build_prompt(scenes: list[tuple[str, str]]) -> str:
    body_parts = [f"### {title}\n{narration}" for title, narration in scenes]
    narration_doc = "\n\n".join(body_parts)
    return f"{PROMPT_HEADER}\n\n---\n\n{narration_doc}\n"


# ============================================================
# codex exec 呼び出し
# ============================================================


def _run_codex_once(
    codex_exe: str, prompt_text: str, *, timeout: float, cwd: Path
) -> str:
    out_file = cwd / "response.md"
    cmd = [
        codex_exe,
        "exec",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        str(cwd),
        "-o",
        str(out_file),
        "-",
    ]
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
        raise ReviewScriptError(f"codex exec がタイムアウトしました（{timeout:.0f}秒）") from exc

    combined = f"{result.stdout or ''}\n{result.stderr or ''}"
    rate_limit = _detect_rate_limit(combined)

    if result.returncode != 0:
        if rate_limit:
            raise ReviewScriptError(f"__RATE_LIMIT__:{rate_limit}")
        raise ReviewScriptError(
            f"codex exec が失敗しました（終了コード {result.returncode}）。出力末尾:\n{_tail(combined)}"
        )

    if not out_file.exists():
        if rate_limit:
            raise ReviewScriptError(f"__RATE_LIMIT__:{rate_limit}")
        raise ReviewScriptError(
            f"codex exec の最終応答ファイルが生成されませんでした。出力末尾:\n{_tail(combined)}"
        )

    return out_file.read_text(encoding="utf-8").strip()


def run_codex_review(prompt_text: str, *, codex_exe: str, timeout: float) -> str:
    """レート制限検知時は60秒待って1回だけ再試行する。"""

    attempt = 0
    while True:
        attempt += 1
        with tempfile.TemporaryDirectory(prefix="review_script_") as tmp:
            try:
                return _run_codex_once(codex_exe, prompt_text, timeout=timeout, cwd=Path(tmp))
            except ReviewScriptError as exc:
                message = str(exc)
                if message.startswith("__RATE_LIMIT__") and attempt <= MAX_RATE_LIMIT_RETRIES:
                    pattern = message.split(":", 1)[1]
                    print(
                        f"レート制限/クォータ超過を検知しました（文言: \"{pattern}\"）。"
                        f"{RATE_LIMIT_WAIT_S:.0f}秒待って再試行します",
                        file=sys.stderr,
                    )
                    time.sleep(RATE_LIMIT_WAIT_S)
                    continue
                if message.startswith("__RATE_LIMIT__"):
                    raise ReviewScriptError("レート制限/クォータ超過のため断念しました（1回再試行済み）") from exc
                raise


# ============================================================
# 出力
# ============================================================


def default_out_path(md_path: Path, references_dir: Path) -> Path:
    folder_name = md_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-gptreview.md"


def build_output(md_path: Path, md_text: str, response: str) -> str:
    sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# GPT（Codex CLI 経由）による台本レビュー\n\n"
        f"- 日時: {now}\n"
        f"- 入力ファイル: {md_path}\n"
        f"- SHA256（先頭8桁）: {sha}\n"
        f"- 観点: 7項目（用語初出順／前振りのない参照／長文・同音異義／論理の飛躍／"
        f"同構文の反復／冗長／結論の着地）\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="台本ドラフト（md）を GPT（Codex CLI）でレビューする")
    parser.add_argument("md_path", help="台本 Markdown のパス")
    parser.add_argument("--out", default=None, help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-gptreview.md）")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help=f"codex exec のタイムアウト秒（既定 {DEFAULT_TIMEOUT_S:.0f}）")
    parser.add_argument("--codex-path", default=None, help="codex 実行ファイルのパス（既定: 自動検出）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    md_path = Path(args.md_path)
    if not md_path.is_file():
        print(f"台本ファイルが見つかりません: {md_path}", file=sys.stderr)
        return 1
    md_text = md_path.read_text(encoding="utf-8")

    scenes = extract_scenes(md_text)
    if not scenes:
        print("シーン（## シーンN + **ナレーション**/**画面**）が見つかりませんでした", file=sys.stderr)
        return 2
    print(f"{len(scenes)} シーンのナレーションを抽出しました")

    try:
        codex_exe = resolve_codex_exe(args.codex_path)
    except ReviewScriptError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    prompt_text = build_prompt(scenes)

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
    out_path.write_text(build_output(md_path, md_text, response), encoding="utf-8")

    n_table_lines = sum(1 for line in response.splitlines() if line.strip().startswith("|"))
    print(f"保存しました: {out_path}（表 {n_table_lines} 行、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
