# 調査メモ: 容姿の賃金プレミアム — chart 用数値の裏取り（A-6）

対象: `scripts/20260629-sns-lookism-acceptance.yaml` シーン4（論証②）の `diagram.type: chart`
候補データ。1本だけ入れる「裏取り済み数値の chart」の元ネタとして検証した。

## 結論（要約）

**一次資料で確定できた。** Hamermesh & Biddle (1994) の Table 6（Pooled Estimates）の数値を
そのまま bar chart 化できる。台本の既存ナレーション文言（「賃金が最大で十数パーセント高く」）は
この一次資料の数値と整合しない箇所があるため、要修正として別途フラグを立てた（後述）。

## 一次資料

- Hamermesh, D. S., & Biddle, J. E. (1994). "Beauty and the Labor Market." *American Economic
  Review*, 84(5), 1174–1194.
- 著者公式の再録（NBER Working Paper No. 4518, 1993, 同一著者による配布版）:
  https://www.nber.org/papers/w4518 / PDF: https://www.nber.org/system/files/working_papers/w4518/w4518.pdf
- Abstract（NBER / AEA=ideas.repec.org 双方で同一文言を確認）:
  > "Plain people earn less than average-looking people, who earn less than the good-looking.
  > The plainness penalty is 5 to 10 percent, slightly larger than the beauty premium. Effects
  > for men are at least as great as for women..."

### 裏取りの経緯（手法のメモ）

- NBER の PDF は画像スキャン（JBIG2）で、本環境には `pdftoppm`（poppler）も Python の PDF
  ライブラリ（`fitz` / `pypdf` / `pdfplumber`）も無く、Read ツール・WebFetch の標準経路では
  本文を読めなかった。
- テキスト抽出プロキシ（`https://r.jina.ai/<NBER PDFのURL>`）経由で同じ NBER 公式 PDF を
  再取得し、本文のテキスト化に成功した。**フェッチ先は変わらずNBER公式PDFそのもの**であり、
  プロキシは抽出手段に過ぎない。
- ハルシネーション対策として、同じ表を独立した2回の問い（(1)「abstract の 5-10% の根拠になる
  表は？」(2)「Table 6 を表としてそのまま書き出して」）で取得し、数値が完全一致することを
  確認した（Table 6 は論文（NBER WP版）18ページに掲載）。

## Table 6（Pooled Estimates）の数値

賃金の対数を被説明変数とする回帰の係数（他の人的資本・労働市場属性を統制済み）。カッコ内は標準誤差。

| | 容姿が平均以下（ペナルティ） | 容姿が平均以上（プレミアム） |
|---|---|---|
| 男性（3サンプル併合） | −0.091 (0.031) | +0.053 (0.019) |
| 女性（3サンプル併合） | −0.054 (0.038) | +0.038 (0.022) |
| 男女計（3サンプル併合） | −0.072 (0.024) | +0.048 (0.015) |

対数係数を実際のパーセント効果に変換（`(e^b − 1) × 100`。小さい係数では単純に×100してもほぼ同じ値になるが、正確を期して指数変換した）:

| | 容姿が平均以下 | 容姿が平均以上 |
|---|---|---|
| 男性 | **−8.7%** | **+5.4%** |
| 女性 | **−5.3%** | **+3.9%** |
| 男女計 | **−6.9%** | **+4.9%** |

Abstract の「plainness penalty 5 to 10 percent」は、この表（特に男性 −8.7%／男女計 −6.9%）と
整合する。

## chart 化の推奨形

**推奨: bar・1系列・3点**（`docs/schema.md` の `chart` 節にある例と同じ構成。男女を分けず
「男女計」の数値を使い、平均を0とする3点で見せるのがナレーションとの対応も取りやすい）。

```yaml
diagram:
  type: chart
  chart: bar
  title: 容姿による賃金プレミアム
  unit: "%"
  source: "Hamermesh & Biddle (1994) American Economic Review 84(5), Table 6"
  series:
    - color: accent
      at: 3
      points:
        - {label: 容姿低い, value: -6.9}
        - {label: 平均,     value: 0.0}
        - {label: 容姿高い, value: 4.9}
```

**代替案（男女別・4点）**: 「効果は男性の方が女性と同等かそれ以上」という論文の指摘まで見せたい
場合は、平均以下／平均以上 × 男女の4点にできる（ラベルは8文字以内の制約内）。

```yaml
        - {label: 男性・低い, value: -8.7}
        - {label: 男性・高い, value: 5.4}
        - {label: 女性・低い, value: -5.3}
        - {label: 女性・高い, value: 3.9}
```

どちらも `bar` の上限（1系列・3〜8点）を満たす。台本の展開上は3点案がシンプルで、既存の
`gen_prompt`（"bar chart illustration comparing income by perceived attractiveness"）や
シーン4の narration の流れ（平均より良い/悪いの二分）とも自然に合う。

## 要修正フラグ（台本側への申し送り）

`scripts/20260629-sns-lookism-acceptance.yaml` シーン4 の既存ナレーション:

> 「すると、平均より見た目が良いとされた人は賃金が最大で十数パーセント高く、逆に平均より
> 見た目が劣るとされた人は、賃金が下がる傾向がありました。」

これは一次資料の数値と食い違う。実際は「平均より見た目が良い」側（プレミアム）は
男女計で**+4.9%（男性でも+5.4%）**にとどまり、「十数パーセント」に達するのは
**平均より見た目が悪い側（ペナルティ）のサブサンプル**（例: Table 6「男性・米国2サンプルのみ」
の −0.132 → 約−12.4%）である。つまり「十数パーセント」という強い表現は、プレミアム側では
なくペナルティ側の一部の推定に対応する。台本修正時にどちらの表現を使うか（プレミアム側を
「最大一割弱」、ペナルティ側を「大きい場合は十数パーセント」に直すなど）は要判断。
本タスクの範囲では判定・記録のみとし、台本本文の書き換えはしていない。

## 却下した候補・フォローアップ確認先

- **却下はしていない**（一次資料で確定できたため代替候補への切り替えは不要だった）。
- ただし裏取りの過程で Mobius & Rosenblat (2006) "Why Beauty Matters" (*American Economic
  Review*, 96(1), 222–235) も一次資料ベースで確認し、H&B (1994) と同オーダーの結果である
  ことを確認した（クロスチェック用に記録）。
  - 実験室設定（雇用者役が労働者役の賃金を決める迷路解きタスク）で、魅力度が1標準偏差
    上がるごとの賃金プレミアムが条件別に Table 4 で報告されている: 視覚のみ条件で約12%、
    音声のみ条件で12.8%、視覚+音声で12.3%、対面条件で17%。
  - Table 4 の脚注で "These premia are of a similar order of magnitude to the beauty premia
    found by Hamermesh and Biddle (1994)" と明記されており、H&B の数値の妥当性の傍証になる。
  - 出所: NBER PDF と同様、原論文PDF（https://econweb.ucsd.edu/~jandreon/182/Mobius%20AER%202005.pdf ,
    著者本人の講義資料等を通じた配布版）をテキスト抽出プロキシ経由で確認。
