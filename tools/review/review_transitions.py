"""対話台本（めたん・ずんだもん紙芝居版）の章と章のつなぎを、別モデル（GPT。Codex CLI 経由）に
「つなぎの自然さ・予告の具体性・章カードとの整合・反復」の観点でレビューさせるツール。

前作（ドパガキ紙芝居版）で `references/20260905-dopagaki-kamishibai-transitions-review.md` を
アドホックなカスタムプロンプトで Codex CLI に投げて得た内容・形式を、再現可能なツールにしたもの
（2026-09-05）。`review_dialogue.py` を雛形にし、codex exec 呼び出し（`review_script.py` から
import）・md のパース・出力保存の構造をそのまま流用する。**台本の文言はこのツールでは一切
編集しない**（指摘の生成のみ）。採否判断と反映は人／Claude が行う。

## 対象とする台本の書式

`review_dialogue.py` と同じ（`## シーンN: タイトル` でシーンを区切り、各シーンは 1 行 1 発話
`**話者**（表情）: 本文` が並ぶ）。加えて `**画面**` セクション内の `- 章カード: 「…」` 行を
章カードの有無・文言として抽出する（章カードが無いシーンは対象行が存在しないため自然に
「なし」扱いになる）。`## 出典リスト` 以降は対象外。

正規表現（`SCENE_HEADING_RE` / `SOURCE_LIST_MARKER_RE` / `DIALOGUE_LINE_RE` / `PAUSE_NOTE_RE` /
`extract_title`）は `review_dialogue.py` から import して再利用する。キャラクター設定は
`review_dialogue.py` の `CHARACTER_PROFILE` を流用せず、このツール専用に汎用版（特定動画の
題材に依存する記述を含まない版）を定義する（`review_dialogue.py` の版は「ドパガキ」動画向けの
題材依存の一文を含むため、他の題材の台本に使い回すと誤ったキャラ像を GPT に渡してしまう）。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_transitions.py scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-transitions-review.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 全境界（シーン数-1）をまとめて1回の codex exec 呼び出しに渡すため出力が長くなりやすい。
  「usage limit」「at capacity」等のクォータ超過で失敗することがあり、その場合は60秒待って
  1回だけ再試行する。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# review_dialogue.py / review_script.py と同じディレクトリにあるため、そのまま import して
# 再利用する（正規表現・キャラクター設定・codex exec 呼び出し）。
from review_dialogue import (
    DIALOGUE_LINE_RE,
    PAUSE_NOTE_RE,
    SCENE_HEADING_RE,
    SOURCE_LIST_MARKER_RE,
    extract_title,
)
from review_script import (
    DEFAULT_TIMEOUT_S,
    ReviewScriptError,
    resolve_codex_exe,
    run_codex_review,
)

# ============================================================
# 定数
# ============================================================

# review_dialogue.py の CHARACTER_PROFILE は「ドパガキ」動画向けの題材依存の一文を含むため
# 流用しない。ここでは題材によらない汎用版を定義する（当事者性の有無・程度は台本ごとに違うため
# 「当事者としての反応を交える」という一般的な記述に留める）。
CHARACTER_PROFILE = (
    "- **ずんだもん**（聞き手）: 語尾は「〜のだ」「〜なのだ」。無邪気・素直・時々ボケる。"
    "疑問・驚き・言い換え・ツッコミ・（テーマによっては当事者としての反応）で掛け合いの節目を"
    "作る。\n"
    "- **四国めたん**（解説役）: 落ち着いた丁寧語に少しお嬢様の余裕（「〜のよ」「〜かしら」。"
    "「〜ですわ」は多用しない）。ずんだもんに向かって話しかける口調で、講義調にはならない。"
)

# `**画面**` セクション内の `- 章カード: 「…」` 行。章カードが無いシーンでは一致しないため、
# 「なし」として自然に扱われる。
CHAPTER_CARD_RE = re.compile(r"^-\s*章カード[:：]\s*「(.+?)」\s*$", re.MULTILINE)

N_TAIL_LINES = 3
N_HEAD_LINES = 3

OBSERVATION_POINTS = (
    "(a) **つなぎの自然さ**: 前シーン末尾の発話から次シーン冒頭の発話への接続が、話の流れとして"
    "不自然でないか（唐突な話題転換、同じ語・同じ言い回しの直後の反復による稚拙さ等）。\n"
    "(b) **予告の具体性**: 前シーン末尾で次章の話題を予告している場合、具体性が適切か。"
    "抽象的すぎて引きが弱い場合と、次シーンの冒頭でこれから話す内容をほぼそのまま先取りして"
    "しまい重複感が出ている場合の両方を指摘してください。\n"
    "(c) **章カードとの整合**: 次シーンに章カードがある場合、その位置が大きな論点の反転・検証"
    "開始にふさわしいか。章カードが無い境界についても、本来あったほうがよいか、逆に不要な"
    "場面転換で追加すべきでないかを判断してください。\n"
    "(d) **境界ごとの判定**: (a)〜(c) を踏まえて境界ごとに「可」または「要修正」を判定し、"
    "要修正の場合は言い直し案（セリフとして自然な代替案。事実・数値・固有名詞は変えないこと）を"
    "示してください。\n"
    "(e) **反復チェック**: 予告文・次シーン冒頭で使われる接続の型（例:「次は〜」「実は〜」で"
    "始まる、同じキーワードを予告と冒頭の両方で繰り返す）が、動画全体を通して3回以上"
    "同じパターンで連続・多発していないか。該当する場合は、使い分けられる言い換え案を"
    "複数パターン示してください。"
)

PROMPT_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画の構成レビュアーです。対象は「{title}」。四国めたん"
    "（VOICEVOX、解説役）とずんだもん（VOICEVOX、聞き手）の二人による対話劇で、絵は紙芝居風"
    "（緑の黒板・木枠の額縁・棒付きの紙人形）です。視聴者は一般層で、専門知識は仮定しません。\n\n"
    "この台本は複数のシーン（章に近い単位）で構成されています。シーンとシーンの境界（つなぎ）が、"
    "視聴者の関心を途切れさせずに次章へ引き継げているかをレビューしてください。各境界について、"
    "前シーンの末尾{n_tail}発話・次シーンの章カードの有無・次シーンの冒頭{n_head}発話を"
    "以下に列挙します。\n\n"
    "## キャラクター設定\n"
    f"{CHARACTER_PROFILE}\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "まず「## 境界ごとの判定」として、Markdown の表（列: 境界／判定（可・要修正）／(a) 自然さ／"
    "(b) 具体性／言い直し案）を出力してください。判定が「可」の境界は言い直し案を「—」にして"
    "構いません。\n\n"
    "続けて次の3つのセクションを出力してください。\n"
    "- 「## 章カードについて」: 各章カードの配置意図の妥当性、章カードが無い境界の判断、"
    "追加・削除すべき境界があればその理由。\n"
    "- 「## 反復チェック」: (e) の観点での指摘と言い換え案。\n"
    "- 「## 総評」: 全体を通した評価（3〜6行）。\n\n"
    "台本の書き換えはせず、指摘と言い直し案の提示のみを行ってください。ファイルは編集しない"
    "でください。"
)


@dataclass
class SceneInfo:
    title: str
    lines: list[tuple[str, str, str]]  # (speaker, expression, text)
    chapter_card: str | None


# ============================================================
# 台本 md からシーン・章カード抽出
# ============================================================


def extract_scenes_with_chapters(md_text: str) -> list[SceneInfo]:
    """シーン見出しごとに SceneInfo を抽出する。`## 出典リスト` 以降は除外する。"""

    source_match = SOURCE_LIST_MARKER_RE.search(md_text)
    body = md_text[: source_match.start()] if source_match else md_text

    headings = list(SCENE_HEADING_RE.finditer(body))
    scenes: list[SceneInfo] = []
    for i, m in enumerate(headings):
        title = m.group(1).strip()
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        section = body[start:end]

        lines: list[tuple[str, str, str]] = []
        for dm in DIALOGUE_LINE_RE.finditer(section):
            speaker, expression, text = dm.group(1), dm.group(2), dm.group(3).strip()
            text = PAUSE_NOTE_RE.sub("", text).strip()
            lines.append((speaker, expression, text))

        chapter_match = CHAPTER_CARD_RE.search(section)
        chapter_card = chapter_match.group(1).strip() if chapter_match else None

        if lines:
            scenes.append(SceneInfo(title=title, lines=lines, chapter_card=chapter_card))
    return scenes


def format_lines(lines: list[tuple[str, str, str]]) -> str:
    return "\n".join(f"{speaker}（{expression}）: {text}" for speaker, expression, text in lines)


def build_prompt(video_title: str, scenes: list[SceneInfo]) -> str:
    boundary_parts = []
    for i in range(len(scenes) - 1):
        prev_scene = scenes[i]
        next_scene = scenes[i + 1]
        tail = prev_scene.lines[-N_TAIL_LINES:]
        head = next_scene.lines[:N_HEAD_LINES]
        chapter_text = f"「{next_scene.chapter_card}」" if next_scene.chapter_card else "なし"
        part = (
            f"### 境界 S{i + 1}→S{i + 2}\n"
            f"前シーン「{prev_scene.title}」末尾{len(tail)}発話:\n{format_lines(tail)}\n\n"
            f"次シーン「{next_scene.title}」の章カード: {chapter_text}\n"
            f"次シーン「{next_scene.title}」冒頭{len(head)}発話:\n{format_lines(head)}"
        )
        boundary_parts.append(part)
    boundary_doc = "\n\n".join(boundary_parts)
    header = PROMPT_HEADER_TEMPLATE.format(
        title=video_title, n_tail=N_TAIL_LINES, n_head=N_HEAD_LINES
    )
    return f"{header}\n\n---\n\n{boundary_doc}\n"


# ============================================================
# 出力
# ============================================================


def default_out_path(md_path: Path, references_dir: Path) -> Path:
    folder_name = md_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-transitions-review.md"


def build_output(
    video_title: str,
    md_path: Path,
    md_text: str,
    n_scenes: int,
    n_boundaries: int,
    response: str,
) -> str:
    sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# 「{video_title}」章のつなぎレビュー（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"章と章のつなぎ（{n_boundaries}境界）について、つなぎの自然さ・予告の具体性・"
        f"章カードとの整合・反復の4観点でレビュー。Codex CLI（GPT）経由。\n\n"
        f"- 日時: {now}\n"
        f"- 対象台本: `{md_path}`（全{n_scenes}シーン・{n_boundaries}境界）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 観点: (a) つなぎの自然さ (b) 予告の具体性 (c) 章カードとの整合 (d) 境界ごとの判定 "
        f"(e) 反復チェック\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。カスタムプロンプトで実行。\n\n"
        f"台本の書き換えは行わせていない（指摘・言い直し案の提示のみ）。\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="対話台本（めたん・ずんだもん）の章のつなぎを GPT（Codex CLI）に自然さ・予告の具体性・章カード整合・反復の観点でレビューさせる"
    )
    parser.add_argument("md_path", help="対話台本 Markdown のパス")
    parser.add_argument(
        "--out",
        default=None,
        help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-transitions-review.md）",
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
    scenes = extract_scenes_with_chapters(md_text)
    if len(scenes) < 2:
        print(
            "境界を作るには2シーン以上必要です（## シーンN + **話者**（表情）: 本文 形式の"
            "発話が見つかりませんでした）",
            file=sys.stderr,
        )
        return 2
    n_boundaries = len(scenes) - 1
    print(f"{len(scenes)} シーン・{n_boundaries} 境界を抽出しました（タイトル: {video_title}）")

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
        build_output(video_title, md_path, md_text, len(scenes), n_boundaries, response),
        encoding="utf-8",
    )

    n_table_lines = sum(1 for line in response.splitlines() if line.strip().startswith("|"))
    print(f"保存しました: {out_path}（表 {n_table_lines} 行、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
