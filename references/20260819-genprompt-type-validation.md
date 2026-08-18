# 検証メモ: 乖離型 gen_prompt の新しい型の有効性検証（A-5）

対象: `scripts/20260629-sns-lookism-acceptance.yaml` の生成イラスト用 `gen_prompt` のうち、
v5で構図が乖離した2例。新しい執筆規約（CLAUDE.md 素材候補収集ワークフロー節: 「人物主語＋
小道具＋一瞬のポーズ＋様式強制句」、before/after・二者比較は単一被写体に還元）が実際に
機能するかを、最も難しかった2例で検証した。

## 対象特定について

タスク依頼文の「scene4-2」という呼称に対応するシーン番号・cutaway番号は、現行 YAML には
存在しない（リポ内を検索したが該当なし）。内容の記述（「自分と有名人を見比べる」「左右の
人物で人種的特徴が異なる」）から、現行 YAML では下記に一致すると判断した。

- (a) **シーン5**（論証③）cutaways slot 1（`from`/`to`: 2）— Di Gestoら（2021）の内容を示す
  カットアウェイ。
- (b) **シーン4**（論証②）cutaways slot 2（`from`/`to`: 7）— 2024年フィルター研究のカットアウェイ。

## 旧 gen_prompt（v5, 乖離の原因）

```
(a) "a young woman comparing her own selfie with a celebrity's photo on a smartphone screen,
     thoughtful expression, full-bleed composition, subject fills the frame"

(b) "a smartphone screen showing a person's face before and after a beauty filter is applied,
     side-by-side comparison, full-bleed composition, subject fills the frame"
```

(a) は「自分」と「有名人」という**別人格の2人物**を暗に要求する構図で、生成モデルが左右の人物を
異なる人種的特徴で描いてしまうリスクが最優先案件として指摘されていた。(b) も
「before and after ... side-by-side」という**2枚の異なる生成結果の並置**を要求する構図で、
同一人物として一貫性が保証されない。

## 新 gen_prompt（今回の検証で書き直したもの）

`video.style`（YAML 共通）と `build_generation_prompt()` で連結した実際の送信プロンプト全文。

### (a) 1人称視点への還元

```
flat vector illustration, muted desaturated palette, limited color range, soft geometric
shapes, consistent line weight, calm editorial tone, no text, no lettering, no watermark,
generous negative space in the lower third. a first-person point-of-view shot of a hand
holding a smartphone, thumb scrolling a glamorous social media photo feed, warm screen glow
on fingers, single quiet frozen moment
```

「有名人と自分」という2人物の構図を捨て、**視点人物（POV）の手＋スマホという小道具**だけに
還元した。画面内に人物の顔を一切描かせないことで、人種的特徴の不一致リスクを構造的に排除する
狙い。

### (b) 単一被写体の顔を中央で分割

```
flat vector illustration, muted desaturated palette, limited color range, soft geometric
shapes, consistent line weight, calm editorial tone, no text, no lettering, no watermark,
generous negative space in the lower third. extreme close-up of a single young woman's face,
split exactly down the center by a thin vertical line, left half with a smooth glowing
beauty-filter effect, right half with natural skin texture, symmetric front-facing pose, one
continuous face
```

「before/after の2枚」ではなく、**1人の顔を中央線で分割し、片側だけにフィルター効果を
掛ける**という単一被写体の記述に還元した。

## 生成・検品結果

Stability AI（quality: core, $0.03/枚）で各1枚、計2枚生成。実際の課金額は**$0.06**
（予算上限どおり）。保存先: `C:\Users\shuya\Projects\script-to-video\build\r18-proto\`
（`case_a_celebrity_compare.png`, `case_b_filter_before_after.png`。使い捨てスクリプトも
同ディレクトリの `gen_a5_validation.py` に保存。`src/` は一切変更していない）。

### (a) 判定: 合格（構図・リスクとも改善、内容は一部弱まる）

- **様式適合**: 良好。フラットな配色・アイコン主体で、写実化していない。手の描写も
  ベクターイラスト的で崩れていない。
- **内容一致**: 部分的。「手でスマホを持ち画面を見る」構図には成功したが、画面内は
  Facebook/Twitter風のロゴと、輪郭が崩れた「Pのマーク」（Pinterest風だが正確な形になって
  いない、いわば幻覚気味のロゴ）を含むアイコンの集合になっており、「有名人の華やかな写真
  フィード」というビジュアル意図までは再現されていない（写真ではなくアイコンバッジの塊）。
  ナレーション単体で意味が通る補助情報としては機能するが、「容姿を比較する」というテーマ性は
  弱まっている。
- **含意リスク**: 解消。画面に人物の顔がまったく描かれないため、人種的特徴の不一致という
  最優先リスクは構造的になくなった。
- **新たに気づいた点（想定外の副作用）**: 実在ブランドのロゴ（Facebook の "f"、Twitter の
  鳥アイコン）がそのまま生成されている。商用動画で実在の商標ロゴをそのまま使うのは別種の
  リスク（商標・ブランドガイドライン）になりうるため、採用時は要確認（プロンプトに
  "generic app icons, no real brand logos" のような否定指定を足すと避けられる可能性が高い）。

### (b) 判定: 不合格（様式が崩れ、内容も意図通りに再現されなかった）

- **様式適合**: **NG**。生成結果はほぼ写実的なポートレート写真（肌の質感・自然光・
  被写界深度のある実写調）で、「flat vector illustration」の指定が効いていない。
  `video.style` を先頭に連結しているにもかかわらず、"extreme close-up of a...face"
  "natural skin texture" 等の内容記述側の語が写実表現を強く引っ張ったとみられる。
- **内容一致**: **NG**。「中央線で分割し、片側だけフィルター効果」という指示は再現されず、
  代わりに両目の下に対称な白い曲線が2本描かれただけで、左右の質感差（フィルター前後の対比）
  は表現されていない。before/after という論点が画面から読み取れない。
- **含意リスク**: 部分的に改善。単一の連続した顔として生成されたため、「左右で人種的特徴が
  異なる」という当初の最優先リスクは再現されなかった（1人物として一貫）。ただし、実写調の
  「理想化された容姿（整った目鼻立ち・染み一つない肌）」の女性像がそのまま出ており、
  ルッキズムを批判的に扱う動画の主張とトーンが噛み合わない見え方になるリスクは残る
  （新規に気づいた副作用。当初の判定基準にはなかった観点）。

## 結論: 型は「機能する」が、ケースに依存する

- **二者比較（別人物どうしの比較）を1人称視点・小道具中心の構図に還元する**というルール
  （ケースa）は、想定通り機能した。人物の顔を画面から排除できる構図に落とし込めれば、
  人種的特徴の不一致リスクは構造的に消せる。ただし、視覚的な情報量（何を見せたいか）が
  弱まるトレードオフがあり、「アイコンの塊」のような抽象化しすぎた結果になりやすい点は
  今後の書き方の注意点。
- **before/after を単一被写体の一瞬（顔の中央分割）に還元する**というルール（ケースb）は、
  含意リスク（人種不一致）は解消したものの、**様式適合（flat illustration の維持）に
  失敗した**。単独の顔を extreme close-up で写実的に記述すると、スタイルプレフィックスが
  あってもモデルは実写ポートレートに寄る傾向がある。今回の検証で分かった実践的な教訓は、
  「単一被写体への還元」だけでは様式崩れを防げず、**むしろケースaと同じ「小道具＋POV」の
  還元パターン**（例: 顔そのものではなく、スマホ画面のフィルター切り替えUIを操作する手、
  という構図）の方が、様式・内容一致・含意リスクの3点をまとめて満たしやすい可能性が高い。
  before/after 系は「顔のクローズアップの記述」自体を避けるのが安全、というのが今回の
  暫定的な追加知見。
- 総合結論: 新しい執筆規約（人物主語＋小道具＋一瞬のポーズ＋様式強制句、二者比較は単一被写体
  へ還元）は**方向性としては正しく機能する**が、「単一被写体」の中身が「顔のクローズアップ」
  になると様式崩れのリスクが残る。ルールに一文足すなら、「二者比較・before/afterは、
  可能な限り顔のクローズアップではなく、小道具の操作（POV・手・UI要素）に還元する」を
  推奨する。

## 実際の課金額

$0.06（Stability AI core品質、$0.03 × 2枚）。追加生成はしていない。
