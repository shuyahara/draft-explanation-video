# ファクトチェック：「なぜ人は冷笑してしまうのか」数字・所属の一次資料確認

- **調査日**: 2026-08-27
- **目的**: 台本に載せる数字・研究者の所属を一次資料（論文本文・機関公式ページ・原資料PDF）で確認する。
  `20260827-reisho-*.md`（二次資料経由の調査メモ）に対する裏取りの第二段階。
- **手法**: WebSearch/WebFetch。多くは journals.sagepub.com の full-text ページ、PubMed、大学リポジトリPDF、
  Perseus Digital Library、日本財団公式PDF等の一次〜準一次資料に直接アクセスして確認した。
  一部（WVS・OED本体・Sloterdijk訳文の逐語）は一次資料への直接到達ができず未確認のまま残した。

---

## 数字

### 1. Stavrova & Ehlebracht (2019) PSPB "The Cynical Genius Illusion" — **要修正**

**台本の記述**: 「皮肉屋の方が認知課題の成績が良いと信じた人 62〜70%」（Studies 1–3、米英独 計479名）、
「ドイツ成人 約9,197名」「30カ国 約20万人」「相関 r ≈ −.17〜−.25」

**確認結果（一次資料 = journals.sagepub.com full-text 直接閲覧）**:
- 実際は **Study 1a（米・n=195）70%**、**Study 1b（米・n=190）56%**、**Study 2（独・n=137）62%**、
  **Study 3（英・n=152、最適なcynicism比率の判断課題で単純な「%」ではない）** の4研究構成。
  「Studies 1–3」ではなく実際は 1a/1b/2/3 の4本。
  **「62〜70%」というレンジは不正確**（実際のレンジは 56〜70%。Study 1bの56%が抜け落ちている）。
  「米英独 計479名」は 190(1b)+137(2)+152(3) = 479 で数値としては合うが、この組み合わせだと1aが除外され
  「62〜70%」の根拠になる70%（Study 1a）が入らない、という内部矛盾がある。
- Study 4（独成人 **n=9,197**）: r = **−.25**（全体）、−.26（読解）、−.07（情報処理速度）
- Study 5（独青年 **n=879**、7年追跡）: r = **−.17**
- Study 6（**30カ国・約20万人**、PIAAC）: r平均 −.19（教育）、−.16（リテラシー/ヌメラシー）、−.14（ICT）
- 台本の「r ≈ −.17〜−.25」はStudy 4・5の主要値としてはおおむね妥当（Study 4の−.07やStudy 6の−.14〜−.19を
  丸めて省略している点は許容範囲）。
- 「有能な人は腐敗の多い社会でだけシニシズムを強める」の原文: *"highly competent individuals will be more
  likely to endorse cynicism if they live in a country where cynical views seem justified—for example, in a
  country with corrupted institutions and a weak rule of law"*（確認済み）。

**一次資料URL**: https://journals.sagepub.com/doi/full/10.1177/0146167218783195 、
PubMed https://pubmed.ncbi.nlm.nih.gov/29993325/

**判定**: 要修正（「62〜70%」のレンジ表現と「Studies 1–3」という括りが不正確）

**修正案**: 「56〜70%の参加者が、皮肉屋の方が認知課題の成績が良いと信じていた（米・独・英の4研究、
計674名）」、または「Study 1aでは米国の参加者の70%が、Study 2ではドイツの参加者の62%が、皮肉屋の方が
認知課題の成績が良いと予測した」のように、レンジではなく個別の数値を明示する方が正確。相関係数は
「r ≈ −.17〜−.25（研究により−.07〜−.26の幅）」と幅があることを一言添えるとより正確。

**著者所属（確認済み）**: Olga Stavrova = Tilburg University（現在）、Daniel Ehlebracht = University of
Cologne（複数の検索結果で一致。ただし論文本文のaffiliation欄そのものは今回直接閲覧できず、Tilburg大学
研究ポータル等の周辺情報からの確認）。

---

### 2. Stavrova & Ehlebracht (2016) JPSP — **確認済み**

**台本の記述**: 「ベースラインのシニシズムが高いと9年後の収入が低い」（Study 1）

**確認結果**: Journal of Personality and Social Psychology, 110(1), 116–132 (2016年1月)。
Study 1・2は米国の全国代表縦断調査。ベースラインでシニシズムを支持していた人は、**9年後（Study 1）**・
**2年後（Study 2）**の収入が有意に低かった。機序として「協力・信頼を避ける、または監視・統制に過剰投資
することで、協力の恩恵を逃す」と説明。台本の記述と一致。

**一次資料URL**: PubMed https://pubmed.ncbi.nlm.nih.gov/26011659/ 、APA公式PDF
https://www.apa.org/pubs/journals/releases/psp-pspp0000050.pdf

**判定**: 確認済み

---

### 3. Stavrova, Ehlebracht & Ren (2024) British Journal of Psychology — **確認済み**

**台本の記述**: 「約9,000人を最長10年追跡、シニカルな人はリーダー職に就く確率が低い」「権力欲求は強い」

**確認結果**: British Journal of Psychology, 115(2), 226–252。ドイツの全国代表雇用者パネル調査
（約9,000人）の**10年間**のデータを分析。シニシズムが高い従業員ほど、その後10年間でリーダー職に就く
確率が低かった。シニカルな人は「他者に利用されないため」の権力欲求（支配動機）が強いことも確認。
台本の記述と一致。

**一次資料URL**: Wiley https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bjop.12685 、
BPS Research Digest https://www.bps.org.uk/research-digest/cynics-rarely-rise-top

**判定**: 確認済み

---

### 4. Minson & Monin (2012) SPPS "Do-Gooder Derogation" — **確認済み**

**台本の記述**: 「自由連想で47%がベジタリアンに否定語を連想」「否定の強さが『道徳的に見下されている』
予期と相関」

**確認結果**: Social Psychological and Personality Science, 3(2), 200–207。Study 1で参加者の**47%**が
自由連想でベジタリアンに否定的な語を結びつけ、その否定性の強さは「ベジタリアンが自分たちを道徳的に
優れていると見なしているだろう」という予期の強さと相関した。台本の記述と一致。

**一次資料URL**: https://journals.sagepub.com/doi/10.1177/1948550611415695

**判定**: 確認済み

**著者所属（確認済み）**: Julia A. Minson = 2012年当時 University of Pennsylvania (Wharton School)、
現在は Harvard Kennedy School（Professor of Public Policy）。Benoît Monin = Stanford University
（Department of Psychology、一貫して確認）。

---

### 5. Monin, Sawyer & Marquez (2008) JPSP — **確認済み**

**台本の記述**: 「差別的課題を拒否したrebelを、当事者は嫌い、無関係な観察者は好んだ」「自己確証
（self-affirmation）で拒絶が消えた」

**確認結果**: Journal of Personality and Social Psychology, 95(1), 76–93。4研究。Study 1: 反道徳的な
発言を行った参加者は、それを拒んだ人（rebel）を嫌ったが、無関係な観察者はそのrebelを好んだ。Study 2:
差別的課題に参加した人はrebelを嫌ったが、単なる観察者は嫌わなかった。Study 3: この拒絶はrebelが自分
たちを非難しているだろうという知覚に媒介される。Study 4: 参加者が事前に自分の重要な価値観・特性を
記述していた場合（自己確証）はこの拒絶が起きなかった。台本の記述と一致。

**一次資料URL**: PubMed https://pubmed.ncbi.nlm.nih.gov/18605853/

**判定**: 確認済み

**著者所属**: Benoît Monin = Stanford University（確認済み）

---

### 6. Feather & Sherman (2002) PSPB — **確認済み（ただし「予測したのは嫉妬ではない」と明記する必要）**

**台本の記述**: 「シャーデンフロイデを予測したのは嫉妬ではなく憤り（resentment）」、N=184

**確認結果**: Personality and Social Psychology Bulletin, 28, 953–961。**184名**の学部生を対象にした
シナリオ実験。高達成/平均的達成の学生が後に失敗する場面を提示し、**シャーデンフロイデを予測したのは
「嫉妬」ではなく「憤り（resentment）」**であることを確認（嫉妬と憤りは統計的に分離可能）。同情は
どちらによっても予測されなかった。台本の記述と一致。対応著者は N. T. Feather, School of Psychology,
Flinders University。

**Feather の Tall Poppy 研究**（"Attitudes towards the high achiever: The fall of the Tall Poppy"）:
自尊心が低い被験者ほど高達成者への否定的態度が強く、その失敗を望む傾向が確認された、という記述は
ResearchGate上の要旨レベルで確認できたが、原論文本文への直接到達はできず（**部分確認**）。

**一次資料URL**: https://journals.sagepub.com/doi/abs/10.1177/014616720202800708

**判定**: 確認済み（Tall Poppy研究は部分確認）

**著者所属（確認済み）**: N. T. Feather = Flinders University, Australia

---

### 7. Smith et al. (1996) PSPB "Envy and Schadenfreude" — **確認済み（概要レベル）**

**台本の記述**: 実験の概要（優秀な学生のインタビュー映像→挫折）と結果

**確認結果**: Personality and Social Psychology Bulletin, 22(2)。著者は Richard H. Smith, Terence J.
Turner, Ron Garonzik, Colin W. Leach, Vanessa Urch-Druskat, Christine M. Weston。「優れた」または
「平均的」に見える学生のインタビュー映像を見せ、その後挫折したという後日談を伝える実験デザインで、
嫉妬が誘発された条件でシャーデンフロイデが有意に増加したことを確認。台本の記述と一致（ただし今回は
論文要旨レベルの確認にとどまり、本文の詳細な数値までは未照合）。

**一次資料URL**: https://journals.sagepub.com/doi/10.1177/0146167296222005

**判定**: 確認済み（要旨レベル）

**著者所属（確認済み）**: Richard H. Smith = University of Kentucky（Professor of Psychology）

---

### 8. van Dijk et al. (2006) Emotion — **確認済み**

**台本の記述**: 「標的が自分と類似している場合にのみ嫉妬がシャーデンフロイデを予測」

**確認結果**: *Emotion*, 6(1), 156–160。先行研究で「嫉妬がシャーデンフロイデを予測する」結果と「しない」
結果が混在していた問題を、標的と観察者の**性別の一致（類似性）**という調整変数で整理。標的が自分と
性別が一致する（関連性の高い社会的比較対象である）場合にのみ、嫉妬がシャーデンフロイデを予測することを
示した。台本の記述と一致。

**一次資料URL**: VU大学リポジトリPDF https://research.vu.nl/ws/files/2180526/Van%20Dijk%20Emotion%206(1)%202006.pdf

**判定**: 確認済み

---

### 9. Choy, Eom & Li (2021) PAID — **確認済み**

**台本の記述**: Cyberball、「シニシズムの高い人は排除後に共感・向社会性が回復しない」

**確認結果**: Personality and Individual Differences, 178（2021）。オンラインの仮想キャッチボール
ゲーム（Cyberball）で社会的排除を操作。シニシズムの低い人は排除されると共感が高まりその後の向社会的
行動が増えたが、シニシズムの高い人はこの反応が見られなかった。台本の記述と一致。

**一次資料URL**: Singapore Management University 機関リポジトリ https://ink.library.smu.edu.sg/soss_research/3350/

**判定**: 確認済み

**著者所属（確認済み）**: Bryan K. C. Choy・Norman P. Li = Singapore Management University。
Kimin Eom = 2021年発表当時 Singapore Management University（2021年7月時点のCV記載を確認）。
**現在（2026年時点）は Australian National University に異動済み**（要更新：台本で所属を書く場合は
「発表当時: シンガポール経営大学」と明記するか、現在の所属に更新すること）。

---

### 10. Zoizner (2021) Communication Research — **確認済み**

**台本の記述**: 「54件の知見・32研究・38,658人」「戦略報道→政治的シニシズム d=0.32」

**確認結果**: Communication Research, 48(1), 3–25。54件の知見・32研究・回答者**38,658人**を対象とした
メタ分析。戦略報道への接触は政治的シニシズムを増大させる（効果量 **d = 0.32**）。実質的な政治的知識を
低下させる（d = −0.31）。ニュース評価を悪化させる（d = −0.22）。台本の記述と完全に一致。

**一次資料URL**: https://journals.sagepub.com/doi/10.1177/0093650218808691

**判定**: 確認済み

**著者所属**: Alon Zoizner = **現在 University of Haifa, Department of Communication**（Assistant
Professor）。ただし2021年の論文発表当時はHebrew University of Jerusalem（政治学部）に所属していた
可能性が高い（博士号取得機関）。台本で所属を書く場合は「現在: ハイファ大学」と明記するのが安全
（「発表当時」の所属は今回未確定）。

---

### 11. Hasell, Halversen & Weeks — **確認済み（誌名・巻号に注意）**

**台本の記述**: SNSの政治的攻撃→怒り→シニシズム、調査年・N（約1,800人？）・掲載誌・巻号は要確認

**確認結果**: "When Social Media Attack: How Exposure to Political Attacks on Social Media Promotes
Anger and Political Cynicism"。**The International Journal of Press/Politics, 30(1), 167–186**
（2025年掲載、データは2020年米大統領選期のパネル調査）。米国成人 **N=1,800** のパネル調査。SNS上の
政治的攻撃投稿への接触→怒りの喚起→政治的シニシズムの上昇、という媒介経路を報告。

**一次資料URL**: https://journals.sagepub.com/doi/10.1177/19401612231221806

**判定**: 確認済み（誌名は Communication Research ではなく **International Journal of Press/Politics**、
掲載年は2025年である点に注意）

**著者所属（確認済み）**: Ariel Hasell・Audrey Halversen・Brian E. Weeks = いずれも University of
Michigan, Department of Communication and Media

---

### 12. 日本財団「18歳意識調査」第20回（2019年） — **確認済み（一次PDF照合完了）**

**台本の記述**: 「自分で国や社会を変えられると思う」日本18.3%、韓国39.6%、ドイツ45.9%、イギリス50.7%、
9カ国中最下位

**確認結果**: 日本財団公式PDF「18歳意識調査『第20回–社会や国に対する意識調査-』要約版」（2019年11月
30日）を直接読み込み、全数値を照合した。
- 調査対象: 日本・インド・インドネシア・韓国・ベトナム・中国・イギリス・アメリカ・ドイツの**9カ国**、
  各国17〜19歳**1,000名**（男女各500名）
- 実施期間: **2019年9月27日〜10月10日**、インターネット調査
- 「自分で国や社会を変えられると思う」（はい）: **日本18.3%**（9カ国中最下位）、韓国**39.6%**、
  ドイツ**45.9%**、イギリス**50.7%**、インド83.4%、中国65.6%、インドネシア68.2%、ベトナム47.6%、
  アメリカ65.7%
- 台本の数値・国名・割合は**すべて一次資料と完全一致**。

**一次資料URL**: https://www.nippon-foundation.or.jp/app/uploads/2019/11/wha_pro_eig_97.pdf

**判定**: 確認済み（一次資料で完全照合）

---

### 13. OECD Trust Survey 2021／WVS — **一部確認済み・一部未確認**

**台本の記述**: 日本の「国の政府への信頼が高い/やや高い」24%。WVS Wave 7で日本の一般的信頼が88カ国中
38位？

**確認結果**:
- OECD分: 「Government at a Glance 2023: Japan」で、2021年OECD Trust Surveyにおいて日本の国政府への
  信頼「高い/やや高い」が**24%**であることを確認（地方政府38%、公務員31%）。**確認済み**。
  なお2026年発表の最新調査（2025年実施）では日本の政府信頼は**46%**まで上昇しており、24%は
  「2021年時点」の数値であることを台本で明記する必要がある。
- WVS分: 88カ国中38位・83.7%という具体的数値は、今回もOur World in Data・Visual Capitalist等の
  二次情報の域を出ず、WVS公式データエクスプローラーでの一次照合はできなかった。**未確認のまま**。

**一次資料URL**（OECD分）: https://www.oecd.org/en/publications/government-at-a-glance-2023_c4200b14-en/japan_fc496412-en.html

**判定**: OECD分は確認済み（ただし「2021年時点」の明記が必要）。WVS分は未確認（二次資料のみ）。

**修正案**: WVSの「88カ国中38位」「83.7%」は一次資料未確認のため、台本では使うなら「約8割・世界的には
中位程度」のように幅を持たせた表現にとどめるか、使用を見送ることを推奨。

---

### 14. OED／語源 — **確認済み（ただしOED本体は未直接閲覧）**

**台本の記述**: 英語cynic初出1533、cynicism 1606、「性格・態度」の意味の定着1847年頃

**確認結果**: oed.com のcynic, n. & adj.／cynicism, n. の各ページの検索結果概要、およびetymonline
（OEDに基づく語源辞典）経由で、"cynic"の初出1533年、"cynicism"の初出1606年、人物の性格を表す用法
としての定着が1847年、という3つの年代を確認。台本の記述と一致。

**一次資料URL**: https://www.oed.com/dictionary/cynic_n 、https://www.etymonline.com/word/cynic
（OED自体は購読制のため本文の逐語確認はできず、検索結果に表示された要約での確認にとどまる）

**判定**: 確認済み（ただしOED本文の直接閲覧はできておらず、確度は「中〜強」）

---

### 15. ディオゲネス・ラエルティオス『列伝』第6巻 — **確認済み（一次資料で完全照合）**

**台本の記述**: ランプ6.41、甕6.23、アレクサンドロス6.38、通貨の神託6.20–21、犬を誇る6.60

**確認結果**: Perseus Digital Library の英訳版（Diogenes Laertius, Lives of Eminent Philosophers,
Book VI, Chapter 2）を直接参照し、5つの逸話すべての節番号を照合した。
- **§23**: メトロオンの甕を住処にした
- **§41**: 昼間にランプを点灯し「人間を探している」と言いながら歩いた
- **§38**: アレクサンドロス大王に「Stand out of my light（日陰になるからどいてくれ）」
- **§60**: 「くれる者には尾を振り、拒む者には吠え、悪党には噛みつく」（犬と呼ばれることを誇る発言）
- **§20–21**: デルフォイの神託「政治的通貨を変造せよ」の逸話（複数の異伝あり）

台本の節番号は**すべて一次資料（Perseus英訳）と完全一致**。

**一次資料URL**: https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0258%3Abook%3D6%3Achapter%3D2

**判定**: 確認済み（一次資料で完全照合）

---

### 16. Mazella (2007) の "not a weakening ... but rather their inversion" — **確認済み**

**台本の記述**: この表現が実在するか

**確認結果**: 複数の出版社紹介文・書評で一致して引用されている正確な文言:
*"describes a life of political quietism, passivity, and moral indifference, representing not a
weakening of ancient philosophic norms but rather their inversion."*
台本の記述と一致（実在する）。

**一次資料URL**: University of Virginia Press ほか複数の書誌紹介ページ（原著本文そのものへの直接
アクセスは今回未実施だが、複数の独立した引用元で文言が一致）

**判定**: 確認済み

**著者所属（確認済み）**: David Mazella = University of Houston, Department of English (Associate
Professor)

---

### 17. Sloterdijk『シニカル理性批判』の訳語 — **部分確認**

**台本の記述**: 「啓蒙された偽りの意識（enlightened false consciousness）」の定訳（高田珠樹訳ミネルヴァ
書房の訳語）

**確認結果**: 高田珠樹訳『シニカル理性批判』がミネルヴァ書房（Minerva哲学叢書1）から1996年12月に
刊行されたことは国立国会図書館サーチ・出版社ページで確認できた。訳者・出版社・刊行年は**確認済み**。
ただし「啓蒙された偽りの意識」に対応する訳文が本書内で実際に「啓蒙された虚偽意識」等どう訳されているか
の逐語確認は、今回の検索では原文・訳文本体に到達できず**未確認のまま**。

**一次資料URL**: NDLサーチ https://ndlsearch.ndl.go.jp/books/R100000002-I000002560056 、
ミネルヴァ書房 https://www.minervashobo.co.jp/book/b47366.html

**判定**: 部分確認（書誌情報は確認済み、訳語の逐語は未確認）

---

## 所属（研究発表当時／現在）

| 研究者 | 確認結果 | 判定 |
|---|---|---|
| Olga Stavrova | Tilburg University（現在） | 確認済み（複数情報源一致、論文本文のaffiliation欄は未直接閲覧） |
| Daniel Ehlebracht | University of Cologne | 確認済み（同上） |
| Julia Minson | 2012年当時: University of Pennsylvania (Wharton School)／現在: Harvard Kennedy School (Professor of Public Policy) | 確認済み |
| Benoît Monin | Stanford University（Department of Psychology） | 確認済み |
| Norman Feather | Flinders University, Australia | 確認済み |
| Richard H. Smith | University of Kentucky（Professor of Psychology） | 確認済み |
| Susan Fiske | Princeton University | 今回は再検証せず（著名研究者につき既知の情報として扱う。要望があれば別途一次確認） |
| Choy / Eom / Li | Choy・Li = Singapore Management University／Eom = 2021年発表当時SMU、**現在はAustralian National Universityに異動** | 確認済み（要更新: 現在の所属が変わっている） |
| Alon Zoizner | **現在** University of Haifa, Department of Communication | 確認済み（現在の所属。発表当時の所属は未確定） |
| Ariel Hasell | University of Michigan, Department of Communication and Media | 確認済み |
| Joseph Cappella / Kathleen Hall Jamieson | University of Pennsylvania, Annenberg School（著名研究者につき今回は再検証せず） | 未検証（既知情報） |
| David Mazella | University of Houston, Department of English (Associate Professor) | 確認済み |
| Jack Citrin / Laura Stoker | UC Berkeley（著名研究者につき今回は再検証せず） | 未検証（既知情報） |
| George Vaillant | Harvard Medical School（著名研究者につき今回は再検証せず） | 未検証（既知情報） |
| Michel Foucault | Collège de France（1983–84講義。著名につき再検証せず） | 未検証（既知情報） |
| 津田正太郎 | **現在は法政大学ではなく慶應義塾大学メディア・コミュニケーション研究所教授**（法政大学社会学部には2008年4月〜2022年3月在籍） | **要修正**（台本で「法政大学」と書く場合は誤り。現在は慶應義塾大学） |
| 北田暁大 | 東京大学大学院情報学環 教授（現在） | 確認済み（2005年当時の所属は今回未確認だが、現在の所属として東大情報学環は確定） |
| Jamil Zaki | Stanford University（著名研究者につき今回は再検証せず） | 未検証（既知情報） |

---

## 要修正のまとめ

1. **項目1（Stavrova & Ehlebracht 2019）**: 「62〜70%」というレンジ表現が不正確（実際は56〜70%、
   Study 1bの56%が欠落）。「Studies 1–3」という括りも実際の研究構成（1a/1b/2/3の4研究）と食い違う。
   使うなら個別の数値（70%・56%・62%）で示すか、レンジを「56〜70%」に修正する。
2. **項目9の所属**: Kimin Eomは2021年発表当時Singapore Management Universityだが、現在（2026年時点）
   はAustralian National Universityに異動済み。台本で「現在の所属」として書く場合は要更新。
3. **項目10の所属**: Alon Zoizner の「発表当時（2021年）」の所属は今回確定できず。台本で所属を書く
   場合は「現在: ハイファ大学」に統一するのが安全。
4. **項目11**: 掲載誌はCommunication ResearchではなくInternational Journal of Press/Politics
   （2025年、30巻1号）。台本で誌名・巻号を明記する場合は修正が必要。
5. **津田正太郎の所属**: 台本や調査メモで「法政大学」と書いている場合は誤り。2022年3月に法政大学を
   離れ、現在は慶應義塾大学メディア・コミュニケーション研究所教授。

## 未確認のまま残った項目

- 項目13: WVS（世界価値観調査）の日本の一般的信頼「88カ国中38位・83.7%」は一次資料（WVS公式データ
  エクスプローラー）に到達できず未確認。使うなら幅を持たせた表現にとどめるか使用を見送る。
- 項目14: OED本体（購読制）の逐語的な語義説明は未確認。年代（1533/1606/1847）は複数の情報源で一致し
  確度は高いが、OED原文そのものではない。
- 項目17: Sloterdijk日本語訳の「啓蒙された偽りの意識」に対応する訳語の逐語は、翻訳書本文に到達できず
  未確認。書誌情報（高田珠樹訳、ミネルヴァ書房、1996年）のみ確認済み。
- 著者所属のうち、Susan Fiske・Cappella & Jamieson・Jack Citrin & Laura Stoker・George Vaillant・
  Michel Foucault・Jamil Zaki は著名研究者であり今回は時間配分の都合で一次資料による再確認を行って
  いない（誤りのリスクは低いと判断したが、確認済みではない点に留意）。

## 追記（2026-08-28 公開前チェック）
- **Vaillant の防衛階層**: Vaillant, G. E. (1994). Ego Mechanisms of Defense and Personality Psychopathology. *Journal of Abnormal Psychology*, 103(1), 44–50 の Table 1 と本文で、passive aggression＝immature defenses、humor＝mature defenses（sublimation, suppression, anticipation, altruism, humor）を一次確認。**sarcasm（皮肉）の語は同論文に出てこない**ため、「皮肉を未成熟な受動攻撃に分類した」という帰属は過剰と判断し、シーン 11 を「受動攻撃を未成熟な防衛に分類した／言い逃れできる皮肉はこの側に近い（＝本稿の推論）」に修正（rev9）。
- **TTS の読み**: ASR 読みチェック（`tools/review/review_reading.py`）で「一行」が「いっこう」と読まれている疑い → シーン 4 に `readings`（一行＝イチギョウ、身体＝カラダ）を追加（rev9）。他の固有名詞・難読語は指定読みどおりを確認。
