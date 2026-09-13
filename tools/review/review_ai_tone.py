"""台本（対話台本・ナレーション台本の両方に対応）を、別モデル（GPT。Codex CLI 経由）に
「AI らしさ（セリフが文書になっていないか）」の観点でレビューさせるツール。

ユーザー指摘（2026-09-13）: 「AI 独特の表現でスッと入ってこない」箇所があるが、既存のレビュー
（`review_dialogue.py` のセリフの自然さ・キャラらしさ等）ではこれを拾えなかった。既存観点は
「セリフとして自然か」「キャラらしいか」を見ており、「話者が台本の構成・規則をそのまま台詞に
してしまっている」「対句・唱和・読点刻みなど、生成モデル特有の文の型になっている」かは見ていない。

判定軸は一つ: **「その台詞が更新するのは『状況』か『文書』か」**（出来事・数字・判断を進めるなら
状況＝残す。台本の構成・規則・予告を語るなら文書＝削る）。k16shikano「認知リズムを生むための
日本語ライティング規範」の「装置は実現するものであって、宣言するものではない」を参考にした。

`review_clarity.py`（対話台本・ナレーション台本の両対応。自動判別）を雛形にし、codex exec 呼び出し
（`review_script.py` から import）・対話台本の抽出（`review_dialogue.py` から import）・
ナレーション台本の抽出（`review_script.py` から import）をそのまま流用する。キャラクター設定は
`review_transitions.py` と同じく、特定動画の題材に依存しない汎用版を使う。**台本の文言はこの
ツールでは一切編集しない**（指摘の生成のみ）。採否判断と反映は人／Claude が行う。

## 対象とする台本の書式（対話台本・ナレーション台本の両方に対応）

- **対話台本**（`**話者**（表情）: 本文` 行がある）: `review_dialogue.py` と同じ
  `extract_scenes_with_lines` で発話を抽出し、行単位でレビューさせる。
- **ナレーション台本**（`**話者**（表情）: 本文` 行が無く、`**ナレーション**` ブロックがある）:
  `review_script.py` と同じ `extract_scenes` でシーンごとのナレーション全文を抽出する。

いずれも `## 出典リスト` / `## 付録` 以降は対象外（各抽出関数がすでに除外する）。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_ai_tone.py scripts/20260913-comparison-kamishibai/20260913-comparison-kamishibai.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-ai-tone-review.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 台本全文＋観点9つを渡すため出力が長くなりやすい。「usage limit」「at capacity」等の
  クォータ超過で失敗することがあり、その場合は60秒待って1回だけ再試行する。
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from datetime import datetime
from pathlib import Path

# review_dialogue.py / review_script.py と同じディレクトリにあるため、そのまま import して
# 再利用する（対話台本の抽出・タイトル抽出・codex exec 呼び出し）。
from review_dialogue import (
    DIALOGUE_LINE_RE,
    extract_scenes_with_lines,
    extract_title,
)
from review_script import (
    DEFAULT_TIMEOUT_S,
    ReviewScriptError,
    extract_scenes as extract_narration_scenes,
    resolve_codex_exe,
    run_codex_review,
)

# ============================================================
# 定数
# ============================================================

# review_dialogue.py の CHARACTER_PROFILE は「ドパガキ」動画向けの題材依存の一文を含むため
# 流用しない（review_transitions.py と同じ理由）。ここでは題材によらない汎用版を定義する。
CHARACTER_PROFILE = (
    "- **ずんだもん**（聞き手）: 語尾は「〜のだ」「〜なのだ」。無邪気・素直・時々ボケる。"
    "疑問・驚き・言い換え・ツッコミ・（テーマによっては当事者としての反応）で掛け合いの節目を"
    "作る。\n"
    "- **四国めたん**（解説役）: 落ち着いた丁寧語に少しお嬢様の余裕（「〜のよ」「〜かしら」。"
    "「〜ですわ」は多用しない）。ずんだもんに向かって話しかける口調で、講義調にはならない。"
)

JUDGE_AXIS = (
    "この観点でのレビューは、判定軸を一つに絞ります。**「その台詞が更新するのは『状況』か"
    "『文書』か」**。出来事・数字・判断を前に進める台詞は「状況」を更新しており自然です。"
    "台本の構成・規則・これから話す予告・レビュー基準そのものを語っている台詞は「文書」を"
    "更新しており、AI が台本を書いていることが透けて見える不自然な台詞です（参考: "
    "k16shikano「認知リズムを生むための日本語ライティング規範」の「装置は実現するものであって、"
    "宣言するものではない」）。"
)

OBSERVATION_POINTS = (
    "1. **骨組みの実況**: 「先に答えだけ言っておくわ」「思い込みが三つひっくり返るわ」"
    "「一つ目／二つ目」「ここから先は私の推論ね」「限定をつけておくわ」「注意しておくわ」の"
    "ように、構成・章の予告・レビュー規則を台詞で宣言している行を列挙してください。\n"
    "2. **規則語彙の漏出**: 「決め文」「限定」「推論」「予告」「前提」「三つ」「定義」など、"
    "台本作りの語彙がそのまま台詞に出ている行を列挙してください。\n"
    "3. **対句・決め台詞**: 「〜じゃない。〜よ」「〜を、〜に変える」「〜は見える。でも〜は"
    "見えない」のような、コピー調・標語調の締めになっている行を列挙し、普段の口調での"
    "言い直し案を出してください。\n"
    "4. **読点刻みと語尾置き**: 「何と比べたか、よ」「壊れているのは二つ。『〜』と、『〜』"
    "よ」のように、読点で刻んで語尾だけ置く型になっている行を列挙し、2文に分けて自然に言う"
    "案を出してください。\n"
    "5. **名詞句の唱和**: 同じ名詞句（例: 「誰と比べるか」「相手の何を見るか」）を、章を"
    "またいで台詞で繰り返している箇所を列挙してください。ただし章の入口・結びで現在地を"
    "示す1回は許容してください。それ以外の箇所は、場面の言い方に崩す案を出してください。\n"
    "6. **要約だけの相づち**: ずんだもんの返しが、主語のない要約になっている行（例:"
    "「相手を選べなくて、相手のいい瞬間しか見えない。」）を列挙してください。要約自体は"
    "禁止しませんが、「僕」を主語にした当事者の言い方（例:「じゃあ僕、流れてきた人のいい"
    "ところだけ見て落ち込んでたのだ？」）に直す案を出してください。加えて、要約・問い・"
    "感想・具体例・早合点のいずれかの型が3回続けて同じ型になっている箇所があれば"
    "指摘してください。\n"
    "7. **理論名の先出し**: 「1954年、アメリカの心理学者〜が」のように、違和感や場面より"
    "先に固有名詞・年・理論名から入る行を列挙し、場面を先に置く順序案を出してください。\n"
    "8. **息継ぎの欠如**: 1シーンの中で、言い淀み・言い直し・軽い脱線が一つもなく、全行が"
    "主張の文になっている場合にそのシーンを指摘し、どこに息継ぎを入れられるかを提案して"
    "ください。\n"
    "9. **拍**: めたんの長い断定文が3行以上連続している箇所を列挙し、短い断定→長い説明→"
    "短い止め、の順に組み替える案を出してください。"
)

OUTPUT_FORMAT_COMMON = (
    "各観点の指摘には、必ず「該当行の引用・種別・理由・言い直し案」を含めてください。"
    "言い直し案は、めたんの口癖「〜のよ」「〜わ」、ずんだもんの口癖「〜のだ」「僕」を"
    "保ってください。事実・数値・固有名詞は変えないこと。\n\n"
    "最後に次の2点を出力してください。\n"
    "- 「## 最優先で直すべき5点」: 上記9観点を横断して優先度順に5件。\n"
    "- 「## このレビューが誤検出しやすい点」: 口癖（「〜のよ」「〜のだ」）自体は対象外で"
    "あること、板・章カードの文言（画面指示側）は対象外であることを明記した上で、"
    "他にも誤検出しやすい観点があれば追記してください。\n\n"
    "台本の書き換えはせず、指摘と言い直し案の提示のみを行ってください。ファイルは編集"
    "しないでください。"
)

DIALOGUE_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画の台本を、**AI らしさ（セリフが文書になっていないか）**という"
    "観点でレビューする担当者です。対象は「{title}」。四国めたん（VOICEVOX、解説役）と"
    "ずんだもん（VOICEVOX、聞き手）の二人による対話劇で、絵は紙芝居風（緑の黒板・木枠の額縁・"
    "棒付きの紙人形）です。視聴者は一般層で、専門知識は仮定しません。\n\n"
    f"{JUDGE_AXIS}\n\n"
    "## キャラクター設定\n"
    f"{CHARACTER_PROFILE}\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "観点ごとに「## 1. 骨組みの実況」〜「## 9. 拍」の見出しを立て、表（列: シーン／行／"
    "話者／該当セリフ（短く引用）／種別／理由／言い直し案）で出力してください。該当なしの"
    "観点は「該当なし」と1行で書いてください。\n\n"
    f"{OUTPUT_FORMAT_COMMON}"
)

NARRATION_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画（機械音声ナレーション）の台本を、**AI らしさ（語りが文書に"
    "なっていないか）**という観点でレビューする担当者です。対象は「{title}」。視聴者は"
    "一般層で、専門知識は仮定しません。一人語りのナレーション台本のため、キャラクター設定・"
    "掛け合い関連の観点（5.名詞句の唱和の章またぎ判定、6.要約だけの相づち、9.拍の話者間の"
    "リズム）は「話者」欄を単一のナレーターとして読み替え、該当がなければ「該当なし」と"
    "してください。\n\n"
    f"{JUDGE_AXIS}\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "観点ごとに「## 1. 骨組みの実況」〜「## 9. 拍」の見出しを立て、表（列: シーン／"
    "該当文（短く引用）／種別／理由／言い直し案）で出力してください。該当なしの観点は"
    "「該当なし」と1行で書いてください。\n\n"
    f"{OUTPUT_FORMAT_COMMON}"
)


# ============================================================
# 台本 md からの抽出・プロンプト組み立て（対話台本 / ナレーション台本）
# ============================================================


def is_dialogue_script(md_text: str) -> bool:
    """`**話者**（表情）: 本文` 行が1つでもあれば対話台本と判定する。"""

    return DIALOGUE_LINE_RE.search(md_text) is not None


def build_dialogue_prompt(
    video_title: str, scenes: list[tuple[str, list[tuple[int, str, str, str]]]]
) -> str:
    body_parts = []
    for scene_title, lines in scenes:
        line_texts = [
            f"{line_no}. {speaker}（{expression}）: {text}"
            for line_no, speaker, expression, text in lines
        ]
        body_parts.append(f"### {scene_title}\n" + "\n".join(line_texts))
    dialogue_doc = "\n\n".join(body_parts)
    header = DIALOGUE_HEADER_TEMPLATE.format(title=video_title)
    return f"{header}\n\n---\n\n{dialogue_doc}\n"


def build_narration_prompt(video_title: str, scenes: list[tuple[str, str]]) -> str:
    body_parts = [f"### {title}\n{narration}" for title, narration in scenes]
    narration_doc = "\n\n".join(body_parts)
    header = NARRATION_HEADER_TEMPLATE.format(title=video_title)
    return f"{header}\n\n---\n\n{narration_doc}\n"


# ============================================================
# 出力
# ============================================================


def default_out_path(md_path: Path, references_dir: Path) -> Path:
    folder_name = md_path.parent.name
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{folder_name}-ai-tone-review.md"


def build_output(
    video_title: str,
    md_path: Path,
    md_text: str,
    mode: str,
    n_scenes: int,
    n_units: int,
    response: str,
) -> str:
    sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode_label = "対話台本（発話単位）" if mode == "dialogue" else "ナレーション台本（シーン単位）"
    unit_label = "発話" if mode == "dialogue" else "シーン"
    header = (
        f"# 「{video_title}」AI らしさレビュー（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"「その台詞が更新するのは『状況』か『文書』か」を判定軸に、骨組みの実況・規則語彙の"
        f"漏出・対句決め台詞・読点刻みと語尾置き・名詞句の唱和・要約だけの相づち・理論名の"
        f"先出し・息継ぎの欠如・拍の9観点でレビュー。Codex CLI（GPT）経由。\n\n"
        f"- 日時: {now}\n"
        f"- 対象台本: `{md_path}`（{mode_label}、全{n_scenes}シーン・{n_units}{unit_label}）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。カスタムプロンプトで実行。\n"
        f"- 依頼した観点: 1.骨組みの実況 2.規則語彙の漏出 3.対句・決め台詞 4.読点刻みと"
        f"語尾置き 5.名詞句の唱和 6.要約だけの相づち 7.理論名の先出し 8.息継ぎの欠如 9.拍\n\n"
        f"台本の書き換えは行わせていない（指摘・言い直し案の提示のみ）。\n\n"
        f"---\n\n"
    )
    return header + response + "\n"


# ============================================================
# CLI
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "台本（対話台本・ナレーション台本の両方に対応）を GPT（Codex CLI）に"
            "「AI らしさ（セリフが文書になっていないか）」の観点（骨組みの実況・規則語彙の"
            "漏出・対句決め台詞・読点刻み・名詞句の唱和・要約だけの相づち・理論名の先出し・"
            "息継ぎの欠如・拍）でレビューさせる"
        )
    )
    parser.add_argument("md_path", help="台本 Markdown のパス")
    parser.add_argument(
        "--out",
        default=None,
        help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-ai-tone-review.md）",
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

    if is_dialogue_script(md_text):
        mode = "dialogue"
        dialogue_scenes = extract_scenes_with_lines(md_text)
        if not dialogue_scenes:
            print(
                "シーン（## シーンN + **話者**（表情）: 本文 形式の発話）が見つかりませんでした",
                file=sys.stderr,
            )
            return 2
        n_scenes = len(dialogue_scenes)
        n_units = sum(len(lines) for _, lines in dialogue_scenes)
        prompt_text = build_dialogue_prompt(video_title, dialogue_scenes)
    else:
        mode = "narration"
        narration_scenes = extract_narration_scenes(md_text)
        if not narration_scenes:
            print(
                "シーン（## シーンN + **ナレーション** ブロック形式）が見つかりませんでした",
                file=sys.stderr,
            )
            return 2
        n_scenes = len(narration_scenes)
        n_units = n_scenes
        prompt_text = build_narration_prompt(video_title, narration_scenes)

    print(f"{n_scenes} シーン（{mode}）を抽出しました（タイトル: {video_title}）")

    try:
        codex_exe = resolve_codex_exe(args.codex_path)
    except ReviewScriptError as exc:
        print(str(exc), file=sys.stderr)
        return 1

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
        build_output(video_title, md_path, md_text, mode, n_scenes, n_units, response),
        encoding="utf-8",
    )

    n_table_lines = sum(1 for line in response.splitlines() if line.strip().startswith("|"))
    print(f"保存しました: {out_path}（表 {n_table_lines} 行、所要 {elapsed:.0f}秒）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
