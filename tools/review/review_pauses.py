"""対話台本（めたん・ずんだもん紙芝居版）のシーン YAML の `pause_after` を、別モデル（GPT。
Codex CLI 経由）に「間が足りない／長すぎる箇所・息継ぎ位置」の観点でレビューさせるツール。

前作（ドパガキ紙芝居版）で `references/20260905-dopagaki-kamishibai-pause-review.md` を
アドホックなカスタムプロンプトで Codex CLI に投げて得た内容・形式を、再現可能なツールにしたもの
（2026-09-05）。`review_dialogue.py` を雛形にし、codex exec 呼び出し（`review_script.py` から
import）・出力保存の構造をそのまま流用する。**台本・YAML の文言はこのツールでは一切編集
しない**（指摘の生成のみ）。採否判断と反映は人／Claude が行う。

## 対象とする YAML の書式

script-to-video の紙芝居モードのシーン YAML（`tools/kamishibai_md_to_yaml.py` の出力）。
`scenes[]` の各要素が `id` / `title` / `chapter_title`（無ければ `null`）/ `narration[]`
（各要素が `text` / `speaker` / `expression` / `pause_after`）を持つ想定。

## 話速（tempo）前提

このプロジェクトの対話台本は話速 1.1 倍（`--tts-rate` ではなく VOICEVOX 系の
`--tempo 1.1`）を標準にしており、`pause_after` は `tools/kamishibai_md_to_yaml.py` の
`PAUSE_PRESETS` で自動付与される（話者交代・文境界・章転換）。決め文（「（間 N）」で台本に
明示された保持）は自動生成対象外で、台本執筆時に個別の秒数を書く。既定は `--tempo 1.1` とし、
`--tempo 1.0` を指定すると等速用の目安値をプロンプトに使う。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_pauses.py scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.yaml

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-pause-review.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 全シーンの `pause_after` をまとめて1回の codex exec 呼び出しに渡すため出力が長くなりやすい。
  「usage limit」「at capacity」等のクォータ超過で失敗することがあり、その場合は60秒待って
  1回だけ再試行する。
- PyYAML（`import yaml`）が必要（script-to-video の venv には入っている）。
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

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

# `tools/kamishibai_md_to_yaml.py` の PAUSE_PRESETS と同じ値（話者交代・文境界・章転換の
# 自動付与分）。決め文（台本の「（間 N）」で個別に書く保持）はこのプリセットの対象外。
PAUSE_PRESETS = {
    "1.0": {"speaker_change": 0.4, "sentence": 0.35, "chapter_transition": 1.0},
    "1.1": {"speaker_change": 0.45, "sentence": 0.35, "chapter_transition": 1.2},
}
# 決め文の目安（話速に依らず本作の設計判断。CLAUDE.md のビート運用ルール「決め文は画面を
# 保持したまま pause_after 2.0〜2.5秒」を踏襲。前作の間レビューでは対話テンポに対して長すぎる
# との指摘があったため、目安として提示しつつ判断はGPTに委ねる）。
DECISIVE_LINE_TARGET = "2.0〜2.5秒（ただし直後がずんだもんの即時リアクションの場合は短めが適切なこともある）"

OBSERVATION_POINTS = (
    "1. **間が足りない、または長すぎる箇所**: `pause_after` の値が、直前のセグメントの情報密度・"
    "意味の重さに対して短すぎる（消化する間がない）、または長すぎる（テンポが間延びする、"
    "直後が即時のリアクションなのに間が空きすぎて反応が遅れて聞こえる）箇所を指摘し、"
    "推奨値を示してください。\n"
    "2. **決め文の後の保持**: 言い切り・重要な反転・強い引用の直後の `pause_after` が、"
    f"目安（{DECISIVE_LINE_TARGET}）に対して適切かを判定してください。\n"
    "3. **話者交代の間**: 話者が変わる箇所の `pause_after` が、直前の発話の重さ（高密度な説明・"
    "重い引用・強い反転の直後かどうか）に対して適切かを判定してください。\n"
    "4. **章転換**: シーンの最後のセグメント（次シーンへの境界）の `pause_after` が、次シーンに"
    "章カードがあるか・動画全体の最終シーンかに応じて適切かを判定してください。\n"
    "5. **息継ぎ位置**: 1セグメントの文が長すぎて、機械音声でも人が読んでも息が続かない、"
    "または情報が過多で聞き手が処理しきれない箇所を指摘し、文を分ける位置（分割案）を"
    "示してください（`pause_after` の変更ではなく、セグメントを分割する提案）。"
)

PROMPT_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画の音声設計レビュアーです。対象は「{title}」。四国めたん"
    "（VOICEVOX、解説役）とずんだもん（VOICEVOX、聞き手）の二人による対話劇です。以下は"
    "シーン YAML から抽出した各シーンのナレーションセグメントで、各行に `pause_after`"
    "（そのセグメントの直後に置かれる無音の長さ、秒）を付記しています。\n\n"
    "この台本は話速 {tempo} 倍を前提にしています。`pause_after` は次の値を基準に設計されて"
    "います（この基準からの逸脱が適切かどうかを、文脈に応じて判定してください）。\n"
    f"- 話者交代: {{speaker_change}}秒\n"
    f"- 文境界（同一話者の文の区切り）: {{sentence}}秒\n"
    f"- 章転換（シーンの最後、次のシーンへの境界）: {{chapter_transition}}秒\n"
    f"- 決め文（言い切り・強い反転・重い引用の直後）: {DECISIVE_LINE_TARGET}\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "次の3つのセクションを、この順で出力してください。\n\n"
    "### 「## 1. 間が足りない、または長すぎる箇所」\n"
    "Markdown の表（列: シーン・セグメント／現在値→推奨値／指摘・理由）。該当なしの場合は"
    "その旨を1行で。\n\n"
    "### 「## 2. 息継ぎが必要な長文（文を分けるべき箇所）」\n"
    "Markdown の表（列: シーン・セグメント／該当文／分割案（区切る位置））。該当なしの場合は"
    "その旨を1行で。\n\n"
    "### 「## 3. 話速{tempo}倍にしたときの間の推奨値」\n"
    "Markdown の表（列: 区分／現在値／推奨値／評価）。区分は「話者交代」「文境界（同一話者）」"
    "「決め文」「章転換」の4行にしてください。\n\n"
    "台本・YAML の書き換えはせず、指摘と推奨値の提示のみを行ってください。ファイルは編集しない"
    "でください。"
)


@dataclass
class NarrationSegment:
    seg_no: int  # シーン内の通し番号（1始まり）
    speaker: str
    text: str
    pause_after: float


@dataclass
class SceneInfo:
    scene_id: int
    title: str
    chapter_title: str | None
    segments: list[NarrationSegment]


# ============================================================
# YAML からシーン・セグメント抽出
# ============================================================


def extract_scenes(yaml_data: dict) -> list[SceneInfo]:
    scenes: list[SceneInfo] = []
    for sc in yaml_data.get("scenes", []):
        segments: list[NarrationSegment] = []
        for i, seg in enumerate(sc.get("narration", []), start=1):
            segments.append(
                NarrationSegment(
                    seg_no=i,
                    speaker=str(seg.get("speaker", "")),
                    text=str(seg.get("text", "")),
                    pause_after=float(seg.get("pause_after", 0.0)),
                )
            )
        if segments:
            scenes.append(
                SceneInfo(
                    scene_id=sc.get("id"),
                    title=str(sc.get("title", "")),
                    chapter_title=sc.get("chapter_title"),
                    segments=segments,
                )
            )
    return scenes


def build_prompt(video_title: str, scenes: list[SceneInfo], tempo: str) -> str:
    n_scenes = len(scenes)
    body_parts = []
    for idx, sc in enumerate(scenes):
        is_last_scene = idx == n_scenes - 1
        next_chapter = scenes[idx + 1].chapter_title if not is_last_scene else None
        heading = f"### シーン{sc.scene_id}/{n_scenes}: {sc.title}"
        if sc.chapter_title:
            heading += f"（このシーンの章タイトル: 「{sc.chapter_title}」）"
        lines = []
        n_segs = len(sc.segments)
        for seg in sc.segments:
            note = ""
            if seg.seg_no == n_segs:
                if is_last_scene:
                    note = "  ※動画全体の最終セグメント（終幕）"
                elif next_chapter:
                    note = f"  ※次シーンへの境界。次シーンの章タイトル: 「{next_chapter}」"
                else:
                    note = "  ※次シーンへの境界。次シーンに章カードなし"
            lines.append(
                f"{seg.seg_no}. {seg.speaker}: {seg.text}"
                f"（pause_after={seg.pause_after}秒）{note}"
            )
        body_parts.append(heading + "\n" + "\n".join(lines))
    segments_doc = "\n\n".join(body_parts)

    preset = PAUSE_PRESETS[tempo]
    header = PROMPT_HEADER_TEMPLATE.format(
        title=video_title,
        tempo=tempo,
        speaker_change=preset["speaker_change"],
        sentence=preset["sentence"],
        chapter_transition=preset["chapter_transition"],
    )
    return f"{header}\n\n---\n\n{segments_doc}\n"


# ============================================================
# 出力
# ============================================================


def default_out_path(yaml_path: Path, references_dir: Path) -> Path:
    folder_name = yaml_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-pause-review.md"


def build_output(
    video_title: str,
    yaml_path: Path,
    yaml_text: str,
    n_scenes: int,
    n_segments: int,
    tempo: str,
    response: str,
) -> str:
    sha = hashlib.sha256(yaml_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    preset = PAUSE_PRESETS[tempo]
    header = (
        f"# 「{video_title}」間・息継ぎレビュー（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"- 日時: {now}\n"
        f"- 対象 YAML: `{yaml_path}`（全{n_scenes}シーン・{n_segments}セグメント）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。カスタムプロンプトで実行。\n"
        f"- 前提: 話速 {tempo} 倍。`pause_after` の基準値（話者交代 {preset['speaker_change']}秒・"
        f"文境界 {preset['sentence']}秒・章転換 {preset['chapter_transition']}秒・決め文 "
        f"{DECISIVE_LINE_TARGET}）をプロンプトに明記した。\n\n"
        f"台本・YAML の書き換えは行わせていない（指摘・推奨値の提示のみ）。\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="対話台本のシーン YAML の pause_after を GPT（Codex CLI）に間の過不足・息継ぎ位置の観点でレビューさせる"
    )
    parser.add_argument("yaml_path", help="シーン YAML のパス")
    parser.add_argument(
        "--tempo",
        choices=["1.0", "1.1"],
        default="1.1",
        help="想定話速（既定 1.1。プロンプトに提示する pause_after の基準値が変わる）",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-pause-review.md）",
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

    yaml_path = Path(args.yaml_path)
    if not yaml_path.is_file():
        print(f"YAML ファイルが見つかりません: {yaml_path}", file=sys.stderr)
        return 1
    yaml_text = yaml_path.read_text(encoding="utf-8")
    yaml_data = yaml.safe_load(yaml_text)

    video_title = str((yaml_data.get("video") or {}).get("title") or yaml_path.stem)
    scenes = extract_scenes(yaml_data)
    if not scenes:
        print("シーン（scenes[].narration[]）が見つかりませんでした", file=sys.stderr)
        return 2
    n_segments = sum(len(sc.segments) for sc in scenes)
    print(f"{len(scenes)} シーン・{n_segments} セグメントを抽出しました（タイトル: {video_title}）")

    try:
        codex_exe = resolve_codex_exe(args.codex_path)
    except ReviewScriptError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    prompt_text = build_prompt(video_title, scenes, args.tempo)

    start = time.time()
    try:
        response = run_codex_review(prompt_text, codex_exe=codex_exe, timeout=args.timeout)
    except ReviewScriptError as exc:
        print(f"レビューに失敗しました: {exc}", file=sys.stderr)
        return 1
    elapsed = time.time() - start

    # tools/review/ から見て ../../references（draft-explanation-video/references）を既定にする。
    references_dir = Path(__file__).resolve().parents[2] / "references"
    out_path = Path(args.out) if args.out else default_out_path(yaml_path, references_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        build_output(
            video_title, yaml_path, yaml_text, len(scenes), n_segments, args.tempo, response
        ),
        encoding="utf-8",
    )

    n_table_lines = sum(1 for line in response.splitlines() if line.strip().startswith("|"))
    print(f"保存しました: {out_path}（表 {n_table_lines} 行、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
