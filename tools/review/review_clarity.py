"""台本（対話台本・ナレーション台本の両方に対応）を、別モデル（GPT。Codex CLI 経由）に
「視聴者の理解と主題への適合」の観点でレビューさせるツール。

冷笑ずんだもん版（2026-09-05〜06）で、既存の5種のレビュー（`review_script.py` の7観点・
`review_holistic.py` の総合・`review_dialogue.py` のセリフ・`review_transitions.py` の
つなぎ・`review_pauses.py` の間）を全部通した台本に、ユーザーの試写で次のような指摘が出て、
5版分の手戻りになった（2026-09-06）。
- 意味が取れない一文（引用「それが欺瞞だと知っている。それでも、そうする」、聞き手の問い
  「みんな同じ人に向かうことがあるのだ？」）
- 説明の抜け（「意識が高い人がなぜ『冷たい』側に置かれるのか」）
- 主題に寄与しない逸話（ディオゲネスのランプ・甕・大王）が3分残っていた
- 婉曲・比喩の決め文（「請求書」「犬は権力に吠え…」）が直接表現より分かりにくい
- 具体例の選び方が論と噛み合わない（海岸清掃の「意識高い」→本来は「本気の人を笑う」例が必要）

既存レビューは「表現として自然か」を見ていて、「視聴者がこの一文を聞いて理解できるか」
「この段落は主題にどう寄与するか」を見ていなかった。本ツールはその隙間を埋める
（`docs/dialogue-guide.md` §4b 直接表現・逸話より主題、§5 反転の否定範囲、を踏まえる）。

2026-09-12、ユーザー指示で観点5「冗長・婉曲（表現）」・観点6「構成の切れ味（議論）」を
追加した。「結論がスッと入ってくるのが面白い解説動画」という基準に対し、既存4観点は
一文単位の理解可能性と段落単位の主題適合は見ていたが、①回りくどい言い回し・抽象語で
済ませている表現、②結論到達の最短経路として構成が無駄なく組まれているか、は見ていな
かった。観点5は各指摘に「元の文 → 簡潔な言い換え案」、観点6は各指摘に
「削る／前に出す／一文にまとめる」の処方を必須で添えさせる。

`review_dialogue.py` / `review_transitions.py` を雛形にし、codex exec 呼び出し
（`review_script.py` から import）・出力保存の構造をそのまま流用する。**台本の文言は
このツールでは一切編集しない**（指摘の生成のみ）。採否判断と反映は人／Claude が行う。

## 対象とする台本の書式（対話台本・ナレーション台本の両方に対応）

- **対話台本**（`**話者**（表情）: 本文` 行がある）: `review_dialogue.py` と同じ
  `extract_scenes_with_lines` で発話を抽出し、行単位でレビューさせる。
- **ナレーション台本**（`**話者**（表情）: 本文` 行が無く、`**ナレーション**` ブロックがある）:
  `review_script.py` と同じ `extract_scenes` でシーンごとのナレーション全文を抽出する。

いずれも `## 出典リスト` / `## 付録` 以降は対象外（各抽出関数がすでに除外する）。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_clarity.py scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.md

出力は既定で `references/{実行日 YYYYMMDD}-{台本フォルダ名}-clarity-review.md`。

## 前提

- Codex CLI（`codex`/`codex.bat`）にログイン済みであること（`codex login status`）。
- 台本全文＋観点6つを渡すため出力が長くなりやすい。「usage limit」「at capacity」等の
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

OBSERVATION_POINTS = (
    "1. **理解度（一文ごと）**: 初見の一般視聴者が、その一文を音声で一度聞いただけで意味を"
    "取れるかを判定してください。意味が取れない文、二重の意味に読める文、指示語（「それ」"
    "「その」等）の指す先が曖昧な文、引用（「」で囲まれた言葉）で意味が閉じていない文"
    "（引用だけでは何を言っているか分からない文）を列挙し、「何が分からないか」と"
    "言い直し案を示してください。事実・数値・固有名詞は変えないこと。\n"
    "2. **説明の抜け**: 主張と主張の間に飛躍がないかを判定してください。「なぜそうなるのか」"
    "が説明されないまま次の話に進んでいる箇所（例: 分類・区分の理由が示されない、"
    "因果の理由が示されない、反転の主張が何を否定して何を否定していないか曖昧なまま）を"
    "列挙し、補うべき説明の要点を示してください。\n"
    "3. **主題への適合**: この台本のタイトル（冒頭の問い）に対して、各シーン・各段落が"
    "どう寄与するかを1行で述べてください。寄与が薄い、または寄与しないと判断した段落・"
    "逸話・具体例は削除候補として、その分量の目安（文字数）とともに列挙してください。"
    "加えて、冒頭で提示される具体例が、中盤以降の論（根拠・実験・結論）と同じ型の対象"
    "（同じ主語・同じ立場の人物像）を指しているかどうかも判定してください（型が違う場合、"
    "冒頭の例をどう差し替えるべきかの方向性も示してください）。\n"
    "4. **直接表現**: 比喩・婉曲・対句になっている決め文・キーフレーズを列挙し、比喩を使わず"
    "直接に言い直した案を添えてください。言い直した方が分かりやすい場合はそう明記し、逆に"
    "「この比喩は直接表現より分かりやすい／効果的」と判断した場合は、その理由とともに"
    "そう書いてください（機械的にすべての比喩を悪いと判定しないこと）。\n"
    "5. **冗長・婉曲（表現）**: 4.で扱う決め文・キーフレーズ以外の一般的な文を対象に、"
    "回りくどい言い回し、比喩・婉曲で言い換えている箇所、同じ内容を言葉を変えて二度"
    "言っている箇所、抽象語（「効く」「向かう」「用意する」「機能する」等）で済ませていて"
    "具体的な語に直せる箇所を列挙してください。各指摘には必ず「元の文 → 簡潔な言い換え案」"
    "を示してください（4.の決め文と重複させないこと）。\n"
    "6. **構成の切れ味（議論）**: 台本全体を、論証としての最短経路という観点で判定して"
    "ください。結論（タイトルの問いへの答え）が最初に示唆されるのはどのシーンか、後半に"
    "置かれた結論的な主張は前に出せないか、章の順序が論証として最短か（入れ替えても・"
    "無くしても結論が変わらない章・段落・研究紹介はどれか。3.主題への適合とは異なり、"
    "ここでは「主題には触れているが議論の主軸から外れた回り道になっている」かどうかを"
    "見ること）を判定してください。対話台本の場合は、聞き手の相づち・聞き返し・言い直しの"
    "要求で議論が足踏みしている箇所（結論に近づかないやり取り）も列挙してください"
    "（ナレーション台本の場合、この対話の下位項目は該当なしとしてください）。各指摘には"
    "「削る」「前に出す」「一文にまとめる」のいずれかの処方を付けてください。"
)

DIALOGUE_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画の台本を、**視聴者の理解と主題への適合**という観点で"
    "レビューする担当者です。対象は「{title}」。四国めたん（VOICEVOX、解説役）とずんだもん"
    "（VOICEVOX、聞き手）の二人による対話劇で、絵は紙芝居風（緑の黒板・木枠の額縁・棒付きの"
    "紙人形）です。視聴者は一般層で、専門知識は仮定しません。ナレーションは音声のみで流れ、"
    "視聴者は聞き逃したら聞き返せません（字幕はあるが、一度画面から消える前提で判定してください）。\n\n"
    "この観点でのレビューは、**「セリフとして自然か」ではなく「視聴者がその一文を聞いて"
    "理解できるか」「その段落・その逸話が、動画の主題（タイトルの問い）にどう寄与するか」"
    "を見る**ものです。セリフの自然さ・キャラらしさ・表情タグは別のレビューで扱うため、"
    "本レビューでは対象にしないでください（冗長・婉曲な言い回しと構成の切れ味は5.・6.で"
    "扱うため対象に含めます）。\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "次の6セクションを、この順で Markdown で出力してください。\n"
    "- 「## 1. 理解度」: 表（列: シーン／行／話者／該当セリフ（短く引用）／分からない点／"
    "言い直し案）。\n"
    "- 「## 2. 説明の抜け」: 表（列: シーン／箇所（行番号や該当セリフの引用）／飛躍の内容／"
    "補うべき説明）。\n"
    "- 「## 3. 主題への適合」: まず各シーンの寄与を1行ずつ列挙し（表: 列 シーン／タイトル"
    "への寄与（1行）／判定（寄与する・薄い・寄与しない）／削除候補の場合の目安文字数）、"
    "続けて「### 冒頭の具体例と後半の論の型の一致」として判定結果を記述してください。\n"
    "- 「## 4. 直接表現」: 表（列: シーン／行／該当表現（比喩・婉曲・対句）／直接に言い直した"
    "案／コメント（比喩の方が良い場合はその理由））。\n"
    "- 「## 5. 冗長・婉曲（表現）」: 表（列: シーン／行／元の文／分類（回りくどい・比喩婉曲・"
    "二度言い・抽象語）／簡潔な言い換え案）。\n"
    "- 「## 6. 構成の切れ味（議論）」: まず表（列: 箇所（シーン・行）／問題（回り道・結論の"
    "遅さ・冗長な章・対話の足踏み）／処方（削る・前に出す・一文にまとめる）／理由）で列挙し、"
    "続けて「### 結論が最初に示唆されるシーン」と「### 削っても結論が変わらない章・段落」を"
    "1〜2行ずつ記述してください。\n\n"
    "最後に「## 最優先で直すべき5点」として、上記6観点を横断して優先度順に5件挙げて"
    "ください。\n\n"
    "台本の書き換えはせず、指摘と言い直し案の提示のみを行ってください。ファイルは編集"
    "しないでください。"
)

NARRATION_HEADER_TEMPLATE = (
    "あなたは YouTube 解説動画（機械音声ナレーション）の台本を、**視聴者の理解と主題への"
    "適合**という観点でレビューする担当者です。対象は「{title}」。視聴者は一般層で、"
    "専門知識は仮定しません。ナレーションは音声のみで流れ、視聴者は聞き逃したら聞き返せません"
    "（字幕はあるが、一度画面から消える前提で判定してください）。\n\n"
    "この観点でのレビューは、**「文章として自然か」ではなく「視聴者がその一文を聞いて理解"
    "できるか」「その段落・その逸話が、動画の主題（タイトルの問い）にどう寄与するか」を見る**"
    "ものです。用語の初出順・同構文の反復等の文章レベルのチェックは別のレビューで扱うため、"
    "本レビューでは対象にしないでください（冗長・婉曲な言い回しと構成の切れ味は5.・6.で"
    "扱うため対象に含めます）。\n\n"
    "## レビュー観点\n"
    f"{OBSERVATION_POINTS}\n\n"
    "## 出力形式\n"
    "次の6セクションを、この順で Markdown で出力してください。\n"
    "- 「## 1. 理解度」: 表（列: シーン／該当文（短く引用）／分からない点／言い直し案）。\n"
    "- 「## 2. 説明の抜け」: 表（列: シーン／該当箇所（引用）／飛躍の内容／補うべき説明）。\n"
    "- 「## 3. 主題への適合」: まず各シーンの寄与を1行ずつ列挙し（表: 列 シーン／タイトル"
    "への寄与（1行）／判定（寄与する・薄い・寄与しない）／削除候補の場合の目安文字数）、"
    "続けて「### 冒頭の具体例と後半の論の型の一致」として判定結果を記述してください。\n"
    "- 「## 4. 直接表現」: 表（列: シーン／該当表現（比喩・婉曲・対句）／直接に言い直した"
    "案／コメント（比喩の方が良い場合はその理由））。\n"
    "- 「## 5. 冗長・婉曲（表現）」: 表（列: シーン／元の文／分類（回りくどい・比喩婉曲・"
    "二度言い・抽象語）／簡潔な言い換え案）。\n"
    "- 「## 6. 構成の切れ味（議論）」: まず表（列: 箇所（シーン）／問題（回り道・結論の遅さ・"
    "冗長な章）／処方（削る・前に出す・一文にまとめる）／理由）で列挙し、続けて"
    "「### 結論が最初に示唆されるシーン」と「### 削っても結論が変わらない章・段落」を"
    "1〜2行ずつ記述してください。\n\n"
    "最後に「## 最優先で直すべき5点」として、上記6観点を横断して優先度順に5件挙げて"
    "ください。\n\n"
    "台本の書き換えはせず、指摘と言い直し案の提示のみを行ってください。ファイルは編集"
    "しないでください。"
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
    return references_dir / f"{today}-{folder_name}-clarity-review.md"


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
        f"# 「{video_title}」視聴者理解・主題適合レビュー（GPT、{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        f"理解度（一文ごと）・説明の抜け・主題への適合・直接表現・冗長婉曲・構成の切れ味の"
        f"6観点でレビュー。Codex CLI（GPT）経由。\n\n"
        f"- 日時: {now}\n"
        f"- 対象台本: `{md_path}`（{mode_label}、全{n_scenes}シーン・{n_units}{unit_label}）\n"
        f"- 入力SHA256（先頭8桁）: {sha}\n"
        f"- 呼び出し方式: `tools/review/review_script.py` と同じ codex exec 呼び出し"
        f"（`--sandbox read-only --skip-git-repo-check`、stdin にプロンプト、`-o` で応答ファイル"
        f"出力）。カスタムプロンプトで実行。\n"
        f"- 依頼した観点: 1.理解度（一文ごと） 2.説明の抜け 3.主題への適合 4.直接表現 "
        f"5.冗長・婉曲（表現） 6.構成の切れ味（議論）\n\n"
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
            "「視聴者の理解と主題への適合」の観点（理解度・説明の抜け・主題への適合・"
            "直接表現・冗長婉曲・構成の切れ味）でレビューさせる"
        )
    )
    parser.add_argument("md_path", help="台本 Markdown のパス")
    parser.add_argument(
        "--out",
        default=None,
        help="出力先パス（既定: references/{実行日}-{台本フォルダ名}-clarity-review.md）",
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

    print(
        f"{n_scenes} シーン（{mode}）を抽出しました（タイトル: {video_title}）"
    )

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
