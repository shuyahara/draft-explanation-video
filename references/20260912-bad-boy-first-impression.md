# 裏取りメモ:「悪い男は初対面では人気だが、時間が経つと落ちる」説の検証

対象動画:「なぜ"誠実な"男性はモテないのか」（Issue #34）。主軸「モテ要素は段階ごとに違う。誠実さは長い関係の段階で効くが、初対面では見えない」を補強する章として使えるかの検証。

## 結論（5行以内）

- **主軸に使えるか: 現状 No（数値つきでは不可）。方向性のみ Yes。**
- 一次資料の**本文PDFを一つも取得できなかった**（後述「アクセス状況」）。ページ番号・表番号つきの数値は1件も確認できておらず、本ルール（一次資料の本文でのみ確認済み数値を採用）上、台本に載せられる数値はゼロ件。
- ただし公式アブストラクト（Crossref / PubMed/NCBI eutils 経由、出版社が一次資料として公開している要旨）のレベルでは、Back et al. (2010) の「ナルシシズムは初対面で人気、特に搾取性/特権意識が最も魅力的」と Leckelt et al. (2015) の「3週間のうちに人気が低下し、これは主に narcissistic rivalry に伴う尊大・攻撃的な言動と信頼できない人物という評価の増加で説明される」という方向性は、主軸と整合する。
- 核になりうる2研究は Back et al. (2010, JPSP) と Leckelt et al. (2015, JPSP)（下記参照）。ただし現時点では「初対面で〜、時間が経つと〜」を**具体的な数字つきで**言うことはできない。
- 使うなら「章を足す」のではなく、本文を入手して数値を確認できてから、が前提。今回は見送るか、「要確認」の含みを持たせた一般的な記述に留めるべき。

## アクセス状況（重要: 読む前に）

以下の4本すべてについて、本文PDFの入手を試みたが**入手できなかった**。試した経路:

- 出版社サイト（APA PsycNet, Wiley Online Library, SAGE Journals, ScienceDirect）→ いずれも購読者限定（403 or ペイウォール）。
- ResearchGate → 論文ページ・直接PDFリンクとも DataDome/Cloudflare のボット対策で 403（`datadome` cookie 発行のみでコンテンツ取得不可）。
- Unpaywall API / OpenAlex API → Back et al. 2010, Leckelt et al. 2015, Jonason et al. 2009 は **oa_status: closed**（合法な無料全文なし）。Carter et al. 2014 のみ oa_status: green と表示されたが、リンク先の Teesside University リポジトリ・York St John リポジトリはいずれも書誌情報のみで「Full text not available from this repository」。
- 大学の研究室ページ（Mitja Back / Boris Egloff / Steffen Nestler の所属サイト）→ 出版物一覧はあるが reprint PDF の直リンクなし。
- scispace.com の PDF リンクは CloudFront 側で 403。
- CORE.ac.uk API は API キーが必要で未取得（今回は取得せず）。
- Sci-Hub 等の違法な迂回手段は使用していない。

→ 結果として、得られたのは **Crossref / PubMed(NCBI eutils) が保持する公式アブストラクト**と、大学リポジトリの書誌ページ止まり。これらは「要旨」であり、プロジェクトルール（要旨や二次記事の数字は採用しない）に照らして、本文の数値としては使えない。

---

## 1. Back, Schmukle & Egloff (2010)

**"Why are narcissists so charming at first sight? Decoding the narcissism–popularity link at zero acquaintance."** *Journal of Personality and Social Psychology*, 98(1), 132–145. DOI: 10.1037/a0016338

- **著者・所属・肩書き**: Mitja D. Back（責任著者、Department of Psychology, Johannes Gutenberg-University Mainz）／Stefan C. Schmukle（University of Münster、当時の具体的な肩書きは未確認）／Boris Egloff（未確認の大学、当時の肩書きは未確認）。肩書き（教授／准教授等）は本文・著者紹介を読めておらず**未確認**。
- **対象と方法**（公式アブストラクトによる）: Study 1 は心理学専攻の新入生 N=73 が、簡単な自己紹介文だけをもとに互いを評価するラウンドロビン・デザイン（2,628ペア）。Study 2〜4 は「うかがい知らない第三者評価者」が、(a) 映像＋音声フル情報、(b) 映像のみ（非言語情報のみ）、(c) 服装の静止画のみ、という3条件で人気を評価し、Study 1 の結果を追試。
- **数値**: **本文未確認**。相関係数・効果量・p値は表・本文ページを読めていないため採用不可。
- **主軸に使える一文（要旨レベル、数値なし）**: 「ナルシシズムは初対面での人気を予測し、特に長期的には最も不適応的とされる側面（搾取性・特権意識）が、初対面ではもっとも魅力的に働く」（アブストラクトの記述。本文 p.X 付きでは未確認）。
- **注意点**: 対象は大学新入生（一般化に留保）。「初対面」の後にどうなるかはこの論文単体では扱っていない（Leckelt et al. 2015 が追跡研究に相当）。自己紹介文・映像・静止画という刺激条件ごとの再現性は示されているが、実際の交際・恋愛文脈での人気ではなく、同性を含む集団内の「好感度・人気」の評価である点に注意（対象者の性別構成・評価者の性別による効果の違いは本文未確認）。

## 2. Leckelt, Küfner, Nestler & Back (2015)

**"Behavioral processes underlying the decline of narcissists' popularity over time."** *Journal of Personality and Social Psychology*, 109(5), 856–871. DOI: 10.1037/pspp0000057

- **著者・所属・肩書き**: Marius Leckelt、Albrecht C. P. Küfner、Steffen Nestler、Mitja D. Back。4名とも University of Münster, Department of Psychology 所属（Crossref/PubMed 記載）。当時の個々の肩書き（教授／博士課程等）は**未確認**。
- **対象と方法**（公式アブストラクトによる）: 縦断的な実験室研究。参加者 N=311 がまず Narcissistic Personality Inventory と Narcissistic Admiration and Rivalry Questionnaire で自己報告し、その後3週間にわたり毎週セッションで小集団に分かれて交流。全セッションを録画し、訓練を受けた評定者が行動をコーディング。セッション内で参加者同士が assertiveness（自己主張）・untrustworthiness（信頼できなさ）・likability（好感度）を相互評定。
- **数値**: **本文未確認**。「何週目で逆転するか」「効果量」は表・図を読めていないため不明。アブストラクトは「時間とともに人気が低下する」「narcissistic admiration の正の効果は当初はあるが減少する」「narcissistic rivalry による負の効果（尊大・攻撃的な言動、信頼できないという評価）は増加する」という**方向性**のみ述べている。
- **主軸に使える一文（要旨レベル、数値なし）**: 「ナルシシズムの人気への効果は当初はプラスだが3週間のうちに低下し、これは尊大・攻撃的な行動が増え信頼できない人物とみなされるようになることで説明される」。
- **注意点**: 「3週間」という短期間の集団内人気の変化であり、恋愛関係の長期的な経過（数ヶ月〜数年）への一般化は本文未確認・要注意。ナルシシズムの2側面（admiration/rivalry）を分けて論じている点は、単純な「悪い男」という括りより精緻であり、台本で使うなら単純化に注意。

## 3. Carter, Campbell & Muncer (2014)

**"The Dark Triad personality: Attractiveness to women."** *Personality and Individual Differences*, 56, 57–61. DOI: 10.1016/j.paid.2013.08.021（Web公開は2013年、印刷号は2014年）

- **著者・所属・肩書き**: Gregory Louis Carter（責任著者、University of Durham, Psychology Department）／Anne C. Campbell（University of Durham）／Steven Muncer（University of Teesside）。当時の肩書き（教授等）は**未確認**。
- **対象と方法**（York St John大学リポジトリの書誌ページ要約、および検索エンジンの要約による）: 女性 N=128 が、ダークトライアド（ナルシシズム・マキャベリアニズム・サイコパシー）の特性を高く持つように設計された架空の男性キャラクター、または対照群の性格描写を読み、魅力度を評価。身体的魅力（写真等）の条件は統制。DT高群のキャラクターが有意に魅力的と評価され、この効果はビッグファイブ人格特性の知覚では説明されなかった、とされる。
- **数値**: **本文未確認**。平均値・t値・p値・効果量、ページ番号・表番号はいずれも確認できていない。
- **短期／長期の区別**: **本文未確認**。要旨・書誌ページからは「短期的関係」の文脈で論じられている（DTは「男性の短期的配偶戦略の進化的な促進要因」という理論枠組みで議論、との記載あり）が、長期的関係についての明示的な比較評価があるかは不明。
- **主軸に使える一文**: 現状は要旨レベルの記述のみで、数値なしでは「初対面で人気→時間が経つと下がる」という**時間経過を伴う主張の裏付けにはならない**（この研究自体、時系列比較をしていない静的な魅力度評価である可能性が高いが、本文未確認のため断定不可）。
- **注意点**: 刺激が「架空のキャラクター描写」であり、実際の初対面の人物評価（Back et al. 2010 のような zero acquaintance 実験）とは方法が異なる点に注意。

## 4. Jonason, Li, Webster & Schmitt (2009)

**"The Dark Triad: Facilitating a short-term mating strategy in men."** *European Journal of Personality*, 23(1), 5–18. DOI: 10.1002/per.698

- **著者・所属・肩書き**: Peter K. Jonason（責任著者、New Mexico State University）／Norman P. Li（University of Texas at Austin）／Gregory D. Webster（University of Florida）／David P. Schmitt（Bradley University）。当時の肩書きは**未確認**。
- **対象と方法・結果（Crossref に登録された公式アブストラクトより全文引用可能）**:
  > "This survey (N = 224) found that characteristics collectively known as the Dark Triad (i.e. narcissism, psychopathy and Machiavellianism) were correlated with various dimensions of short-term mating but not long-term mating. The link between the Dark Triad and short-term mating was stronger for men than for women. The Dark Triad partially mediated the sex difference in short-term mating behaviour."
- **数値**: **本文未確認**（相関係数・回帰係数等は本文・表を読めていない）。
- **主軸に使える一文**: この論文は「初対面の人気→時間経過で低下」という時系列の話ではなく、「ダークトライアドは"短期的な"配偶戦略と相関し、長期的な配偶戦略とは相関しない（自己申告ベース）」という**自己申告アンケート調査**である。主軸の「初対面では見えないが誠実さは長期的に効く」という文脈には、"DT型は短期向き・長期には結びつきにくい"という間接的な傍証として使える可能性はあるが、「初対面で人気→時間とともに不人気」という主張の直接的な裏付けにはならない。
- **注意点**: 自己申告データ（自分が短期・長期の関係をどれだけ求めるか、実際にそうした行動を取ったか）であり、他者からの魅力度評価や人気の推移を扱った研究ではない。N=224 の一般サンプル調査。

## 5. 日本語の調査（「悪い男」「ダメ男」志向）

**なし。** 学術的な一次資料（大学等の調査論文）は検索で見つからなかった。見つかったのは女性誌・恋愛コラム等の二次的なポップ心理学記事（例:「ゲインロス効果」を引用する記事、56.7%の女性がダメ男を好きになった経験があるとするアンケート記事）のみで、出典（実施機関・実施者・調査方法）が確認できるものではない。台本には採用しない。
