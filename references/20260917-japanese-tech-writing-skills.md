# 日本語テクニカルライティング系スキル調査（2026-09-17）

調査目的: Claude Code で使える「日本語テクニカルライティング」系のスキル（Agent Skills /
`SKILL.md` 形式、または Claude Code プラグイン）を調べ、よく使われていて性能に信頼性がある
ものを推薦する。用途は動画台本・技術記事などの日本語ナレーション／解説文の執筆・校正。

**調査方法の制約（正直な申告）**: WebSearch がセッション中たびたび "unavailable" エラーを
返し、Wikipedia など無関係な結果しか取れない試行が多発した。有効な結果が出た検索語・
GitHub 横断検索（コード検索）はログイン要求で使えなかったため、判明した候補から芋づる式に
（README・言及元リンクを辿って）候補を広げる方式で 9 件を集めた。スター数・更新日は
`api.github.com/repos/...` の生データ（2026-09-17 取得）を優先し、ページ要約と数値が食い違う
場合は API 値を採用した。「網羅的な調査」ではなく「見つかった範囲の調査」である点に留意。

## 推薦 3 件（順位付き）

1. **[hikimay/japanese-tech-writing](https://github.com/hikimay/japanese-tech-writing)（1位）**
   — 用途が本プロジェクトに最も一致する Claude Code Skill。「論理で読ませる説明文」を対象に、
   生成AIに日本語の技術文書を書かせる・推敲させる・採点する（6軸×10点、合格ライン42/60）まで
   一式そろう。根拠がラムダノート（理工系専門書出版社）の編集者 k16shikano 氏の規範
   （原典 gist）と、457 スターの stop-ai-slop-jp を明示的に出典として引いており、「作者の主観
   ルール」ではなく由来がたどれる点を評価した。スター数は 4 と少なく実績は薄いが、MIT
   ライセンスで `.claude/skills/` に clone するだけで使え、本リポジトリの「捏造禁止・出典明記・
   一文一義」的な思想と親和性が高い。
2. **[iKora128/stop-ai-slop-jp](https://github.com/iKora128/stop-ai-slop-jp)（2位）**
   — 457 スターと日本語系 Claude Skill の中では突出して採用実績がある。「AI っぽい日本語」の
   語彙・構造パターンを検出・修正する SKILL.md で、5 軸採点（35/50 が基準）を持つ。技術文書の
   構成全体ではなく「AI 臭の除去」に特化するため単独では役不足だが、1位のスキルの下敷きにも
   なっており、1位と組み合わせる／単体で仕上げの校正に使うのに向く。
3. **textlint（`textlint-rule-preset-ja-technical-writing` 555★ + MCP サーバー）（3位・比較枠）**
   — SKILL.md 形式ではないが、azu 氏（textlint 作者本人）による老舗ルールプリセットで、
   「1文100字以内」「読点3つまで」「ら抜き言葉排除」など機械的に判定できるルールを持つ。
   textlint 15.1.0+ は `--mcp` で MCP サーバーとして起動でき、Claude Code から `mcp add` して
   接続すれば「生成→機械チェック→修正」のループを組める。1・2位が文体・論証構造という主観的な
   観点を扱うのに対し、textlint は客観的・再現可能な指標を補完できるため、SKILL.md 2つと併用
   する構成を推薦する。

**それ以外の候補**（表参照）は、スター数 0〜1・更新実績も薄く、内容が重複するか根拠の記載が
薄いため、今回は推薦から外した（`shimo4228/claude-skill-writing-ecosystem`、
`megmogmog1965/claude-code-writing-style`、`hoshimiyacelica/skills`）。

## 比較表

| 名前 | URL | 作者 | ★（2026-09-17時点） | 最終更新 | 導入方法 | 規定している規則の要点 | 根拠の出典 | 信頼性の手がかり | 注意点 |
|---|---|---|---|---|---|---|---|---|---|
| japanese-tech-writing | https://github.com/hikimay/japanese-tech-writing | hikimay | 4（fork 0） | pushed_at 2026-06-19（README上のバージョンは v1.1.0=2026-06-18） | `~/.claude/skills/` または `.claude/skills/` に git clone | 8観点（整形／段落・論証構成／論証の厳密さ＝最優先／読み手負荷／視点と語り／演出の抑制／LLM的表現の禁止／冗長性排除）。生成・推敲・採点（6軸×10点、42/60が合格）の3用途 | k16shikano氏（ラムダノート編集者）の「日本語技術文書の文章規範」gistと、iKora128/stop-ai-slop-jpの語彙リストを明記して引用 | GitHub上でスター4件のみ、利用報告・SNS言及は未確認。ライセンスはMIT表記だがGitHub API判定は"Other"（要確認） | 更新履歴が浅い（コミット数5）。実運用の採用事例は今回未確認 |
| 日本語技術文書の文章規範（gist） | https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d | k16shikano（ラムダノート編集者、自己紹介コメントで確認） | gistのため★指標なし | 2026-09-17（当日更新あり） | gist本文をSKILL.mdとして流用する形（単体でのインストール手順は無い） | パラグラフライティング、論証の厳密さ（推量と断定の使い分け）、読者の認知負荷最小化、LLM的な空句の禁止、翻訳調比喩・擬人化の排除、冗長表現の削除 | 原典そのもの（編集者本人の経験則）。他の一次資料への言及は本文中に見当たらない | X（旧Twitter）で複数の編集者・書き手アカウントが言及・称賛しているのを確認（voluntas氏「プロの編集者が公開した日本語技術文章のスキル」等） | 単体では配布形式（インストーラ・SKILL.md化）が無く、そのままはClaude Codeに導入しづらい。hikimay版を介して使うのが実用的 |
| stop-ai-slop-jp | https://github.com/iKora128/stop-ai-slop-jp | Daichi Nagashima（iKora128） | 457（fork 17） | pushed_at 2026-06-11 | git clone、SKILL.mdをそのまま配置 | 「AI臭」除去に特化。誇張見出し・過度な一般化・パターン化構造・不要な記号（全角ダッシュ等）を検出し、立場・リズム・主体性・具体性・削減の5軸で35/50以上を合格ラインに採点 | 明示的な一次資料への言及は無し（作者の観察・経験則） | 日本語系Claude Skillの中では★数が突出。open issue 0件で放置感は無いが、直近の活発なコミット履歴までは未確認 | 技術文書の論証構造や出典規則までは扱わない（AIっぽい言い回しの除去が主眼）。単独では本プロジェクトの「出典必須」要件は満たせない |
| claude-skill-writing-ecosystem | https://github.com/shimo4228/claude-skill-writing-ecosystem | shimo4228 | 1（fork 0） | pushed_at 2026-08-28 | git clone + `./install.sh`（skills/agentsを`~/.claude/`配下へ） | AI-slop禁止語リスト（日英）、Voice規則（だ・である調×発見調、初期仏教の説法パターンを模範に結論を「共到達」させる修辞戦略）、タイトル規則、article-writing/editor/essay-reviewer/fact-checkerの役割分担 | 明示的な学術・言語学的根拠への言及は限定的（README内の概念紹介のみ） | ★1、利用報告は今回の調査では確認できず | 独自の修辞理論（発見調）が本プロジェクトの「論証型」構成と噛み合うか要検討。実績が薄く単体採用はリスクあり |
| claude-code-writing-style | https://github.com/megmogmog1965/claude-code-writing-style | Yusuke Kawatsu（megmogmog1965） | 1（fork 0） | pushed_at 2026-08-19 | `/plugin marketplace add megmogmog1965/claude-code-writing-style` → `/plugin install writing-style@...` | 6グループ16項目（体言止め禁止、である/ます調統一、冗長表現排除等）。SessionStart hookでルール注入、PreToolUse hookで書き込み時に検証エージェント実行、`/style-review`で全文採点という3層構造が特徴 | 記事・READMEに一次資料への言及なし（textlintへの言及も無し） | Qiita記事（作者本人執筆、2026-08-19投稿・2026-09-03更新）で仕組みを解説。★1で外部の利用報告は未確認 | 「plugin」形式でフックを使う設計のため、既存の `.claude/skills/` ベース運用と混在させる場合は動作確認が必要 |
| japanese-writing-style（hoshimiyacelica/skills） | https://github.com/hoshimiyacelica/skills | hoshimiyacelica | 0（fork 0） | pushed_at 2026-08-26 | リポジトリからskillフォルダを配置（配布方法の詳細記載は薄い） | 記号・書式（太字/中黒の多用禁止、半角英数字原則）、言葉づかい（助詞省略禁止、体言止め禁止、能動態基本）、内容の扱い（断定前の根拠確認）、文のリズム（一文30〜50字目安） | 根拠文献への明示的言及なし（経験則） | ★0、利用報告未確認 | 最も実績が薄い候補。内容は妥当だが第三者評価が皆無 |
| textlint-rule-preset-ja-technical-writing | https://github.com/textlint-ja/textlint-rule-preset-ja-technical-writing | azu（textlint作者） | 555（fork 11） | pushed_at 2026-09-15（継続更新中） | `npm install textlint-rule-preset-ja-technical-writing`、`.textlintrc`に設定 | 1文100字以内、カンマ/読点は1文3つまで、連続漢字6字まで、ですます/である統一、二重否定・ら抜き言葉・弱い日本語表現の排除など23ルール（機械判定可能な客観指標が中心） | textlintコミュニティの慣行・JTFスタイルガイドへの言及あり（詳細な文献リストは本文になし） | 555★・open issue 22件で継続的にメンテされている老舗プリセット。SKILL.mdではなくnpmパッケージ | Claude Codeでは直接の「スキル」ではなくCLI/MCP経由の利用になる（後述） |
| textlint-rule-preset-ai-writing | https://github.com/textlint-ja/textlint-rule-preset-ai-writing | azu | 1,138（fork 22） | pushed_at 2026-06-16 | `npm install @textlint-ja/textlint-rule-preset-ai-writing`（textlint 15.1.0+必須） | AI生成文の機械的パターン5種を検出（機械的箇条書き・誇張表現・過度な強調・コロン直後のブロック要素・テクニカルライティングのベストプラクティス提案） | textlintコミュニティの慣行に基づく。「表現ではなく構造を縛る」という設計方針を明記 | 1,138★・fork22と、調査した中で最も多くの支持を得ている。`npx textlint --mcp`でMCPサーバー化しClaude Code等と連携できる旨が公式ドキュメントに明記 | ルールが「AIっぽさの検出」中心で、日本語表現そのものの巧拙（論証構造・出典要否等）までは扱わない |
| textlint-rule-preset-JTF-style | https://github.com/textlint-ja/textlint-rule-preset-JTF-style | textlint-ja（コミュニティ） | 218（fork 22） | pushed_at 2025-11-18 | `npm install textlint-rule-preset-JTF-style` | JTF（日本翻訳連盟）日本語標準スタイルガイドをルール化。一部ルールは`--fix`で自動修正可 | JTF日本語標準スタイルガイド（一次資料）に準拠。ライセンス表記はコード=MIT、JTFガイド本文=CC BY-SA | 218★。ただしpushed_atが2025-11-18で他候補より更新が止まり気味 | 直近1年弱コミットが無い可能性があり、メンテナンス速度はja-technical-writing/ai-writingに劣る |

## 各候補の詳細

### 1. hikimay/japanese-tech-writing
- SKILL.md の目的は「論理で読ませる説明文」を対象にした生成・推敲・チェックで、マーケティング
  コピーや小説には適用しないと明記。
- 「6軸×10点、合格ライン42/60」という定量的な採点基準を持つ点が、他の日本語スキルと比べて
  実務的（本プロジェクトの `/review` 一式運用と相性が良い）。
- 出典が明記されているのは調査した Claude Skill の中でこの1件のみ（k16shikano gist +
  stop-ai-slop-jp）。

### 2. k16shikano 氏の gist「日本語技術文書の文章規範」
- ラムダノート（理工系専門書出版社）の編集者本人が公開。X 上で複数の編集者・書き手が
  「プロの編集者が公開した日本語技術文章のスキル」と評価しているのを確認（一次資料は本人の
  コメント欄での自己紹介）。
- ライセンスは Unlicense。gist 単体は配布形式を持たないため、hikimay 版を通して使うのが現実的。

### 3. iKora128/stop-ai-slop-jp
- ファイル構成が `SKILL.md`（コアルール・採点表）＋ `references/phrases.md`（消すべき語彙）＋
  `references/structures.md`（false agency 等の構造的クセ）＋ `references/examples.md`
  （AI版 vs 修正版の対比）と整理されており、Skill としての完成度は高い。
- 「大げさな見出し」「小さな体験を真理まで膨らませる」など、本プロジェクトの反復回避規約
  （docs/dialogue-guide.md §9 AI らしさの禁止リスト）と重なる指摘が多い。

### textlint 系（比較対象）
- `preset-ja-technical-writing`・`preset-ai-writing`・`preset-JTF-style` はいずれも SKILL.md
  ではなく npm パッケージ（textlint のルールプリセット）。Claude から使うには
  (a) textlint を CLI として `Bash` 経由で叩かせる、または (b) `npx textlint --mcp` で
  MCP サーバー化して `claude mcp add` で接続する、の2通りがある。textlint 公式ドキュメント
  （textlint.org/docs/mcp/）に Claude Code との連携手順が明記されている。
- 3プリセットとも azu 氏（textlint 本体の作者）によるもので、スター数・継続性の面では
  今回調べた中で最も信頼性が高い。ただし「機械的に判定できるルール」が中心で、
  「論証の厳密さ」「出典の明記」「反証の検討」のような本プロジェクトの構造的要件は扱わない。

## 見つからなかった／確認できなかったこと

- **GitHub のコード検索**（`github.com/search?type=code`）はログインを要求され、
  SKILL.md 本文の横断検索ができなかった。そのため「日本語テクニカルライティング」を名乗る
  スキルを網羅できた保証はない。
- WebSearch がセッション中たびたび `unavailable` エラーを返し、有効な検索語でも
  Wikipedia 等の無関係な結果しか返らない試行が複数あった（"claude skills marketplace
  japanese writing" 等）。この間は取りこぼしが発生した可能性がある。
- skills.sh（マーケットプレイス）を紹介する Qiita 記事（hokutoh氏）を確認したが、
  日本語文章作成・校正に特化したスキルの掲載は見当たらなかった。skills.sh 自体を
  直接検索・閲覧できていないため、同サイト内に該当スキルがある可能性は排除できない。
- hikimay/japanese-tech-writing のライセンスは README 表記では MIT だが、GitHub API の
  `license.name` は `"Other"` を返した（LICENSE ファイルの形式が定型と異なる可能性。
  未確認のため利用前に LICENSE ファイル本文を直接確認することを推奨）。
- 各スキルの「利用報告数」「issue の活発さ」は、★数・open issue 数以上の定量情報
  （ダウンロード数、Zenn/note 等での言及数）を取得できていない。npm パッケージ
  （textlint系）はダウンロード数を npm 側で確認できるはずだが、今回は取得していない。
- 対話劇（めたん×ずんだもん）向けの語り口規則との整合性は未検証（今回はナレーション主体の
  台本を前提に調査した）。
