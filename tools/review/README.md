# tools/review — 別モデル・ASRによる自動レビュー

台本執筆フローに「別モデルによる自動レビュー」を組み込むためのツール群（2026-08-27 追加）。
**①台本レビュー**（ナレーション全文の分かりやすさ。GPT）と**②総合レビュー**（面白さ・視聴維持・
見やすさ・タイトルの企画レビュー。GPT。2026-09-01 追加）、**③映像レビュー**（レンダ済み動画の
ビート単位の静止画＋ナレーション＋テロップの検査。GPT）に加え、**④読み上げレビュー**
（レンダ済み音声をASRで文字起こしし、台本テキストと突き合わせて誤読・読み飛ばし候補を検出。
2026-08-28 追加）の4段構成。映像レビューには**決定論的な事前チェック**（ナレーションにない文字が
テロップに出ていないか等）もあり、これは GPT を呼ばずに行う。

いずれのツールも**指摘を生成するだけ**で、台本・YAML の文言は一切編集しない。採否判断と反映は
人／Claude が行う（`DRAFT/CLAUDE.md` の方針どおり）。

## 対話台本（紙芝居版）のレビュー一式

対話台本（めたん×ずんだもん）は、上記に加えて対話特有の観点（セリフの自然さ・章のつなぎ・間の
設計）を持つ。台本執筆〜レンダまでの間、次の順序で回す。

1. `review_script.py`（7観点。ナレーションの分かりやすさ）
2. `review_holistic.py`（総合。面白さ・視聴維持・見やすさ・タイトル）
3. `review_clarity.py`（視聴者の理解と主題への適合。理解度・説明の抜け・主題への適合・直接表現）
4. `review_dialogue.py`（セリフ。自然さ・キャラらしさ・テンポ・表情タグ・面白さ）
5. `review_transitions.py`（章のつなぎ。つなぎの自然さ・予告の具体性・章カードとの整合・反復）
6. `review_pauses.py`（間・息継ぎ。シーン YAML の `pause_after` が対象なので、YAML 生成後に回す）
7. `../preflight.py`（レンダ前の機械チェック一括。読みの突合・長いキュー・板だけの区間・要確認
   文字・ラベル長・素材ファイルの存在）
8. レンダ後に `review_video.py`（映像）と `review_reading.py`（読み上げ・ASR）

## 前提

- Python は script-to-video の venv を使う（Bash の `python` は Microsoft Store のスタブで動かない）。
  ```
  C:\Users\shuya\Projects\script-to-video\.venv\Scripts\python.exe
  ```
  `PYTHONUTF8=1` を必ず付ける。パスはスラッシュ表記＋ダブルクォートで書く。
- Codex CLI（`codex`/`codex.bat`）にログイン済みであること。
  ```
  codex login status
  ```
  未ログインなら `codex login` を対話的に実行する（このツールでは行わない）。
- `review_video.py` は script-to-video のライブラリ（`src/script_to_video`）と ffmpeg を使う。
- `review_reading.py` は Codex CLI を使わない（GPTを呼ばないローカルASRのみ）。必要な追加
  パッケージは `faster-whisper`・`pykakasi`（後述）。
- `../preflight.py` も Codex CLI を使わない。必要な追加パッケージは `fugashi`・`unidic-lite`
  （形態素解析。無ければ `pykakasi` にフォールバック。後述）。

## review_script.py（台本レビュー）

台本 Markdown のシーンごとのナレーション本文を抽出し、7観点（用語の初出順／前振りのない参照／
長文・同音異義／論理の飛躍／同構文の反復／冗長／結論の着地）で GPT にレビューさせる。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_script.py scripts/20260827-cynicism/20260827-cynicism.md
```

- 出力先の既定: `references/{実行日 YYYYMMDD}-{台本フォルダ名}-gptreview.md`（`--out` で変更可）。
- 所要時間: 実測で約100秒（1回の codex exec 呼び出し）。
- 台本 md は「## シーンN: タイトル」〜「\*\*ナレーション\*\*」〜「\*\*画面\*\*」の構造を前提とする
  （`templates/script-template.md` のフォーマット）。「## 付録」以降は抽出対象から除外する。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--out` | `references/{実行日}-{フォルダ名}-gptreview.md` | 出力先パス |
| `--timeout` | 900秒 | codex exec のタイムアウト |
| `--codex-path` | 自動検出 | codex 実行ファイルの明示指定 |

## review_holistic.py（総合レビュー）

台本 Markdown のシーンごとのナレーション本文＋画面欄（テロップ・ビジュアル意図・章タイトル等）を
抽出し、**面白さ・視聴維持・見やすさ・タイトル妥当性**の5観点でGPTに総合レビューさせる
（2026-09-01 追加）。`review_script.py` の7観点（用語初出順など「分かりやすさ」寄り）とは別軸の、
企画レビュー寄りのチェック。codex exe の解決・レート制限リトライ付き codex exec 呼び出し・
台本 md のシーン境界抽出は `review_script.py` の実装を import して再利用している。

先行実験として `references/20260901-dopagaki-holistic-review.md` でアドホックに実行した
カスタムプロンプトをツール化したもの。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_holistic.py scripts/20260827-cynicism/20260827-cynicism.md
```

依頼する5観点:
1. 面白さの総合採点（10点満点）と根拠（冒頭15秒のフックの強さ・中だるみ箇所・決め台詞の効きを
   それぞれ個別採点）
2. 視聴維持の危険箇所（シーン番号＋該当文の引用を必須）
3. 見やすさ（章構成のリズム、図解・画面転換の頻度がナレーションの情報密度と合っているかを
   画面欄から判断）
4. タイトル・サムネ文言の妥当性（10点満点評価＋代案3つ。各代案に根拠となる台本中の文の引用）
5. 改善提案を最低5件、優先度S/A/B/C付きで（全体を褒めるだけの出力は不可）

- 出力先の既定: `references/{実行日 YYYYMMDD}-{台本フォルダ名}-holistic.md`（`--out` で変更可）。
- 所要時間: 目安で約3〜8分（1回の codex exec 呼び出し。`review_script.py` よりプロンプト・
  出力が長いため時間がかかりやすい）。
- 台本 md のシーン境界の前提は `review_script.py` と同じ（`templates/script-template.md` の
  フォーマット。「## 付録」以降は抽出対象から除外）。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--out` | `references/{実行日}-{フォルダ名}-holistic.md` | 出力先パス |
| `--timeout` | 900秒 | codex exec のタイムアウト |
| `--codex-path` | 自動検出 | codex 実行ファイルの明示指定 |

## review_clarity.py（視聴者の理解・主題適合レビュー）

台本 Markdown（対話台本・ナレーション台本の両方に対応）を、**「視聴者がその一文を聞いて理解
できるか」「その段落・逸話が主題にどう寄与するか」**の観点でGPTにレビューさせる
（2026-09-06 追加）。冷笑ずんだもん版で、既存の5種のレビュー（`review_script.py` の7観点・
`review_holistic.py` の総合・`review_dialogue.py` のセリフ・`review_transitions.py` の
つなぎ・`review_pauses.py` の間）を全部通した台本でも、ユーザーの試写で「意味が取れない
一文」「説明の抜け」「主題に寄与しない逸話」「婉曲・比喩の決め文」「論と噛み合わない具体例」
の指摘が出て手戻りになったことへの対応。既存レビューは「表現として自然か」を見ており、
「視聴者が理解できるか」「主題に寄与するか」は見ていなかった隙間を埋める。

対話台本（`**話者**（表情）: 本文` 行がある）と一人語りのナレーション台本（`**ナレーション**`
ブロックのみ）の両方を自動判別して対応する。台本 md のシーン抽出・codex exec 呼び出しは
`review_dialogue.py` / `review_script.py` の実装を import して再利用している。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_clarity.py scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.md
```

依頼する4観点:
1. 理解度（一文ごと。初見の一般視聴者が音声で一度聞いただけで意味を取れるか。指示語の曖昧さ・
   引用の意味の閉じなさを含む）
2. 説明の抜け（主張間の飛躍。分類・因果の理由が示されていない箇所）
3. 主題への適合（タイトルの問いへの各シーンの寄与を判定し、寄与が薄い・無い段落や逸話を削除
   候補として文字数の目安つきで列挙。冒頭の具体例と後半の論が同じ型の対象かも判定）
4. 直接表現（比喩・婉曲・対句の決め文を直接表現に言い直した案。比喩の方が分かりやすいと判断
   した場合はその旨を明記）

- 出力先の既定: `references/{実行日 YYYYMMDD}-{台本フォルダ名}-clarity-review.md`（`--out` で
  変更可）。
- 対話台本・ナレーション台本のどちらも1回の codex exec 呼び出しで全シーンをまとめて渡す。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--out` | `references/{実行日}-{フォルダ名}-clarity-review.md` | 出力先パス |
| `--timeout` | 900秒 | codex exec のタイムアウト |
| `--codex-path` | 自動検出 | codex 実行ファイルの明示指定 |

## review_transitions.py（章のつなぎレビュー）

対話台本 Markdown の各シーンの末尾3発話・次シーンの冒頭3発話・次シーンの章カード
（`- 章カード: 「…」`）の有無を抽出し、**つなぎの自然さ・予告の具体性・章カードとの整合・
反復**の観点でGPTにレビューさせる（2026-09-05 追加）。先行して `references/20260905-dopagaki-kamishibai-transitions-review.md`
でアドホックに実行したカスタムプロンプトをツール化したもの。codex exe の解決・レート制限
リトライ付き codex exec 呼び出し・台本 md のシーン抽出まわりの正規表現は `review_dialogue.py` /
`review_script.py` の実装を import して再利用している（キャラクター設定は `review_dialogue.py`
の版が特定動画向けの記述を含むため流用せず、このツール専用の汎用版を定義している）。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_transitions.py scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.md
```

依頼する観点:
(a) つなぎの自然さ (b) 予告の具体性 (c) 章カードとの整合 (d) 境界ごとの判定（可・要修正）
(e) 反復チェック（「次は〜」等の予告構文が3回以上同じ型で連続・多発していないか）

- 出力先の既定: `references/{実行日 YYYYMMDD}-{台本フォルダ名}-transitions-review.md`
  （`--out` で変更可）。
- 全境界（シーン数-1）を1回の codex exec 呼び出しにまとめて渡す。
- 対話台本 md の書式（`## シーンN: タイトル` ＋ `**話者**（表情）: 本文`）は `review_dialogue.py`
  と同じ前提。`## 出典リスト` 以降は抽出対象から除外する。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--out` | `references/{実行日}-{フォルダ名}-transitions-review.md` | 出力先パス |
| `--timeout` | 900秒 | codex exec のタイムアウト |
| `--codex-path` | 自動検出 | codex 実行ファイルの明示指定 |

## review_pauses.py（間・息継ぎレビュー）

シーン YAML（`scenes[].narration[]`）の `text` / `speaker` / `pause_after` を抽出し、
**間が足りない／長すぎる箇所・決め文の後の保持・話者交代の間・章転換・息継ぎ位置（文の分割）**
の観点でGPTにレビューさせる（2026-09-05 追加）。先行して
`references/20260905-dopagaki-kamishibai-pause-review.md` でアドホックに実行したカスタム
プロンプトをツール化したもの。codex exe の解決・レート制限リトライ付き codex exec 呼び出しは
`review_script.py` の実装を import して再利用している。

台本 md ではなく**シーン YAML** が入力（`pause_after` は YAML にしかないため）。台本を対話
形式に組んだ後、`tools/kamishibai_md_to_yaml.py` で YAML を生成してから実行する。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_pauses.py scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.yaml
```

- `--tempo`（既定 `1.1`）でプロンプトに提示する `pause_after` の基準値が変わる
  （`tools/kamishibai_md_to_yaml.py` の `PAUSE_PRESETS` と同じ値: 1.1倍のとき話者交代0.45秒・
  文境界0.35秒・章転換1.2秒。決め文の目安2.0〜2.5秒は話速に依らず本作の設計判断として
  提示する）。
- 出力先の既定: `references/{実行日 YYYYMMDD}-{台本フォルダ名}-pause-review.md`（`--out` で
  変更可）。
- 全シーンの `pause_after` を1回の codex exec 呼び出しにまとめて渡すため出力が長くなりやすい。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--tempo` | `1.1` | 想定話速（`1.0`/`1.1`）。プロンプトに提示する `pause_after` の基準値が変わる |
| `--out` | `references/{実行日}-{フォルダ名}-pause-review.md` | 出力先パス |
| `--timeout` | 900秒 | codex exec のタイムアウト |
| `--codex-path` | 自動検出 | codex 実行ファイルの明示指定 |

## review_video.py（映像レビュー）

レンダ済み動画から各ビート（`beats[]` の image/diagram/typo/chapter）の代表フレームを ffmpeg で
静止画抽出し、対応するナレーション・テロップ・visual_intent とともに (a) 決定論チェック、
(b) GPT 画像レビューを行う。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_video.py ^
    scripts/20260827-cynicism/20260827-cynicism.yaml ^
    C:/Users/shuya/Projects/script-to-video/build/cynicism-v2-codex ^
    --scenes 3,5
```

- YAML パス（レンダに使ったもの）と、レンダ出力ディレクトリ（`timeline.json`・完成 MP4 がある場所）
  の2つが必須引数。
- `--timings-dir` 省略時は `<出力dir>/audio/`。無ければエラーになるので明示する。
- `--mp4` 省略時は `<出力dir>` 直下の唯一の `*.mp4`。`preview_360p.mp4` 等が同居していて複数
  ヒットする場合は明示が必須（レンダ出力ディレクトリには本編 MP4 以外にプレビュー用 MP4 が
  複数入っていることが多い）。
- `--scenes 1,3` でシーンを絞れる（省略時は全シーン。動画1本フルで回すと GPT 呼び出しが
  多数になるため、まず絞って試すことを推奨）。
- `--skip-gpt` を付けると静止画抽出と決定論チェックだけを行う（GPT 呼び出しなし。動作確認・
  静止画の見た目チェックに使う）。
- 静止画は `<出力dir>/review/stills/sNN_bMM_<type>.jpg`（幅960px）、最終レポートは
  `<出力dir>/review/video-review.md` に保存する。

### 決定論チェック（GPTを呼ばない）

- **区分A「ナレーションにない文字」**（捏造検出・原則要対応）: 各ビートの `telop` が、そのシーンの
  ナレーション本文に**部分文字列として含まれない**、かつ出典表記らしいパターン（年の括弧・
  `et al.`・『』・英字の固有名詞列）にも数値＋単位（%・人・件など）にも該当しない場合に列挙する。
  telop が「読み上げていない・出典でも数値でもない」独自の文言になっている＝捏造・誤情報の
  リスクがあるため、原則対応が必要な指摘として扱う。
  - 注意: このチェックは「telop が実際に読み上げられた文言の一部かどうか」だけを見る単純な部分
    文字列マッチであり、「そのテロップを画面に出す設計が適切か」までは判定しない。
- **区分B「字幕の写し」**（要判断）: telop がナレーション本文の一部と**一致し**、かつ数値・英字の
  固有名詞・章の区切り記号（「：」「／」）のいずれも含まない場合に列挙する。ナレーション（字幕）
  と同じ日本語文をそのまま別枠で大きく出しているだけ＝情報として無駄になっている疑いがある、
  というユーザーの意図（「同じ言葉を別枠で大きく出すのは無駄」）に基づくチェック。ただし
  問いの強調表示のような意図的なケースもあるため、問題として断定せず**要判断の一覧として
  列挙するだけ**にする（例: `20260827-cynicism.v1.yaml.bak` シーン3の telop
  「人間を探している」はナレーションの引用と完全一致するため区分Bに列挙される）。
- **同一telopの10秒以内再出現**: 動画全体を通して、同じテロップ文言が10秒以内に2回以上出ていないか。
- **20秒超のimageビート**: 一枚絵の保持が20秒を超えているビート（`validate` の警告と重複してよい）。

### GPT 画像レビュー

`--per-call`（既定6枚）ごとに codex exec へ画像をまとめて渡し、次の7観点で表（画像／問題種別／
説明／推奨）を出させる: ①ナレーション・出典以外の読める文字 ②顔のクローズアップ・正面の顔
③画とナレーションの不一致 ④二者比較/before-after の1枚描写 ⑤字幕・テロップのはみ出し・重なり
⑥画風の不統一 ⑦意図しない含意。問題なしの画像は表から省略される。

**指摘の粒度**（2026-08-28 ユーザー指示）: 画像は「大きい視点で間違っている」場合だけ指摘させる（別の場面を描いている／時代・場所が明らかに違う／読める偽文字が目立つ／正面の顔が大きい／誤解を招く含意が明白）。プロンプトとの逐語差・小物・人数・姿勢・照明のわずかな差・改善提案の類は報告させない（プロンプト内 `GPT_SCOPE_RULES`）。⑤の物理的な崩れだけは細かくても報告対象。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--timings-dir` | `<出力dir>/audio` | timing json の場所 |
| `--mp4` | `<出力dir>` 直下の唯一の `*.mp4` | 完成 MP4 のパス |
| `--scenes` | 全シーン | カンマ区切りのシーン番号フィルタ |
| `--per-call` | 6 | 1回の codex 呼び出しに載せる画像数 |
| `--skip-gpt` | off | GPT呼び出しを省略（決定論チェックのみ） |
| `--timeout` | 900秒 | codex exec 1回あたりのタイムアウト |
| `--ffmpeg-path` / `--codex-path` | 自動検出 | 実行ファイルの明示指定 |

## review_reading.py（読み上げレビュー・ASR）

レンダ済みナレーション音声を faster-whisper（ローカルASR）で文字起こしし、台本（シーン YAML の
`narration[]` 各セグメント）と突き合わせて、漢字の誤読・読み飛ばしの**候補**を列挙する。GPT・
Codex は使わない（ローカルモデルのみ・ネットワークは初回のモデルDLのみ必要）。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_reading.py ^
    --yaml scripts/20260827-cynicism/20260827-cynicism.yaml ^
    --audio-dir C:/Users/shuya/Projects/script-to-video/build/cynicism-audio-rev4 ^
    --model small
```

- `--audio-dir`（`scene_NN.wav` + `scene_NN.timing.json` のディレクトリ。TTS生成時にツールが
  書き出すセグメント別タイミング）を使うのが**最も精度が高い**方式（セグメント単位で比較できる）。
  無い場合は `--mp4`（+ 同ディレクトリの `timeline.json`）でシーン単位の粗い突き合わせに
  フォールバックする。
- 出力先の既定: `references/{実行日}-{台本フォルダ名（先頭の "YYYYMMDD-" は除去）}-reading-check.md`
  （`--out` で変更可）。
- モデルは `--model`（既定 `small`）。GPU無し・CPU・int8前提。`small` は実測で音声の約0.2〜0.26倍の
  処理時間（19分の音声で約5分）。`medium` はより正確な傾向もあるが誤りもあり（後述）、CPUで
  約0.57倍（同19分で約11分）。初回はHugging Face Hubからのモデルダウンロードが入る。
- 台本テキストとASR出力は**ひらがな化して比較する**（`pykakasi`。2026-08-28 改訂）。台本側は
  YAML の `readings`（読み修正指定語）を先に適用してからひらがな化する（＝指定読みで発音
  されているかの検証を兼ねる）。数字は算用数字を漢数字表記に揃え、「％」は「パーセント」に
  揃えてからひらがな化することで、台本とASRのどちらが数字/漢数字・記号/カナのどちらで
  書いていても比較できるようにしている。ひらがな化した文字列どうしを `difflib.SequenceMatcher`
  で比較し、**一致率が閾値未満**（既定 `--threshold 0.85`）のセグメントだけを「要確認」として
  列挙する。「嗤う／笑う」「芥子／消し」のような**同音の別漢字**はこの時点で一致扱いになり、
  要確認からは外れる（漢字表記だけが違う箇所は末尾の参考表に回る）。
- YAML の `readings`（読み修正指定語）については、指定読み（カタカナ）をひらがな化した文字列
  が、該当セグメントのASR出力をひらがな化した文字列に含まれるかを別表に示す（発音そのものの
  検証。区間の「かな一致率」もあわせて表示）。
- `--scenes 1,3` でシーンを絞れる。

### 精度の所感・限界（2026-08-28、冷笑動画で実施）

**漢字表記レベルの比較（旧方式）→ かな比較（現方式）で要確認が146件→28件に減少**（全225
区間中。閾値は旧0.9→新0.85）。漢字表記レベルの比較では同音異字を誤検出として大量に拾って
しまい実用にならなかったため、ひらがな化して比較する方式に切り替えた。かな比較でも一致率が
閾値以上になったが漢字表記だけが違う箇所は97件あり、末尾の参考表に回している（例:
「嗤う→笑う」「冷笑→礼償」「賭ける→欠ける」など、いずれも対応不要）。

- 残った28件を目視で分類したところ、**明確な誤読と断定できるものは無かった**。内訳:
  - **境界ズレ**（短い区間・連続区間でのASR単語タイムスタンプのずれによる語頭の脱落や
    隣接区間からの文字の漏れ）: 半数程度。例:「売名だ。」→「名だポ」（次区間「ポーズだ。」の
    頭が漏れて自区間の「売」が欠落）、「ただし、」→「ただし付」（次区間「付け加えて」の頭が
    漏れた）。
  - **ASRの誤認識**（低信頼度な当て推量による別語への変換、外国人名の音写ゆれ、ごく近い
    音の聞き違い）: 残りの大半。例:「デイヴィッド→デイビット」「スラヴォイ→スラボイ」
    （外国語カタカナの音写ゆれ）、「見下されて→見下ろされて」（活用の言い換え）、
    「どうせ→同性」（近い母音の聞き違い）。
  - **`pykakasi`（かな化ツール）自体の読み崩れ**: ASRが選んだ漢字の組み合わせが辞書に無い
    非標準の熟語（「霊笑」「完修」「傍」の単独読み等）だと、`pykakasi` が文脈に合わない読み
    （音読み／訓読みの取り違え）を返し、実際には近い発音でも不一致に見えることがある。
    例:「冷笑」→ASR「霊笑」は音としては「れいしょう」に近いはずだが、`pykakasi` が「笑」を
    単独の訓読み「わら」で読んでしまい一致率を下げている。
  - **読みが明確に異なり要リスニング確認とした箇所（4件、いずれもASRの当て推量と判断）**:
    「冷笑」→ASR「冷凍」（れいしょう→れいとう。シーン8区間17・シーン11区間18の2箇所で
    独立に出現）、「身体」→ASR「神田」（しんたい→かんだ。シーン4区間14）、
    「一行」→ASR「一向」（いちぎょう→いっこう。シーン4区間21）。「冷笑」は他の約15箇所
    すべてで「れいしょう」に近い誤変換（霊晶・礼償等）に留まっており、この2箇所だけ
    まったく別の実在語に変換されている。TTS側の一貫した誤読なら毎回同じ間違い方をするはずで、
    出現のたびに異なる誤変換をしている時点でASRの低信頼度な当て推量である可能性が高いが、
    断定はできないため要リスニング確認として残した。
- `readings` で読み修正した語（嗤う/冷笑/芥子/北田暁大 等）は、ASR出力を見る限り**指定した
  読み通りに発音されている**ことが確認できた（例: 「芥子」→ASR「消し」＝けし。指定読み
  「ケシ」と一致。「北田暁大」→ASR「北田明広」＝あきひろ。指定読み「アキヒロ」と一致）。
  表記こそ違うが、これはASRが常用の同音漢字を選んだだけで、発音の誤りではない。
- **シーン6区間9「冷笑→名称」**（かな比較導入のきっかけになった箇所）は、かな一致率
  0.94（閾値0.85以上）で要確認からは外れ、参考表（かなは一致するが漢字表記が異なる箇所）に
  回った。ただし「名称」の読み（めいしょう）は「冷笑」の読み（れいしょう）と厳密には異なり、
  この1語だけ見れば同音ではない。区間全体（「〜の第二の安さは、何もしなくても、賢い側に
  立てることだ」）が長く、他の部分は一致しているため区間全体としての一致率は閾値を超えた
  （＝長い区間内の1箇所の不一致は薄まって見えにくくなる、という副作用でもある）。
- セグメント境界の精度限界は上記「境界ズレ」のとおり残っている。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--audio-dir` | なし | セグメント別 wav + timing.json のディレクトリ（最も精度が高い） |
| `--mp4` / `--timeline` | なし / `--mp4` と同じディレクトリ | `--audio-dir` が無い場合のフォールバック |
| `--out` | `references/{実行日}-{フォルダ名}-reading-check.md` | 出力先パス |
| `--model` | `small` | faster-whisperのモデル名（`small`/`medium` 等） |
| `--device` / `--compute-type` | `cpu` / `int8` | ASR実行環境 |
| `--threshold` | `0.85` | かな一致率の閾値 |
| `--scenes` | 全シーン | カンマ区切りのシーン番号フィルタ |

## ../preflight.py（レンダ前の機械チェック一括）

紙芝居モード（めたん×ずんだもん）のシーン YAML を、**レンダ前**に一括で検査するツール
（`tools/preflight.py`。GPT・Codex は使わない）。冷笑ずんだもん版（2026-09-05〜06）の試写
10回のうち4回が機械的に検出できる不具合（誤読・板だけの区間の間延び・フォントで描けない
文字）だったことを受けて追加した（2026-09-06）。`review_reading.py` はレンダ済み音声を ASR で
検証する事後チェックだが、こちらは VOICEVOX の `audio_query` を直接叩くため ASR を通さず
決定的（レンダ自体が不要）。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/preflight.py ^
    scripts/20260905-cynicism-kamishibai/20260905-cynicism-kamishibai.yaml ^
    --assets-dir C:/Users/shuya/Projects/assets-kamishibai/render-assets-cynicism ^
    --out references/20260906-cynicism-kamishibai-preflight.md
```

6項目を1コマンドでまとめて検出し、Markdown レポートを標準出力＋（`--out` 指定時）ファイルへ
出す。該当があれば終了コード1。

1. **読みの突合**（最重要）: narration の各セグメントを VOICEVOX の `/audio_query` に投げ、
   返る実際の読み（kana）を、**fugashi（MeCab + unidic-lite。形態素解析）**によるテキストの
   あるべき読みと比較する（2026-09-06、pykakasi から差し替え。pykakasi は形態素解析器では
   なく漢字→かな変換ツールに過ぎず、「力→りき」「断った→た」「棘→なつめ」「優れ→まさ」の
   ような複合語・活用語の読み取り違いが差分の大半を占め実運用で埋もれていたため）。fugashi
   が import できない環境（未インストール等）でのみ pykakasi にフォールバックする。差分候補を
   `VV:実際の読み/辞書:あるべき読み` の形式で列挙する。事前に YAML の `readings` を VOICEVOX の
   ユーザー辞書へ登録してから比較する（レンダ時と同じ状態で検証するため）。数字・英字略語
   （SNS・OECD 等。fugashi・pykakasi のどちらもかな化できない）は既知ノイズとして除外する
   （助詞「は」「を」の表記と発音の違いは fugashi の発音〔`pron`〕がそのまま解決するため
   除外不要になった。pykakasi フォールバック時のみ「人」のひと／にん／じん のゆれを除外する）。
   それでも fugashi 自身の誤読（辞書に無い複合語の読み違え等。例:「一段上」→ジョウ。実際は
   ウエ）や同音異字は残るため、指摘の採否は人／Claude が目視で判断する（`review_reading.py`
   と同じ位置付け）。`--skip-tts` でこの項目だけ飛ばせる（VOICEVOX未起動の環境向け）。
2. **長いキュー**: 字幕キュー（`。！？` 区切りの1文）が50字を超えるもの（字幕は2行までで
   末尾が切れる）。
3. **板だけの区間**: `board` ビート（黒板・人形だけの区間）の推定尺が10秒を超えるものを列挙
   （参考として `image`/`diagram` の45秒超も別枠で列挙）。
4. **テロップ・図解ラベルの文字**: telop・図解ラベルに en dash（–）等、紙芝居の黒板テロップ
   フォント（UD デジタル教科書体系）で描けない可能性のある文字が無いか（2026-09 に
   「1983–84」の en dash が □ になった実例あり）。矢印「→」・丸数字「①」等は既に複数の
   公開動画で常用されレンダ実績があるため対象外にしている。
5. **ラベル長**: sketch/narrative の要素ラベルが仕様上限を超えるもの（`validate` でも弾かれる
   が、まとめて見たいという要望に応えるもの）。
6. **写真ファイルの存在確認**: `--assets-dir` 指定時、`image` ビートの採用素材
   （`scene_NN_beat{slot}.*`）が全部揃っているか。

### 主なオプション

| オプション | 既定 | 説明 |
|---|---|---|
| `--assets-dir` | なし | 採用素材ディレクトリ（項目6用。省略時は項目6をスキップ） |
| `--out` | なし（標準出力のみ） | Markdown レポートの保存先 |
| `--skip-tts` | オフ | 項目1（VOICEVOX突合）を飛ばす |
| `--voicevox-url` | `http://127.0.0.1:50021` | VOICEVOX ENGINE の base URL |
| `--selftest` | — | 軽量な自己テスト（長いキュー検出・ダッシュ検出・助詞変換・数字/英字マスク）を実行して終了する |

## review_short.py（ショート映像レビュー）

レンダ済みショート動画（TTS専用YAML＋完成mp4）を、ナレーションセグメント単位の静止画で GPT
レビューさせるツール（2026-08-28 追加）。ショートは `beats[]` を持たない TTS専用の最小 YAML
（`narration[]` のみ）で作られるため、シーン・ビート単位ではなく `narration[]` の各セグメントを
単位にする。`scene_id=1`・`beat_num`=セグメント番号（1始まり）として `BeatRecord` を組み立て、
`review_video.py` の `BeatRecord` / `build_gpt_prompt` / `run_gpt_review`（`GPT_SCOPE_RULES` 込み）
をそのまま再利用する。

```
cd C:\Users\shuya\Projects\draft-explanation-video
PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
    tools/review/review_short.py ^
    --yaml C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/short-tts.yaml ^
    --mp4 C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/short.mp4 ^
    --timings-dir C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/audio ^
    --out C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/review/video-review.md
```

- `--yaml` / `--mp4` / `--timings-dir` / `--out` は必須（review_video.py と異なり出力先の既定値は
  無い。ショートのビルドディレクトリは動画ごとに違う場所を使うため明示させる設計）。
- ショートには `telop` が無いため、**決定論チェック（区分A/B・同一telop再出現）は実施しない**。
  GPT観点は review_video.py と同じ7点（うち⑤字幕・テロップの物理的な崩れは細かくても報告対象、
  `GPT_SCOPE_RULES` 準拠。粒度は「大きい視点で間違っている場合だけ指摘」）。
- 静止画は `<--out の親ディレクトリ>/stills/segNN.jpg`（幅960px、各ナレーションセグメントの
  start/end中間時刻）に保存する。
- `--skip-gpt` で静止画抽出だけ行う（GPT呼び出しなし・動作確認用）。
- `--per-call`（既定6）・`--timeout`（既定900秒）・`--ffmpeg-path`・`--codex-path` は
  review_video.py と同じ意味。

## クォータ・失敗時の挙動

Codex CLI は ChatGPT Plus 契約のクォータで動く。「usage limit」「at capacity」等のレート制限
文言を検知すると、両ツールとも**60秒待って1回だけ自動再試行**する。それでも失敗する場合は
エラーとして終了する（`review_video.py` の GPT 画像レビューはバッチ単位で失敗しても続行し、
失敗したバッチは `video-review.md` に「未レビュー」として記録される）。

1回の codex exec 呼び出しは1〜3分程度かかる。動画1本フルで映像レビューを回すと、ビート数×
呼び出し回数ぶん時間がかかる点に注意する（まず `--scenes` で絞ることを推奨）。

## 台本・動画リポジトリ内の位置付け

- `.claude/commands/review.md`（`/review`）から呼び出す想定。
- `CLAUDE.md`「ワークフロー（コマンド）」に `/review` の説明がある。
