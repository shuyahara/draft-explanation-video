# なぜ将棋やスポーツには「プロ」が生まれるのか

- **想定尺**: 約 24 分（1.1倍速。等速 v3 の TTS 実測は 23分56秒）
- **概算文字数**: 約 7,900 文字（v5 実数 7,880 字）（300〜360 文字/分換算。Enceladus 実測はポーズ込みで約 340 文字/分）
- **テーマ／結論**: プロは「強い人がいるから」生まれるのではない。①その技に金を払う仕組み（扶持・入場料・新聞の対局料・興行と楽譜）が先に成立して**生み**、②認定と排除の装置（家元・協会規則・アカデミー・アマチュア規定）があとから地位を**固め**、③複製技術（楽譜・新聞・放送・配信）が観客の上限を外して規模を**増幅**する。三つの説は対立ではなく、順序の違う三つの層。プロは腕前の証明書ではなく「誰かが金を払い始めた」という事実の名前。
- **構成型**: 論証型（問い → 三つの候補説 → 将棋・スポーツ・音楽美術の歴史に当てて比較検討 → 反転〔アマチュアリズムの階級性〕→ 反証と留保〔コスト病：プロは状態〕→ 三層への収束 → 払う仕組みはなぜ生まれるのか〔注目の換金〕→ 冒頭の場面に戻って答える。v3 でコスト病を決着の前に移し、決着後に新理論が来ない順序にした）
- **最終更新**: 2026-09-03（v5: 「資格は必須ではない」を明言〔シーン7・14〕、新シーン13「払う仕組みは、なぜ生まれるのか」を追加、読み上げ 1.1 倍）
- **Issue**: #22
- **トーン設計**:
  - ひとことで: 落ち着いた歴史推理（江戸城・ヴィクトリア朝の競技場・ウィーンの宮廷を渡り歩いて、ひとつの謎を解く）
  - 語り口: 落ち着いた常体。講談ほど煽らず、年号と固有名詞を淡々と積む。二人称「あなた」は各章の問いかけで一度ずつ、距離はやや遠め。テンポは中庸、章の変わり目と反転の直後に長めの間。
  - 画風（video.style）: 版画・セピアの古写真を思わせる抑えた色調のイラスト。歴史場面は紙の質感と暖色のランプ光、現代場面は冷たい自然光と画面の光。人物は引き気味に描き顔のクローズアップは避ける。
  - BGM の方向: チェロとピアノ主体の、穏やかで少し古風な曲。緊張系・明るいポップは不可。候補は references/20260902-pro-bgm.md（本命「遠く、祈りの果て」のる／DOVA-SYNDROME）。
  - 演出の強弱: 章カード5枚（シーン3・5・8・12・13。フック・問題提起・結論には付けない）。図解は採用テストに耐える5箇所（row / chain / converge / chain / converge）に絞り、歴史パートは一枚絵の直接描写で運ぶ。決め文は画面保持＋ポーズ 2.0〜2.5 秒。最後は象徴的な一枚絵（配信画面の光と江戸城の対局を並べない。将棋盤に置かれた一枚の小さな紙幣ではなく、夜の配信者の部屋の静止）で終える。

> 対になるシーン YAML: `scripts/20260902-pro-emergence/20260902-pro-emergence.yaml`
> 裏取りメモ: `references/20260902-pro-sports.md` / `20260902-pro-shogi.md` / `20260902-pro-art-music.md` / `20260902-pro-theory.md`

---

## シーン1: フック（深夜の配信者 → 将棋のくっきりした線 → 問い）

**ナレーション**
深夜2時。画面の中で、誰かがゲームをしている。見ている人は、数十人。画面の端に、500円の投げ銭が流れる。この人は、プロだろうか。
ゲームがうまいから、というだけでは、答えは出ない。この人より上手な人は、いくらでもいる。金をもらっているから、というなら、月にいくらからがプロなのか。誰が、それを決めるのか。
一方で、将棋の世界には、はっきりした線がある。四段という段位を認められた人だけが、プロ棋士と呼ばれる。線は、くっきりしている。
なぜある競技には、こんなにはっきりしたプロがいて、ある遊びには、いないのか。そもそもプロというものは、なぜ生まれるのか。この動画が答えたい問いは、これだ。
素朴な答えは、こうだろう。強い人がいるから。うまい人がいるから。だが、この答えには、はっきりした反例がある。

**画面**
- 章カード: なし
- テロップ: なし（冒頭は画だけで運ぶ）
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt（英語） | cut_reason |
  |---|---|---|---|---|---|
  | 1 | 深夜2時。 | image | 暗い部屋、モニターの光に照らされてゲームをする配信者の後ろ姿。画面の内容は読めない | a person seen from behind playing a video game late at night in a dark room, lit only by the monitor glow, a small webcam on the desk, screen contents blurred and unreadable, cool blue light | 【配信の場面】キュー1〜3は同じ深夜の配信という場面なので1枚で持たせる。冒頭の実写を使う場合は静止画。問い「この人は、プロだろうか。」が開始15秒以内に来るよう情景描写は3文に絞った |
  | 2 | 画面の端に、500円の投げ銭が流れる。 | image | 配信画面の端に流れる通知の手元。文字は読めない | a close-up of a computer monitor edge in a dark room showing a small glowing notification popup with unreadable blurred text, a hand resting on a mouse | 【投げ銭の通知】具体物（通知）にナレーションが触れる瞬間なので寄る |
  | 3 | ゲームがうまいから、 | image | 同じ配信者が椅子にもたれて画面を見ている、少し引いた構図 | the same dark room from a wider angle, a person leaning back in a chair looking at a glowing monitor, headphones around the neck, quiet late-night mood | 【プロかどうかの問い】問いの検討に入るので配信の手元から人物の全体へ引く |
  | 4 | 一方で、将棋の世界には、 | image | 将棋の対局室。和室、盤と駒、二人の対局者を引きで | two players facing each other over a shogi board in a quiet traditional Japanese tatami room, soft daylight from a paper window, seen from a distance, no readable text | 【将棋の線】場面が配信から将棋へ転換する |
  | 5 | なぜある競技には、 | image | 空の将棋盤と、暗い部屋の配信機材を対比させない。問いの提示は将棋盤のクローズアップ（駒の文字は読めない角度）で保持 | a shogi board with pieces seen from a low angle in warm lamplight, shallow depth of field so the piece characters are blurred and unreadable, still and quiet | 【問いの提示】この動画の問いを言語化する箇所なので静かな一枚で保持し、最後の「反例がある。」の後の間まで持たせる |
- 出典表示: なし
- 発音・ポーズメモ: 「奨励会」ショウレイカイ。「四段」ヨダン。「数十人」スウジュウニン。「この人は、プロだろうか。」の後 1.0 秒。「この動画が答えたい問いは、これだ。」の後 0.7 秒。「はっきりした反例がある。」の後 1.2 秒（次シーンへの転換）。

---

## シーン2: 問題提起（強さとプロは別物 → 三つの説の提示）

**ナレーション**
1868年。江戸幕府が消えた年。日本でいちばん強い将棋指したちは、その年に、収入を失った。腕が落ちたわけではない。前の年と同じように、強い。それなのに、将棋で食うという職業のほうが、消えたのだ。
反対の例もある。1880年代のイングランド。フットボール協会は、まだプロを認めていなかった。けれど北部の工業都市では、観客席がすでに労働者で埋まり、クラブは選手に、こっそり金を払っていた。プロは、認められる前から、いた。
強さがあってもプロは消える。認められる前からプロはいる。つまり、プロを生むのは、強さでも、肩書きでもない、別の何かだ。
その何かについて、考えられる説は、大きく三つある。ひとつ。その技に金を払う仕組みがあるから。ふたつ。本物を認定して、他を締め出す装置があるから。みっつ。技を複製して、大勢に届ける技術があるから。
今日はこの三つの説を、将棋、スポーツ、そして音楽と美術の歴史に当てて、比較検討していく。あなたなら、どれに賭けるだろうか。

**画面**
- 章カード: なし
- テロップ: 「説① 金を払う仕組み」「説② 認定と排除の装置」「説③ 複製技術」（ビート5〜7にそれぞれ1本。図解にはしない。単発の列挙は telop が担う）
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | 1868年。 | image | 明治初年、荒れた屋敷の縁側で盤に向かう和装の将棋指し。扶持を失った静けさ | a man in worn Edo-period kimono sitting alone before a shogi board on the veranda of a dilapidated Japanese house, overcast light, muted sepia tones like an old woodblock print, no readable text | 【幕府消滅の年】キュー1〜6は同じ「収入を失った将棋指し」の場面 |
  | 2 | 反対の例もある。 | image | 1880年代イングランド北部、工場の煙突を背景にしたフットボールの観客席、労働者の群衆 | a crowd of working-class men in flat caps packed along the rope of a football pitch in an 1880s northern English industrial town, factory chimneys behind, engraving-like muted tones, no readable text | 【反対の例】場面が日本からイングランドへ転換する |
  | 3 | 強さがあってもプロは消える。 | image | 主張の整理。前ビートの観客席を保持せず、無人の将棋盤とボールを描かない。1枚の静物：古い帳簿の上に置かれた駒（文字は読めない） | a single shogi piece resting on a closed antique ledger book on a dark wooden desk, warm lamplight, book cover and piece characters blurred and unreadable | 【中間の結論】主張の整理に入るので、人物のいない静物で一段落ち着かせる |
  | 4 | その何かについて、 | image | 三つの説の提示の導入。机上に広げた古地図と資料を前に考える人物の手元（文字は読めない） | a person's hands resting on a desk covered with old documents, maps and a magnifying glass in a study, papers blurred and unreadable, warm lamp light, seen from above at an angle | 【三つの説の導入】キュー「その何かについて、」の1文だけ |
  | 5 | ひとつ。 | image | 説①の直接描写: 入場口の小窓で硬貨を渡す手元（19世紀） | a close-up of a hand passing coins through the small window of a wooden ticket booth at a 19th-century sports ground, another hand receiving them, sepia tones, no readable text | 【説①・金を払う仕組み】「ひとつ。」のリズムに合わせて画を切る。telop「説① 金を払う仕組み」 |
  | 6 | ふたつ。 | image | 説②の直接描写: 封蝋と印章の押された免状を手にする人物の手元（文字は読めない） | hands holding an old certificate with a red wax seal and a stamped emblem, the text blurred and unreadable, warm lamplight, close on the document | 【説②・認定と排除の装置】列挙の2つ目で画を切る。telop「説② 認定と排除の装置」。文字物なので偽文字対策の句を添える |
  | 7 | みっつ。 | image | 説③の直接描写: 手動の印刷機から刷り上がった紙が重なる（文字は読めない） | a 19th-century hand printing press with freshly printed sheets stacking up beside it, the print blurred and unreadable, warm workshop light, no people | 【説③・複製技術】列挙の3つ目で画を切る。telop「説③ 複製技術」 |
  | 8 | 今日はこの三つの説を、 | image | 三つの説を持って歴史へ向かう。ビート4と同じ机上資料の画を再提示 | （ビート4と同じ画を再提示） | 【歴史への出発】列挙が終わったので机上へ戻し、「どれに賭けるだろうか。」の後の間まで保持 |
- 出典表示: なし
- 発音・ポーズメモ: 「将棋指し」ショウギサシ。「消えたのだ。」の後 0.7 秒。「プロは、認められる前から、いた。」の後 0.7 秒。「別の何かだ。」の後 0.8 秒。三つの説は「ひとつ。」「ふたつ。」「みっつ。」の後それぞれ 0.4 秒。「どれに賭けるだろうか。」の後 1.5 秒（章転換）。

---

## シーン3: 説①の検証・将棋の起源（章「将棋のプロは、誰が作ったのか」）

**ナレーション**
最初の説から見ていこう。金を払う仕組みが、プロを生む。この説をいちばん素直に確かめられるのが、将棋だ。
日本で将棋が職業になった瞬間は、はっきりしている。1612年、慶長17年。徳川家康が、大橋宗桂という将棋指しに、五十石五人扶持を与えた。米で払う俸禄と、家来を養う手当。将棋の指南役としての、給料だ。これによって将棋所という、将棋界を束ねる役職が生まれ、大橋家は、幕府に仕える武士に近い身分を得た。
以後、大橋本家、大橋分家、伊藤家の三つの家が、家元、つまり技と称号を世襲で管理する家として、将棋を継いでいく。年に一度、旧暦の11月17日には、江戸城で将軍の前で対局する御城将棋が行われた。8代将軍吉宗の時代、1716年からのことだ。
ここで注意してほしいのは、順序だ。強い将棋指しが現れたから幕府が雇ったのではなく、幕府が雇ったから、将棋指しが職業になった。もちろん宗桂は強かった。だが強い人なら、その前にも後にもいる。将棋のプロは、強さではなく、幕府が作った。
そして幕府が作ったものは、幕府と一緒に消える。

**画面**
- 章カード: 「将棋のプロは、誰が作ったのか」
- テロップ: 「1612年 大橋宗桂に五十石五人扶持（日本将棋連盟の史料による）」「御城将棋 旧暦11月17日・1716年から年1回」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 0 | — | chapter | 章カードの下地は江戸城の障壁画風の金地と松 | — | 章の頭 |
  | 1 | 最初の説から見ていこう。 | image | 江戸初期の城内、将棋盤を挟んで対局する二人と上座から見る人物を引きで（顔は描き込まない） | an early Edo-period Japanese castle interior, two men playing shogi on the tatami while a lord watches from a raised seat, gold folding screens, candlelight, seen from a distance, no readable text | 【説①の導入と家康の扶持】キュー1〜7は「幕府が将棋指しを雇った」場面 |
  | 2 | 以後、大橋本家、 | image | 御城将棋の場面。江戸城の広間、居並ぶ家臣と中央の盤 | a formal ceremony in a large Edo castle hall, rows of samurai seated in silence, a shogi board at the center under the gaze of the shogun on a dais, muted ink-wash and gold tones, wide shot | 【御城将棋】年中行事へ場面が広がる |
  | 3 | ここで注意してほしいのは、順序だ。 | image | 順序の主張。前ビートの広間を保持せず、家康から扶持を受ける将棋指しの手元（書状と駒。文字は読めない） | a kneeling man in Edo-period dress receiving a folded document from an attendant, a shogi piece and the document on the tatami before him, paper blank and unreadable, soft lamplight, close on hands | 【順序の主張】「幕府が雇ったから職業になった」の決め文へ向けて具体物に寄る。決め文「幕府が作った。」で画面保持 |
  | 4 | そして幕府が作ったものは、 | image | 予告。夕暮れの江戸城の石垣と堀、人はいない | the stone walls and moat of Edo Castle at dusk with no people, long shadows, muted sepia tones, quiet and foreboding | 【次章への予告】幕府の消滅を暗示する無人の城で章を閉じる |
- 出典表示: 日本将棋連盟「将棋の歴史」／同コラム「11月17日は将棋の日」（2016）
- 発音・ポーズメモ: 「慶長」ケイチョウ。「大橋宗桂」オオハシソウケイ。「五十石五人扶持」ゴジッコクゴニンブチ。「将棋所」ショウギドコロ。「幕臣」バクシン。「御城将棋」オシロショウギ。「吉宗」ヨシムネ。「将棋のプロは、強さではなく、幕府が作った。」の後 2.2 秒（決め文・画面保持）。「幕府と一緒に消える。」の後 1.2 秒。

---

## シーン4: 断絶と再生（幕府 → 新聞）

**ナレーション**
1868年に幕府が倒れると、三家は扶持を失った。家元の制度は名目だけになり、1893年、十一世名人の伊藤宗印が亡くなったあと、名人の座は、5年以上、空いたままになった。強い人がいなくなったのではない。座る人を養う仕組みが、なくなったのだ。
将棋を職業として作り直したのは、新聞だった。ただし、一夜にしてではない。1881年に棋士たちが、対局の記録である棋譜の小冊子を出し、1906年には神戸新聞が将棋の欄を作る。そして1908年、萬朝報という新聞が、公式の対局、つまり棋戦を主催して、対局のたびに一局2円の対局料を払い始めた。将棋を指すこと自体で金が入る仕組みが、ここで復活した。
新聞は、棋譜を紙面に載せて部数を伸ばしたかった。棋士は、指す場所と対局料が欲しかった。この取引が、家元の世襲まで壊していく。1935年、東京日日新聞と大阪毎日新聞の主催で、名人を実力で決める名人戦が始まる。1937年、木村義雄が、初めての実力制名人になった。
今の将棋界も、新聞社が資金を出す、この構造の上にある。竜王戦は読売新聞、名人戦は毎日新聞と朝日新聞が主催している。幕府の扶持が、新聞社の契約金に置き換わった。パトロンの名前が変わっただけで、金を払う誰かが技を職業に変える、という構造は、400年、同じだ。
ここまでは、第一の説の圧勝に見える。だが、将棋が特殊なだけかもしれない。では、スポーツではどうか。

**画面**
- 章カード: なし
- テロップ: 「1893年 伊藤宗印没後、名人不在5年余」「1908年 萬朝報が棋戦を主催・一局2円」「1937年 木村義雄が初の実力制名人」「竜王戦＝読売新聞／名人戦＝毎日新聞・朝日新聞」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | 1868年に幕府が倒れると、 | image | 明治初期、空の上座と置き去りの将棋盤。名人不在 | an empty raised seat in a dim Meiji-era Japanese room with a shogi board left untouched on the tatami, dust in a shaft of light, muted sepia, no people | 【扶持の喪失と名人不在】キュー1〜5は同じ「仕組みが消えた」場面 |
  | 2 | 将棋を作り直したのは、新聞だった。 | image | 明治後期の新聞社の印刷所、輪転機と紙の束（紙面の文字は読めない） | a late Meiji-era newspaper printing room with a large rotary press and stacks of freshly printed papers, workers in the background, newsprint text blurred and unreadable, warm gaslight | 【新聞の登場】主体が幕府から新聞へ転換する |
  | 3 | そして1908年、 | image | 新聞社の一室での対局。記者が棋譜を書き取る手元（紙は白紙） | two men playing shogi at a low table in a Meiji-era newspaper office while a reporter beside them writes on a blank sheet, ink brush and paper, papers unreadable, warm lamplight | 【対局料の復活】「一局2円」の具体的場面に寄る |
  | 4 | 新聞は、棋譜を紙面に載せて | image | 昭和初期の名人戦の対局場。旅館の広間、記録係、新聞社の腕章 | a 1930s Japanese inn hall set up for a shogi title match, two players at the board, a scorekeeper and newspaper staff seated along the wall, soft daylight through shoji, no readable text | 【実力制名人戦】取引が世襲を壊す場面へ転換 |
  | 5 | 今の将棋界も、新聞社が資金を出す、この構造の上にある。 | image | 現代のタイトル戦の対局室。和室、盤、スポンサー看板は描かない（文字回避）。引きの構図 | a present-day professional shogi title match in a quiet traditional Japanese room, two players in kimono facing the board, a recorder seated nearby, clean natural light, wide shot, no signage, no readable text | 【現代への接続】400年同じ構造、の主張を現代の画で受ける。「400年、同じだ。」で画面保持 |
  | 6 | ここまでは、第一の説の圧勝に見える。 | image | 次章への橋渡し。将棋盤から離れ、霧のかかったイングランドの競技場の遠景（無人） | a distant view of an empty Victorian football ground in morning mist, wooden stands and a muddy pitch, industrial town rooftops behind, muted engraving tones | 【次章への問い】場面をイングランドへ先回りさせて章を閉じる |
- 出典表示: 日本将棋連盟「日本将棋の歴史」（3）（20）／Wikipedia「第1期名人戦（将棋）」／ビジネス+IT「日本将棋連盟と新聞社は、将棋界の泥沼から抜け出せるか」
- 発音・ポーズメモ: 「十一世」ジュウイッセイ。「伊藤宗印」イトウソウイン。「萬朝報」ヨロズチョウホウ。「棋譜」キフ。「一局」イッキョク。「木村義雄」キムラヨシオ。「なくなったのだ。」の後 0.8 秒。「ここで復活した。」の後 0.6 秒。「400年、同じだ。」の後 2.0 秒（決め文）。「では、スポーツではどうか。」の後 1.5 秒（章転換）。

---

## シーン5: フットボールのプロ容認（章「スポーツでも、同じことが起きたのか」）

**ナレーション**
19世紀のイングランドに飛ぶ。フットボール協会、FAが設立されたのは1863年。ロンドンの紳士たちのクラブが集まって、ルールを統一するためだった。この人たちにとって、フットボールは金のためにやるものではなかった。
ところが1880年代、様子が変わる。北部や中部の工業都市、プレストン、アストン・ヴィラ、サンダーランドといったクラブで、選手への支払いが常態化する。観客席には、土曜の半休を得た労働者が集まり、入場料を払っていた。1882年には、鉄道会社がFAカップの決勝に向けて、北部から千人単位の観客を運ぶ特別列車を走らせている。ただし、鉄道が観客を作ったのではない。すでにあった流れを鉄道が後押しした、というのが歴史家の慎重な見方だ。
1884年、プレストンがロンドンのクラブから、プロを使っていると告発された。会長は支払いの事実を認め、プレストンは大会から締め出された。だが締め出された側は、引き下がらなかった。金を払っているクラブが集まって、別の協会を作ると言い出したのだ。
FAは折れた。1885年7月20日、一定の条件のもとでプロ選手を認めると発表する。告発から、わずか1年半。3年後の1888年には、定期的な対戦を保証するフットボールリーグが発足した。
順序を見てほしい。金を払う観客が先にいて、その金で選手を雇うクラブが次にできて、協会の規則は、いちばん最後に、しぶしぶ追いついた。ただし、FAは抵抗した。規則は自動的には変わらない。押し切るには、綱引きが必要だった。
では、抵抗した側は、何を守ろうとしていたのか。

**画面**
- 章カード: 「スポーツでも、同じことが起きたのか」
- テロップ: 「1863年 FA設立」「1882年 FAカップに北部から特別列車（鉄道は観客を「作った」のではなく「後押し」）」「1884年 プレストン、プロ使用で告発・除名」「1885年7月20日 FAがプロを容認」「1888年 フットボールリーグ発足」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 0 | — | chapter | 下地はヴィクトリア朝の煉瓦とガス灯 | — | 章の頭 |
  | 1 | 19世紀のイングランドに飛ぶ。 | image | 1863年、ロンドンの酒場の一室で会合するフロックコートの紳士たち。書類は白紙 | a group of Victorian gentlemen in frock coats gathered around a table in a wood-panelled London tavern room in 1863, papers and inkwells on the table, papers blank and unreadable, gaslight | 【FAの設立】キュー1〜4は紳士たちの協会という同じ場面 |
  | 2 | ところが1880年代、様子が変わる。 | image | 北部の工業都市の試合。満員の観客、煙突、泥のピッチ。実写ストックがあればそれを優先 | a packed crowd of working men in flat caps watching a football match in a northern English industrial town in the 1880s, smoke from factory chimneys, muddy pitch, engraving-like tones, no readable text | 【観客と入場料】場面がロンドンの紳士から北部の労働者へ転換する |
  | 3 | 1882年には、鉄道会社が | image | 蒸気機関車の特別列車から降りるサポーターの群衆 | a Victorian steam train at a busy station platform with a crowd of football supporters in caps and scarves pouring out of the carriages, steam and soot, sepia tones, no readable signage | 【特別列車と留保】鉄道の1文と、その留保の2文をこの画で持たせる |
  | 4 | 1884年、プレストンが | image | 告発と除名。委員会室で対峙する二人の男（顔は描き込まない） | two Victorian men in dark suits facing each other across a committee table in a dim office, one holding a document, papers blank and unreadable, tense atmosphere, seen from the side | 【告発と対抗】事件の場面に転換する |
  | 5 | FAは折れた。 | image | 1885年、協会の発表。掲示板に貼られた告示の前に集まる人々（告示の文字は読めない） | a small crowd of Victorian men gathered before a notice pinned to a wooden board outside a club house, the notice text blurred and unreadable, overcast daylight | 【プロ容認】決定の場面へ。「フットボールリーグが発足した。」まで保持 |
  | 6 | 順序を見てほしい。 | image | 順序の整理。観客席→選手→規則。ターンスタイル（回転式入場口）を通る労働者の列 | a line of working-class men in flat caps passing through an iron turnstile into a Victorian football ground, coins changing hands at a small booth, muted sepia, no readable text | 【順序の主張】「金を払う観客が先」を入場口の画で受ける |
  | 7 | では、抵抗した側は、 | image | 次章の問い。漕艇クラブの艇庫に並ぶボートと、白いブレザーの紳士の後ろ姿 | the interior of a Victorian rowing club boathouse with long wooden racing shells on racks, a gentleman in a white blazer seen from behind looking out at the river, soft morning light | 【次章への問い】抵抗した側＝紳士のアマチュアリズムを暗示して閉じる |
- 出典表示: The FA公式「The History of The FA」／Taylor, "From Evil to Expedient: The Legalization of Professionalism in English Football, 1884–85"（Springer）／National Football Museum「Football, trains and the rise of the travelling fan」／TRID「The Railways and Sport in Victorian Britain: A Critical Reassessment」
- 発音・ポーズメモ: 「FA」エフエー。「プレストン」「アストン・ヴィラ」「サンダーランド」は英語名のまま。「金のためにやるものではなかった。」の後 0.6 秒。「別の協会を作ると言い出したのだ。」の後 0.6 秒。「しぶしぶ追いついた。」の後 0.8 秒。「何を守ろうとしていたのか。」の後 1.5 秒。

---

## シーン6: 反転（アマチュアリズムの正体 → 説②の登場）

**ナレーション**
アマチュア、という言葉を、あなたはどんな意味で使っているだろうか。金をもらわずに、純粋に競技を愛する人。たぶん、そんな意味だろう。だが19世紀のイギリスで、この言葉は、まったく別の役目を負っていた。
ボート競技を見てみよう。アマチュア・ローイング協会は、1880年代に、アマチュアではない者の定義を明文化した。賞金のために競技した者。プロと知りながら対戦した者。そして、賃金のために職工、職人、労働者として働いたことのある者。
つまり肉体労働者は、金をもらっていなくても、アマチュアではなかった。この条項は、1937年まで残る。廃止のきっかけは、その前年の事件だ。1936年、ヘンリー・レガッタに、8人で漕ぐ種目、エイトのオーストラリア代表が出場しようとした。その8人全員が、警察官だった。彼らは肉体労働者とみなされ、出場を拒否された。国際的な非難を浴びて、条項はようやく消えた。
表向きは、金を受け取らないことが条件に見える。だが実際に、金を受け取らずに競技を続けられるのは、金を必要としない人だけだ。アマチュアという線引きは、純粋さの基準に見えて、実際には、誰がその競技の主役になれるかを決める、階級の壁だった。
オリンピックも、この壁の上に建てられた。1894年、クーベルタンが各国に会議を呼びかけたとき、招集状に掲げた主題は、オリンピックの復興ではなかった。アマチュアリズムの原則を、考察し、普及すること。それが表題だった。1912年の金メダリスト、ジム・ソープは、大会前にマイナーリーグの野球で週25ドルを受け取っていたことを理由に、翌年メダルを剥奪されている。
ここで、第二の説が姿を現す。プロを生むのは、金そのものではなく、誰が本物かを認定し、他を締め出す装置ではないのか。

**画面**
- 章カード: なし
- テロップ: 「アマチュア・ローイング協会の規定（1880年代）：職工・職人・労働者は除外」「1936年 全員警察官の豪州代表エイトが出場拒否 → 1937年 条項廃止」「1894年 クーベルタンの招集状の表題「アマチュアリズムの原則に関する考察と普及」」「ジム・ソープ：1912年金メダル → 1913年剥奪（名誉回復は1983年）」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | アマチュア、という言葉を、 | image | 現代、休日の河川敷で草野球をする人々（アマチュアの素朴なイメージ）。実写ストック優先・静止画 | amateur baseball players in mismatched uniforms on a riverside field on a weekend afternoon, families watching from the grass, warm natural light, candid wide shot | 【素朴な意味のアマチュア】キュー1〜3は視聴者の常識を確認する場面 |
  | 2 | だが19世紀のイギリスで、 | image | 反転の予告。ヴィクトリア朝のボートレース、河岸の紳士淑女と白いブレザーの漕手 | a Victorian-era rowing regatta on the Thames, gentlemen in straw boaters and ladies with parasols on the bank, a crew in white blazers carrying a shell, engraving-like muted tones | 【反転の入口】時代がヴィクトリア朝へ転換する |
  | 3 | ボート競技を見てみよう。 | diagram（narrative / row、背景付き） | 選別の可視化。同型の漕手が並び、賃金労働者だけが沈む。担う構造情報: 選別（比率・誰が落ちるか） | 背景: an overcast Victorian boathouse dock with racing shells in the water, no people, muted tones | 【アマチュア規定の選別】三つの除外条件を語る間、列の一部が沈む row で「金をもらっていなくても除外」の構造を見せる。決め要素は「労働者として働いたことのある者」の1〜2秒手前「職人」に同期 |
  | 4 | つまり肉体労働者は、 | image | 1936年、ヘンリー・レガッタ。艇庫の前で締め出されるオーストラリアの8人（顔は描き込まない・引き） | eight athletic men in matching 1930s rowing kit standing together on a riverside dock beside their racing shell while officials in blazers turn away, overcast English summer light, seen from a distance | 【1936年の事件】具体的な事件へ転換。「条項はようやく消えた。」まで保持 |
  | 5 | 表向きは、金を受け取らないことが条件に見える。 | image | 決め文へ向けた静止。豪華な邸宅の庭でテニスやボートを楽しむ紳士階級の遠景 | a distant view of Edwardian gentlemen in white flannels playing on the lawn of a grand country house, a lake with a rowing boat beyond, late afternoon light, muted tones | 【階級の壁】「金を必要としない人だけ」を視覚で受ける。決め文「階級の壁だった。」で画面保持 |
  | 6 | オリンピックも、この壁の上に建てられた。 | image | 1894年、ソルボンヌの会議室。長机と各国の代表、招集状の紙（白紙） | a grand 1890s Parisian lecture hall with delegates in formal dress seated at long tables during an international congress, a printed invitation lying on the table with blank unreadable text, warm gaslight | 【オリンピック】場面がパリの会議へ転換 |
  | 7 | 1912年の金メダリスト、ジム・ソープは、 | image | 1912年の競技場、表彰台に立つ十種競技の選手を後ろから（実在人物の顔は描かない） | a 1912 Olympic stadium seen from behind an athlete standing on the winner's podium, crowd in period dress in the stands, flags on tall poles, sepia photographic tone, athlete's face not visible | 【ジム・ソープ】剥奪の1文だけ表彰台の画で受ける |
  | 8 | ここで、第二の説が姿を現す。 | image | 説②の登場。閉じられた鉄の門と、その向こうの競技場 | a tall wrought-iron gate closed and locked in front of a sports ground, seen from outside at dusk, the field visible through the bars, muted tones, no people | 【説②の提示】「締め出す装置」を門で受けて章を閉じる |
- 出典表示: Wikipedia「Amateur Rowing Association」／Olympics.com「I Olympic Congress – Paris 1894」／Smithsonian Magazine「Jim Thorpe's 1912 Olympic Gold Medals Are Finally Reinstated」（2022）
- 発音・ポーズメモ: 「ローイング」ローイング。「職工」ショッコウ。「8人全員」ハチニンゼンイン。「剥奪」ハクダツ。「別の仕事をしていた。」の後 0.8 秒。「アマチュアではなかった。」の後 0.7 秒。「条項はようやく消えた。」の後 0.7 秒。「階級の壁だった。」の後 2.3 秒（決め文）。「メダルを剥奪されている。」の後 0.8 秒。「他を締め出す装置ではないのか。」の後 1.5 秒。

---

## シーン7: 説②の検討（ウィレンスキーの順序 → 装置は固めるが生まない）

**ナレーション**
確かに、成熟したプロの世界には、たいていこの装置がある。将棋には家元があり、今は奨励会がある。四段への昇段をプロ入りの条件にする、養成機関だ。上がれるのは、原則として半年に二人。年齢の上限もあり、26歳までに上がれなければ、原則として退会だ。フットボールにはFAの規則があった。美術にはアカデミーがあった。1648年にパリで生まれた王立絵画彫刻アカデミーは、150年以上、展覧会と教育をほぼ独占し、1669年には、歴史画を頂点とするジャンルの序列まで定めている。
カリフォルニア大学バークレー校の社会学者ハロルド・ウィレンスキーは、1964年、18の職業の歴史を調べて、職業が専門職になっていく典型的な順序を示した。要約すると、こうなる。まず、その仕事がフルタイムの職業になる。次に、養成機関ができる。職業団体ができる。免許や資格ができる。最後に、倫理綱領ができる。
注目してほしいのは、いちばん最初の段階だ。フルタイムの職業になる。つまり、その仕事だけで食えるようになること。養成機関も、資格も、そのあとに来る。
将棋の家元が、装置だけではプロを保てないことを証明している。明治の将棋三家は、家元という認定装置を持ったままだった。段位も、名人の称号も、残っていた。それでも、食えなくなった。装置は、プロを固めることはできても、プロを生むことはできない。
第二の説は、こう修正すべきだろう。認定と排除の装置は、プロが生まれたあとに、その地位を守るために作られる。金が先で、壁があと。
とすると、やはり第一の説が正しいのか。だが、第一の説だけでは説明できないことがある。なぜ、トップの数人だけが、桁違いに稼ぐのか。

**画面**
- 章カード: なし
- テロップ: 「奨励会：三段リーグ上位2名が四段（プロ）・年齢制限26歳（勝ち越しで最長29歳）」「1648年 王立絵画彫刻アカデミー設立／1669年 ジャンルの序列」「Wilensky, "The Professionalization of Everyone?" AJS (1964)」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | 確かに、プロのいる世界には、 | image | 現代の奨励会の対局室。若い対局者が並ぶ長い部屋、引き | a long quiet room with rows of young players facing each other over shogi boards in a present-day Japanese training league, fluorescent light, seen from the end of the room, no readable text | 【装置の実例・奨励会】キュー1〜4は将棋の装置 |
  | 2 | フットボールにはFAの規則があった。 | image | 17世紀パリのアカデミー。石膏像とイーゼルの並ぶ画室で学ぶ画家たち | a 17th-century Parisian academy drawing hall with students at easels sketching plaster casts of classical statues, tall windows, warm daylight, muted tones, no readable text | 【装置の実例・アカデミー】主体が美術へ転換 |
  | 3 | カリフォルニア大学バークレー校の | diagram（narrative / chain、背景付き） | 職業化の順序を縦の層で見せる。担う構造情報: 順序（フルタイム化が最初）。5層: フルタイムの職業／養成機関／職業団体／免許・資格／倫理綱領。各層はナレーションの語順に `after` 同期（「フルタイムの」「養成機関が」「職業団体が」「免許や資格が」「倫理綱領が」）。accent は最上層 | 背景: a 1960s university library reading room with long wooden tables and green lamps, no people, muted tones | 【職業化の順序】5段階の順序そのものが知見。chain で縦に積む |
  | 4 | 注目してほしいのは、 | image | 明治の将棋三家の当主が、称号だけを残して困窮する屋敷。掛け軸と空の膳（掛け軸の文字は読めない） | a dim Meiji-era Japanese room with a faded hanging scroll, an empty low table and a shogi board, a man in worn kimono sitting with his back to the viewer, scroll characters blurred and unreadable, muted sepia | 【家元の証明】明治の将棋へ戻り「装置だけでは食えない」を受ける。決め文「プロを生むことはできない。」で画面保持 |
  | 5 | 第二の説は、こう修正すべきだろう。 | image | 修正の整理と次章への問い。ラジオの前に集まる家族の1930年代の場面はまだ出さず、コンサートホールの空の客席（次章の予告） | an empty 18th-century concert hall with rows of gilded seats and a grand chandelier, a single lit candelabra on the stage, warm tones, no people | 【説②の修正と次の問い】「金が先で、壁があと。」を保持しつつ、次章の音楽への橋渡し |
- 出典表示: 日本将棋連盟「奨励会」／Britannica「Académie Royale de Peinture et de Sculpture」／Wilensky, H. L. (1964). The Professionalization of Everyone? American Journal of Sociology, 70(2), 137–158
- 発音・ポーズメモ: 「二人」フタリ。「ウィレンスキー」ウィレンスキー。「倫理綱領」リンリコウリョウ。「序列まで定めている。」の後 0.7 秒。「倫理綱領ができる。」の後 0.6 秒。「プロを生むことはできない。」の後 2.2 秒（決め文）。「金が先で、壁があと。」の後 1.0 秒。「桁違いに稼ぐのか。」の後 1.5 秒（章転換）。

---

## シーン8: 音楽家の移動（章「音楽家は、いつ使用人でなくなったのか」）

**ナレーション**
その答えを探すために、競技の外へ出る。音楽と美術は、競技より一足早く、同じ道を歩いていた。
1761年、ヨーゼフ・ハイドンは、ハンガリーの大貴族エステルハージ家に、宮廷の副楽長として雇われた。ハイドンは侯爵家の制服を着て、他の使用人と一緒に食事をし、日に二度、侯爵の前に出て指示を仰いだ。作曲家は、料理人や庭師と同じ、屋敷の使用人だった。当時の音楽家にとって、これはむしろ、恵まれた地位だ。
同じころ、ウィーンでは別の稼ぎ方が試されていた。モーツァルトは、貴族に雇われる代わりに、自分で演奏会を興行した。1784年の四旬節、予約制の演奏会に、174人の予約者を集めている。聴衆から直接、金を集める。宮廷ではなく、市場に向けて演奏する音楽家の姿だ。
1790年、ハイドンの主人だった侯爵が亡くなり、ハイドンは自由の身になる。翌年、興行師ザロモンに招かれてロンドンへ渡り、公開演奏会で新作の交響曲を発表した。チケットの売上で報酬を得る、興行としての音楽。29年間、制服を着ていた男が、最後に市場を経験した。
貴族の使用人から、興行で報酬を得る音楽家へ。これは、将棋の家元が新聞の棋戦に変わったのと、同じ移動だ。だが音楽には、将棋にはない、もうひとつの稼ぎ方があった。

**画面**
- 章カード: 「音楽家は、いつ使用人でなくなったのか」
- テロップ: 「1761年 ハイドン、エステルハージ家の副楽長に（制服着用・日に二度伺候）」「1784年 モーツァルトの予約演奏会 予約者174人」「1791年 ハイドン、ロンドンの公開演奏会へ」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 0 | — | chapter | 下地は18世紀の宮殿の廊下 | — | 章の頭 |
  | 1 | その答えを探すために、 | image | 導入。18世紀の宮殿の音楽室、楽器が並び人はいない | an 18th-century palace music room with a harpsichord, music stands and gilded chairs, morning light through tall windows, no people, muted warm tones | 【競技の外へ】キュー1〜2は転換の宣言 |
  | 2 | 1761年、ヨーゼフ・ハイドンは、 | image | 制服姿の楽長が使用人たちと同じ食堂で食事をしている場面（顔は描き込まない・引き） | an 18th-century servants' dining hall in a Hungarian palace, a man in the household's blue livery uniform seated among cooks and footmen at a long table, candlelight, seen from the end of the table, faces not detailed | 【ハイドンの使用人時代】具体的な人物の場面へ。「恵まれた地位だ。」まで保持 |
  | 3 | 同じころ、ウィーンでは | image | ウィーンの予約演奏会。広間に集まる聴衆と、ピアノに向かう小さな人物を引きで | a crowded 1780s Viennese concert hall with an audience in powdered wigs and silk gowns seated in rows, a fortepiano at the front under chandeliers, seen from the back of the hall | 【モーツァルトの興行】主体がハイドンからモーツァルトへ転換 |
  | 4 | 1790年、ハイドンの主人だった | image | ロンドンの公開演奏会。チケット売り場に並ぶ群衆（掲示の文字は読めない） | a crowd of Londoners in 1790s dress queuing at a lamplit ticket booth outside a concert hall on a foggy evening, playbills on the wall blurred and unreadable, warm gaslight | 【ロンドンの興行】市場に向かう場面へ転換 |
  | 5 | 貴族の使用人から、興行で報酬を得る音楽家へ。 | image | 二つの世界の橋渡し。制服の上着が椅子に掛けられ、机には楽譜の束（音符は読めない） | a livery coat draped over a chair beside a desk stacked with handwritten music manuscripts in an 18th-century room, manuscript notes blurred and unreadable, warm candlelight, no people | 【移動の整理と次の予告】「もうひとつの稼ぎ方」＝楽譜を机上に置いて章を閉じる |
- 出典表示: World History Encyclopedia「Joseph Haydn」／Lorenz, M.「Mozart in the Trattnerhof」（2013）／Wikipedia「London symphonies」
- 発音・ポーズメモ: 「エステルハージ」エステルハージ。「副楽長」フクガクチョウ。「日に二度」ヒニニド。「四旬節」シジュンセツ。「ザロモン」ザロモン。「恵まれた地位だ。」の後 0.7 秒。「市場に向けて演奏する音楽家の姿だ。」の後 0.7 秒。「最後に市場を経験した。」の後 0.8 秒。「もうひとつの稼ぎ方があった。」の後 1.2 秒。

---

## シーン9: 楽譜・著作権・画商（複製が開いた道と、その不安定さ）

**ナレーション**
楽譜だ。演奏は一度きりだが、楽譜は印刷して、何度でも売れる。ただし、それで作曲家に金が入るには、法律が要る。
1710年、イギリスでアン法という、世界初の著作権法ができた。だが、この法律が楽譜に及ぶのかは、長く曖昧だった。1777年、ヨハン・クリスティアン・バッハ、大バッハの末の息子が、無断で楽譜を出版した業者を訴える。裁判所は、楽譜も著作物だと認めた。楽譜を勝手に刷らせない権利、つまり複製を作曲家の収入に結びつける道が、ここで開いた。
ベートーヴェンは、この時代の産物だ。1809年、大公ルドルフと二人の侯爵が連名で、年に4000フロリンの終身年金を約束した。条件は、ウィーンに住み続けること。特定の主人に仕える契約ではない。あわせて、出版社に作品を売り、有力者に曲を献呈して謝礼を受け取る。ベートーヴェン・ハウス・ボンは、これを、フリーランスの芸術家の発明と呼んでいる。
美術でも、同じことが起きた。1874年、アカデミーのサロンの審査に見切りをつけた画家たちが、審査なしの自主展覧会を開く。第1回印象派展だ。画商のデュラン・リュエルが彼らの絵を買い取り、個展を開いて、海外の買い手にまで売った。アカデミーの認定を通さずに、絵を金に変える市場が生まれた。
ただし、市場は優しくない。ベートーヴェンの年金は、1811年の通貨の切り下げで実質的に目減りし、侯爵の一人は支払いを渋って、訴訟になった。デュラン・リュエルも、印象派の絵が思うように売れず、何度も破産寸前まで追い込まれている。パトロンを離れた自由は、不安定と引き換えだった。
それでも、複製という道が開いたことで、音楽家の収入には、それまでなかった性質が加わった。上限が、なくなったのだ。

**画面**
- 章カード: なし
- テロップ: 「1710年 アン法（世界初の著作権法）／1777年 Bach v Longman：楽譜も著作物」「1809年 ベートーヴェンの年金契約 年4,000フロリン（大公ルドルフ・キンスキー侯・ロプコヴィッツ侯）」「1874年 第1回印象派展／画商デュラン＝リュエル」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | 楽譜だ。 | image | 18世紀の楽譜印刷工房。版と刷り上がった楽譜の束（音符は読めない） | an 18th-century music engraving workshop with a printer pulling sheets from a hand press, stacks of printed sheet music with notation blurred and unreadable, warm lamplight | 【楽譜という複製】キュー1〜3は「楽譜は何度でも売れる」 |
  | 2 | 1710年、イギリスで | image | 1777年の法廷。判事席と、書類を掲げる弁護士（書類は白紙） | a Georgian-era London courtroom with a judge in a white wig on the bench and a barrister holding up a document, papers blank and unreadable, wood panelling and candlelight, seen from the gallery | 【アン法と裁判】法律の場面へ転換。「ここで開いた。」まで保持 |
  | 3 | ベートーヴェンは、この時代の産物だ。 | image | 1809年、ウィーンの書斎。机の上の年金契約書（白紙）と封蝋、窓の外の街 | a composer's cluttered study in 1809 Vienna, a signed contract with wax seals lying on the desk beside a quill, the document text blurred and unreadable, a window looking onto rooftops, warm afternoon light, no people | 【年金契約】主体がベートーヴェンへ転換。「発明と呼んでいる。」まで保持 |
  | 4 | 美術でも、同じことが起きた。 | image | 1874年、パリの写真スタジオを借りた展覧会。壁一面の絵と少数の観客（絵の内容はぼかす） | a small 1874 Parisian exhibition room in a former photography studio, paintings hung closely on the walls, a few visitors in top hats and long dresses looking at them, paintings blurred and indistinct, warm daylight | 【印象派展】美術へ転換 |
  | 5 | ただし、市場は優しくない。 | image | 反証。売れ残った絵が積まれた画商の倉庫、帳簿を前に頭を抱える男の後ろ姿（帳簿は白紙） | a dim Parisian art dealer's storeroom in the 1870s with unsold canvases stacked against the walls, a man seen from behind sitting at a desk with an open ledger, ledger pages blank and unreadable, single lamp | 【市場の不安定】反証の場面へ転換。「不安定と引き換えだった。」で保持 |
  | 6 | それでも、複製という道が | image | 「上限がなくなった」の予告。印刷された楽譜が積み上がって天井近くまで届く倉庫（音符は読めない） | a tall warehouse filled with towering stacks of printed sheet music reaching toward the ceiling, notation blurred and unreadable, dust in shafts of light, no people | 【上限の消失】決め文「上限が、なくなったのだ。」で画面保持 |
- 出典表示: Wikipedia「Statute of Anne」「Bach v Longman」／Beethoven-Haus Bonn「Beethoven's capital」／National Gallery of Art「1874: The Birth of Impressionism」／Philadelphia Museum of Art「Discovering the Impressionists: Paul Durand-Ruel and the New Painting」
- 発音・ポーズメモ: 「アン法」アンホウ。「大バッハ」ダイバッハ。「献呈」ケンテイ。「デュラン・リュエル」デュランリュエル。「ここで開いた。」の後 0.8 秒。「発明と呼んでいる。」の後 0.6 秒。「市場が生まれた。」の後 0.6 秒。「不安定と引き換えだった。」の後 1.0 秒。「上限が、なくなったのだ。」の後 2.2 秒（決め文）。

---

## シーン10: 説③の検討（ローゼンとアドラー → 複製技術は増幅する力）

**ナレーション**
シカゴ大学の経済学者シャーウィン・ローゼンは、1981年、アメリカン・エコノミック・レビューに、スーパースターの経済学という論文を書いた。問いはこうだ。なぜ、才能のわずかな差が、収入の巨大な差になるのか。
ローゼンの答えは、条件が二つ重なったときにそれが起きる、というものだった。ひとつは、代わりが効かないこと。並の歌手を十人続けて聴いても、一人の傑出した歌手の一回分にはならない。もうひとつは、一人の演奏を、費用をほとんど増やさずに大勢へ届けられること。録音、放送、そして今なら、配信だ。
この二つが重なると、市場は一人に集中する。かつて歌手の市場は、会場に入れる人数が上限だった。レコードとラジオが、その上限を外した。すると、多くの人が最上位の歌手を選べるようになり、需要はトップへ集中していく。
ただし、才能だけの話ではない。1985年、経済学者モシェ・アドラーは、同じ雑誌で反論した。人は、みんなが知っている演奏家について語り合いたいから、すでに人気のある人を選ぶ。才能に差がなくても、人気が、人気を呼ぶ。その後の実証研究では、才能と人気の両方が効く、というのが大方の結論だ。
どちらにせよ、鍵は複製技術だ。新聞は棋譜を複製した。テレビは試合を複製した。複製が観客の上限を外したとき、トップの数人だけが、それまで不可能だった規模で稼ぎ始める。
これが、第三の説の正体だ。複製技術は、プロを生むというより、プロの規模を増幅する。
では、規模さえ増えれば、プロは自分の足で立てるのか。ここに、意外な事実がある。

**画面**
- 章カード: なし
- テロップ: 「Rosen, "The Economics of Superstars" AER 71(5), 1981」「Adler, "Stardom and Talent" AER 75(1), 1985」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | シカゴ大学の経済学者 | image | 1980年代の大学の研究室、論文の山とタイプライター（文字は読めない） | a 1980s university office with stacks of papers, a typewriter and a chalkboard with faint unreadable marks, afternoon light through blinds, no people | 【論文の提示】キュー1〜3は研究の紹介 |
  | 2 | ローゼンの答えは、 | diagram（narrative / converge、背景付き） | 二つの独立した条件が「市場は一人に集中する」へ収束する。担う構造情報: 二条件の合流（どちらか一方では起きない）。items: 「代わりが効かない」（after「代わりが効かない」）／「費用を増やさず届く」（after「大勢へ届けられる」）。result: 「市場は一人に集中」（「この二つが重なると、市場は一人に集中する。」のキューで、after「重なると」に同期） | 背景: a 1930s living room with a family gathered around a large wooden radio, warm lamplight, seen from behind, faces not visible | 【ローゼンの二条件】二つの条件が合わさって初めて起きる、という構造が知見そのもの。「集中していく。」まで保持 |
  | 3 | ただし、才能だけの話ではない。 | image | 反論。レコード店で同じ一枚を手に取る大勢の客の列（ジャケットは無地） | a crowded 1950s record shop with many customers reaching for copies of the same record from a display, record sleeves plain and unreadable, warm tungsten light | 【アドラーの反論】人気が人気を呼ぶ、を同じ一枚を選ぶ群衆で受ける |
  | 4 | どちらにせよ、鍵は複製技術だ。 | image | 複製の系譜。新聞の将棋欄を読む人々→テレビの試合中継、を1枚に混ぜず、昭和の街頭テレビに集まる群衆を描く（画面の内容はぼかす） | a crowd of people in 1950s Japanese street clothes gathered at night around a television set mounted on a pole outdoors, the screen glowing but blurred and unreadable, wide shot from behind the crowd | 【複製が上限を外す】テレビが試合を複製した場面 |
  | 5 | これが、第三の説の正体だ。 | image | 説③の結論。スタジアムの巨大スクリーンと満員の観客（実写ストック優先） | a packed modern stadium at night with a giant screen glowing above the crowd, seen from high in the stands, screen content blurred, sea of lights | 【説③の結論】「プロの規模を増幅する。」で画面保持 |
  | 6 | では、規模さえ増えれば、 | image | 次シーンの問い。無人の演奏会場のステージに置かれた四つの椅子と譜面台 | four empty chairs and music stands arranged for a string quartet on a dim concert stage, a single spotlight, no people, muted warm tones | 【次への問い】弦楽四重奏の椅子でコスト病の場面を予告 |
- 出典表示: Rosen, S. (1981). The Economics of Superstars. American Economic Review, 71(5), 845–858／Adler, M. (1985). Stardom and Talent. American Economic Review, 75(1), 208–212
- 発音・ポーズメモ: 「シャーウィン・ローゼン」シャーウィンローゼン。「モシェ・アドラー」モシェアドラー。「十人」ジュウニン。「一回分」イッカイブン。「二番目」ニバンメ。「収入の巨大な差になるのか。」の後 0.7 秒。「配信だ。」の後 0.5 秒。「集中していく。」の後 0.8 秒。「人気が、人気を呼ぶ。」の後 0.5 秒。「大方の結論だ。」の後 0.7 秒。「プロの規模を増幅する。」の後 2.0 秒（決め文）。「意外な事実がある。」の後 1.2 秒。

---

## シーン11: 反証と留保（ボーモルのコスト病 → プロは状態である）

**ナレーション**
プリンストン大学の経済学者、ウィリアム・ボーモルとウィリアム・ボウエンは、1966年、舞台芸術の経済を調べた本の中で、奇妙な構造を指摘した。弦楽四重奏を演奏するのに必要な人数と時間は、200年前から変わらない。一方、工場の生産性は上がり続ける。すると、生産性の上がらない仕事の費用は、他の分野の賃金上昇に引きずられて、上がり続ける。生身の人間が演じる限り、効率化では逃げられない。のちに、ボーモルのコスト病と呼ばれる考え方だ。
これは、そのまま競技にも当てはまる。将棋の一局に必要な棋士は、江戸時代から二人のままだ。人件費は下げられず、客席の数にも上限がある。だからプロの世界は、興行収入だけでは支えにくく、スポンサーか、協会か、賞金の出し手を、必要とし続ける。
将棋界の主な収入は、今も新聞社の契約金だ。そしてその新聞は、部数を減らし続けている。幕府が消えたとき将棋のプロが消えたように、払う誰かが消えれば、プロもまた、消えうる。プロは、一度生まれれば終わりの身分ではない。払う仕組みが続いている間だけ存在する、状態なのだ。
では、三つの説は、結局、どういう関係にあるのか。

**画面**
- 章カード: なし
- テロップ: 「Baumol & Bowen, Performing Arts: The Economic Dilemma (1966)」「弦楽四重奏に必要な人数は200年変わらない ＝ ボーモルのコスト病」
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | プリンストン大学の経済学者、 | image | 弦楽四重奏の演奏。四人の奏者を引きで、18世紀でも現代でもない中立の舞台 | a string quartet performing on a small stage, four musicians with violins, viola and cello seen from the audience, warm stage light, timeless setting, faces not detailed | 【コスト病の説明】キュー1〜7は弦楽四重奏の比喩で運ぶ |
  | 2 | 一方、工場の生産性は | image | 対比。自動化された現代の工場のライン、人はほとんどいない | a modern automated factory floor with robotic arms assembling products along a conveyor line, few people, cool industrial light, wide shot | 【生産性の対比】工場へ転換し、「逃げられない。」の後で戻す |
  | 3 | これは、そのまま競技にも当てはまる。 | image | 将棋の一局。二人の棋士と盤、江戸でも現代でもない静かな構図 | two shogi players facing each other over a board in a quiet room, the board between them lit by a single window, seen from the side at a distance, no readable text | 【競技への適用】二人のまま、を盤の画で受ける |
  | 4 | 将棋界の主な収入は、 | image | 新聞の衰退。早朝の配達所に積まれた新聞の束と、減った配達員（紙面は読めない） | a nearly empty newspaper delivery depot at dawn with a few bundles of papers on the floor and a single delivery bicycle, newsprint blurred and unreadable, cold morning light | 【新聞の衰退】払う誰かが消える予感の場面。決め文「状態なのだ。」で画面保持し、最後の問いまで持たせる |
- 出典表示: Baumol, W. J., & Bowen, W. G. (1966). Performing Arts: The Economic Dilemma. Twentieth Century Fund／ビジネス+IT（新聞社スポンサーモデルの持続性）
- 発音・ポーズメモ: 「ボーモル」ボーモル。「ボウエン」ボウエン。「弦楽四重奏」ゲンガクシジュウソウ。「二人」フタリ。「効率化では逃げられない。」の後 0.6 秒。「必要とし続ける。」の後 0.8 秒。「プロもまた、消えうる。」の後 0.8 秒。「状態なのだ。」の後 2.3 秒（決め文）。「どういう関係にあるのか。」の後 1.5 秒（章転換）。

---

## シーン12: 三説の決着（章「三つの説の、どれが正しいのか」）

**ナレーション**
三つの説を、並べ直そう。
第一の説、金を払う仕組み。将棋では幕府の扶持と、新聞の対局料。フットボールでは、入場料。音楽では、興行と楽譜。どの事例でも、これがいちばん先に来た。そして、コスト病が示したように、これが続く間だけ、プロは存在する。プロを生み、支えるのは、この仕組みだ。
第二の説、認定と排除の装置。家元、協会の規則、アカデミー、アマチュア規定。これらはプロが生まれたあとに、その地位を固め、参入を絞るために作られた。生む力ではなく、固める力。
第三の説、複製技術。楽譜、新聞、放送、配信。これは観客の上限を外して、収入を一部に集中させる。生む力ではなく、規模を増やす力。
つまり三つは、対立する説ではなかった。順番の違う、三つの層だ。払う仕組みが生み、装置が固め、複製が増幅する。
ひとつだけ、付け加えておく。払う仕組みは、需要がすでに芽生えている場所でしか、働かない。金が、見たい気持ちを作るのではない。見たい気持ちに、金が形を与えるのだ。
では、いちばん下の層、払う仕組みそのものは、なぜ生まれるのか。
**画面**
- 章カード: 「三つの説の、どれが正しいのか」
- テロップ: なし（三層は図解が担う）
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 0 | — | chapter | 下地は三本の道が合流する古地図風の画 | — | 章の頭 |
  | 1 | 三つの説を、並べ直そう。 | image | 整理の導入。机の上に三つの資料の束を並べる手元（文字は読めない） | three neat stacks of old documents arranged side by side on a dark desk, a hand resting beside them, papers blurred and unreadable, warm lamp light, seen from above | 【三説の整理】キュー1〜2は導入 |
  | 2 | 第一の説、金を払う仕組み。 | diagram（narrative / chain、背景付き） | 三層の順序。担う構造情報: 順序と役割（生む→固める→増やす）。3層: 「払う仕組み ── 生む」（after「先に来た」）／「認定と排除 ── 固める」（after「固める力」）／「複製技術 ── 増やす」（after「増やす力」）。accent は最上層。決め要素「三つの層だ」は turn（after「順番の違う」）で色転換 | 背景: an old hand-drawn map with three roads converging on a town, ink on aged paper, no readable text | 【三層の収束】三説が層として並ぶ配置が結論そのもの。シーン7の chain と同じ layout だが、間にシーン10の converge を挟むため隣接しない（意図的な対句ではなく順序の再提示）。「複製が増幅する。」の決め文まで保持 |
  | 3 | ひとつだけ、付け加えておく。 | image | 需要が先、を受ける。試合前からすでに満員の観客席の遠景（1880年代） | a distant view of a Victorian football ground already full of spectators before kick-off, overcast light, engraving tones, no readable text | 【需要が先】「見たい気持ちに、金が形を与える」を満員の観客席で受ける |
  | 4 | では、この三層を、 | image | 結論への橋渡し。深夜の配信者の部屋を廊下から見た遠景、ドアの隙間からモニターの光 | a dark apartment hallway at night with a door ajar, cool monitor light spilling out from the room beyond, quiet and still, no people visible | 【結論への橋渡し】冒頭の場面へ戻ることを予告して章を閉じる |
- 出典表示: なし（各説の出典は該当シーンで表示済み）
- 発音・ポーズメモ: 「三つの層」ミッツノソウ。「この仕組みだ。」の後 0.6 秒。「固める力。」の後 0.5 秒。「増やす力。」の後 0.6 秒。「複製が増幅する。」の後 2.2 秒（決め文）。「金が形を与えるのだ。」の後 0.8 秒。「当ててみよう。」の後 1.2 秒。

---

## シーン13: 払う仕組みは、なぜ生まれるのか（章「払う仕組みは、なぜ生まれるのか」）

**ナレーション**
では、その払う仕組みは、なぜ生まれるのか。
三つの事例で、金を出した側の動機を、見てほしい。
家康は、将棋が好きだったから扶持を出したのではない。
御城将棋は、将軍の前で技を競わせる、年中行事だった。
幕府が観客であり、評価者である。
技を城の中に囲い込むことは、権威を目に見える形にすることだった。
新聞は、将棋への愛で棋戦を主催したのではない。
棋譜が紙面に載れば、部数が伸びるからだ。
鉄道会社が特別列車を走らせたのは、乗客が欲しかったからだ。
つまり、払う側は、技そのものに払っているのではない。
技が集める、人々の注目に払っている。
見たい人が集まる。
その注目を、権威や部数や広告に換えられる誰かが現れる。
そのとき、払う仕組みができる。
では、なぜ人は、見たいのか。
レスター大学の社会学者ノルベルト・エリアスとエリック・ダニングは、1986年の著書で、近代社会でスポーツが求められる理由を、興奮の探求、という言葉で説明した。
暴力を抑えた社会で、安全に興奮できる場。
勝敗の行方が分からない緊張が、その興奮の中心にある。
そして、経済学者アドラーが言ったように、人は、みんなが知っている勝負について、語り合いたい。
見たい気持ちは、一人の中で完結しない。
語り合う相手がいるほど、強くなる。
プロに払われている金は、技の対価というより、技が集める注目の対価だ。
この視点で見ると、配信者の投げ銭も、幕府の扶持も、同じものに見えてくる。
では、冒頭の配信者に、三層を当ててみよう。

**画面**
- 章カード: 「払う仕組みは、なぜ生まれるのか」
- テロップ: 「Elias & Dunning, Quest for Excitement (1986)」「Adler (1985)」
- ビート設計（既出素材の再提示で組む。新規生成なし）:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 0 | — | chapter | — | — | 章の頭 |
  | 1 | では、その払う仕組みは、 | image | 家康が扶持を与える場面（シーン3ビート3の再提示） | （再提示） | 【払う側の動機・幕府】キュー1〜3 |
  | 1b | 御城将棋は、将軍の前で | image | 御城将棋の広間（シーン3ビート5の再提示） | （再提示） | 【分割】年中行事へ広がる。キュー4〜6 |
  | 2 | 新聞は、将棋への愛で | image | 新聞社の印刷所（シーン4ビート3の再提示） | （再提示） | 【払う側の動機・新聞】主体の転換 |
  | 3 | 鉄道会社が特別列車を | image | 特別列車の群衆（シーン5ビート4の再提示） | （再提示） | 【払う側の動機・鉄道】1文だけ |
  | 4 | つまり、払う側は、 | diagram（narrative / converge、背景付き） | items「見たい人が集まる」（after「見たい人が」）／「注目を換える誰か」（after「換えられる」）→ result「払う仕組みができる」（after「そのとき」）。担う構造情報: 二条件の合流 | 背景: 1880年代の観客席（シーン5ビート3の再提示） | 【払う仕組みの成立条件】決め文「払う仕組みができる。」で保持 |
  | 5 | では、なぜ人は、見たいのか。 | image | 満員のスタジアム（シーン10ビート6の再提示） | （再提示） | 【なぜ見たいのか】観客側の欲求へ転換 |
  | 5b | 暴力を抑えた社会で、 | image | 1880年代の観客席の群衆（シーン2ビート3の再提示） | （再提示） | 【分割】安全に興奮できる場・勝敗の緊張を群衆で受ける。キュー17〜18 |
  | 6 | そして、経済学者アドラーが | image | レコード店の群衆（シーン10ビート4の再提示） | （再提示） | 【語り合いたい】消費資本 |
  | 7 | プロに払われている金は、 | image | 投げ銭の通知（シーン1ビート2の再提示） | （再提示） | 【注目の対価】決め文で保持し、投げ銭と扶持を同じものとして見せる |
- 出典表示: Elias, N., & Dunning, E. (1986). Quest for Excitement. Basil Blackwell／Adler (1985)／日本将棋連盟「将棋の日」コラム（御城将棋）／ビジネス+IT（新聞社の広告宣伝としての棋戦）／National Football Museum（特別列車）
- 発音・ポーズメモ: 「御城将棋」オシロショウギ。「家康」イエヤス。「扶持」フチ。「棋譜」キフ。「部数」ブスウ。「金」カネ。「エリアス」「ダニング」。「なぜ生まれるのか。」の後 0.8 秒。「見える形にすることだった。」の後 0.7 秒。「乗客が欲しかったからだ。」の後 0.7 秒。「注目に払っている。」の後 0.7 秒。「払う仕組みができる。」の後 2.0 秒（決め文）。「興奮の中心にある。」の後 0.6 秒。「強くなる。」の後 0.7 秒。「注目の対価だ。」の後 2.2 秒（決め文）。「同じものに見えてくる。」の後 0.8 秒。「当ててみよう。」の後 1.2 秒。

---

## シーン14: 結論（冒頭の配信者へ戻る → 問いに答える）

**ナレーション**
冒頭の配信者に戻ろう。深夜2時、数十人の視聴者、500円の投げ銭。この人は、プロなのか。
三つの層で見ると、答えははっきりする。払う仕組みは、ある。投げ銭と、広告収入だ。複製技術も、ある。配信そのものが、観客の上限を外している。だが、認定と排除の装置だけが、まだない。四段も、協会も、アマチュア規定もない。曖昧なのは、この人がプロかどうかではない。プロと呼ぶかどうか、のほうだ。経済的には、プロはもう生まれている。資格がないからプロではない、という考えは、順序が逆だ。1885年のフットボール協会が、しぶしぶプロを認めたときと、同じ段階にいる。
この動画の問いに、答えよう。なぜ競技にはプロが生まれるのか。強い人がいるからではない。その技が集める注目に、誰かが払い始め、それが仕組みになったからだ。装置はあとから地位を固め、複製技術はあとから規模を増やす。
プロとは、腕前の証明書ではない。あなたの技に、誰かが金を払い続ける仕組みができた、という事実の名前だ。
あなたが今、金にならないと思いながら続けている何かも、払い続ける誰かが現れ、それが仕組みになったとき、職業になる。400年前の将棋が、そうだったように。

**画面**
- 章カード: なし
- テロップ: 「① 払う仕組み：ある ／ ② 認定と排除の装置：まだない ／ ③ 複製技術：ある」（ビート2のみ。三層の視覚言語を結論まで引き継ぐ）
- ビート設計:
  | # | 開始文 | 種別 | visual_intent | gen_prompt | cut_reason |
  |---|---|---|---|---|---|
  | 1 | 冒頭の配信者に戻ろう。 | image | シーン1と同じ深夜の配信部屋（同じ素材の再提示可） | （シーン1ビート1と同じ画を再提示） | 【冒頭への回帰】キュー1〜3で場面を戻す |
  | 2 | 三つの層で見ると、 | image | 配信画面の端の通知と、机の上の何もない場所（装置がない）。手元 | a close-up of a streamer's desk at night: a glowing monitor edge with an unreadable notification, a microphone, and an empty space on the desk where nothing sits, cool blue light | 【三層の当てはめ】telop で三層の答え合わせを出し、「同じ段階にいる。」まで保持 |
  | 3 | この動画の問いに、答えよう。 | image | 問いへの答え。将棋・フットボール・音楽の三場面を1枚に混ぜず、江戸城の対局（シーン3ビート1）を再提示 | （シーン3ビート1と同じ画を再提示） | 【問いへの答え】問いへの答えを、最初の歴史場面で受ける |
  | 4 | プロとは、腕前の証明書ではない。 | image | 決め文。配信者の部屋、モニターを消して静かに座る人物の後ろ姿 | a person sitting quietly in a dark room after turning off the monitor, only a faint blue afterglow on the desk, headphones set down, seen from behind, calm and still | 【決め文】「事実の名前だ。」で画面保持＋長い間 |
  | 5 | あなたが今、金にならないと思いながら | image | 最後の象徴的な一枚絵。夜明け前の窓辺、将棋盤と、その隣に置かれたヘッドホン | a shogi board by a window before dawn with a pair of modern headphones resting beside it, first pale light on the wood, piece characters blurred and unreadable, no people | 【結び】400年前の将棋と現代の配信を同じ窓辺に静かに置いて終える。アウトロ 8 秒 |
- 出典表示: なし
- 発音・ポーズメモ: 「数十人」スウジュウニン。「この人は、プロなのか。」の後 0.8 秒。「順序が逆だ。」の後 2.0 秒（決め文）。「同じ段階にいる。」の後 1.0 秒。「規模を増やす。」の後 0.8 秒。「事実の名前だ。」の後 2.5 秒（決め文）。「そうだったように。」は最終セグメント（pause_after なし、アウトロ 8 秒へ）。

---

## 出典一覧（裏取り済み。詳細と確度は references/20260902-pro-*.md）

### 将棋・囲碁
1. 日本将棋連盟「将棋の歴史」「日本将棋の歴史（3）（20）」 https://www.shogi.or.jp/history/story/
2. 日本将棋連盟コラム「11月17日は将棋の日。実はその由来、徳川吉宗の時代にあった。」（2016） https://www.shogi.or.jp/column/2016/11/post_44.html
3. 日本将棋連盟「奨励会」 https://www.shogi.or.jp/match/shoreikai/
4. 加瀬和俊編「戦間期日本の新聞産業」東京大学社会科学研究所 https://jww.iss.u-tokyo.ac.jp/publishments/issrs/issrs/pdf/issrs_48.pdf
5. ビジネス+IT「日本将棋連盟と新聞社は、将棋界の泥沼から抜け出せるか」 https://www.sbbit.jp/article/cont1/33117

### スポーツ
6. The FA「The History of The FA」 https://www.thefa.com/about-football-association/who-we-are/history
7. Taylor, M. "From Evil to Expedient: The Legalization of Professionalism in English Football, 1884–85"（Springer） https://link.springer.com/chapter/10.1057/9780230320819_3
8. National Football Museum「Football, trains and the rise of the travelling fan」 https://nationalfootballmuseum.com/stories/football-trains/
9. Wikipedia「Amateur Rowing Association」 https://en.wikipedia.org/wiki/Amateur_Rowing_Association
10. Olympics.com「I Olympic Congress – Paris 1894」 https://www.olympics.com/ioc/paris-1894-olympic-congress
11. Smithsonian Magazine「Jim Thorpe's 1912 Olympic Gold Medals Are Finally Reinstated」（2022） https://www.smithsonianmag.com/smart-news/jim-thorpe-olympic-gold-medals-reinstated-180980444/
12. TRID「The Railways and Sport in Victorian Britain: A Critical Reassessment」 https://trid.trb.org/View/694736

### 音楽・美術
13. World History Encyclopedia「Joseph Haydn」 https://www.worldhistory.org/Joseph_Haydn/
14. Lorenz, M.「Mozart in the Trattnerhof」（2013） http://michaelorenz.blogspot.com/2013/09/mozart-in-trattnerhof.html
15. Beethoven-Haus Bonn「Beethoven's capital」 https://internet.beethoven.de/en/exhibition/beethovens-capital/
16. copyrighthistory.org「Statute of Anne, 1710」／Wikipedia「Bach v Longman」
17. Britannica「Académie Royale de Peinture et de Sculpture」 https://www.britannica.com/place/Academie-Royale-de-Peinture-et-de-Sculpture
18. National Gallery of Art「1874: The Birth of Impressionism」 https://www.nga.gov/stories/articles/1874-birth-impressionism
19. Philadelphia Museum of Art「Discovering the Impressionists: Paul Durand-Ruel and the New Painting」 https://www.philamuseum.org/exhibitions/discovering-the-impressionists-paul-durand-ruel-and-the-new-painting

### 理論
20. Rosen, S. (1981). The Economics of Superstars. American Economic Review, 71(5), 845–858.
21. Adler, M. (1985). Stardom and Talent. American Economic Review, 75(1), 208–212.
22. Baumol, W. J., & Bowen, W. G. (1966). Performing Arts: The Economic Dilemma. Twentieth Century Fund.
23. Wilensky, H. L. (1964). The Professionalization of Everyone? American Journal of Sociology, 70(2), 137–158.
24. Elias, N., & Dunning, E. (1986). Quest for Excitement: Sport and Leisure in the Civilizing Process. Oxford: Basil Blackwell.

## 要確認事項（台本では断定を避けた箇所）
- ARA の除外規定は 1883 年定義と 1886 年条項の関係が未整理のため「1880年代に明文化」と幅を持たせた。
- IOC のアマチュア規定撤廃の年は情報源で割れるため、台本では言及しない。
- 鉄道が観客を「作った」説には批判的再評価があるため、シーン5で留保を明示した。
- ハイドンの契約条項の逐語（白い靴下等）は二次資料止まりのため「制服」「日に二度」のみ使用。
- ザロモン・コンサートの報酬額は資料間で食い違うため金額を出さない。
- ローゼン論文の「エルビラ」逸話は裏取りできず不使用。「並の歌手を十人〜」は複数の二次資料が一致する要約表現として使用（原文の逐語ではない）。
- 将棋の棋戦契約金の具体額（2005/2024 年）は個人ブログ由来のため使わず、「部数減少で持続が課題」の趣旨のみ。
- 奨励会の合格率（1〜2%）は連盟公式統計が未確認のため不使用。
