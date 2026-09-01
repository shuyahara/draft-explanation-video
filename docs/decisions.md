本書は CLAUDE.md から 2026-08-26 に切り出した参照資料（Issue #15）。規則の正本は CLAUDE.md、
本書は日付・R番号・実測値・試写FB に基づく判断の索引（詳細な逐語本文は各 docs/*.md 側に残る。
本書はそれらを時系列でたどるための索引であり、内容そのものの正本ではない）。

| 日付 | 決定 | 根拠 | 関連（Issue/R番号） | 所在 |
|---|---|---|---|---|
| 2026-08-14 | HeyGen 運用を凍結。新規台本は script-to-video 向けに執筆する | 自作レンダリングツールへの移行 | — | docs/legacy-heygen.md, CLAUDE.md 冒頭 |
| 2026-08-24 | 台本のナレーション本文はオーケストレーター（Fable）本人が執筆・改稿する（グローバル設定の「執筆はワーカー委譲」より優先） | ユーザー指示 | — | CLAUDE.md「このプロジェクトでの Claude の役割」 |
| 2026-08-24 | 研究・分析・調査紹介時は実施機関と実施者をなるべくナレーション本文で明記する（大学名に権威がある場合は必須） | ユーザー指示 | — | CLAUDE.md「引用・ファクトの扱い」 |
| 2026-08-26 | 標準話者を Google Cloud TTS Chirp3 HD の Enceladus に採用 | 聴き比べの経緯（../references/ の TTS 調査メモ） | #14 | docs/narration-style.md, docs/legacy-heygen.md |
| R19 | 画面様式は生成AIの一枚絵（`image` ビート）を主役に据え、構造的な主張の場面だけ `diagram` ビートに切り替える | ベンチマーク検証 | R19 | docs/diagram-guide.md |
| R19.6 | `gen_prompt` を先・`video.style` を後に連結する順へ反転 | 様式強制句を先頭に置くと主題への追従が弱くなることを実測 | R19.6 | docs/asset-workflow.md |
| R19.12 | ビート境界は字幕キュー（≒文）境界にしか置けない。長い1文は執筆段階で2文に分ける | 実台本検証で後から分割不能と判明 | R19.12 | docs/beat-guide.md |
| 2026-08-19 | 顔のクローズアップは写実調へ様式崩れしやすい | 型検証 | — | docs/asset-workflow.md（参照: ../references/20260819-genprompt-type-validation.md） |
| R20 | `pause_after` 省略時のセグメント境界は前後無音マージン由来の短い間（VOICEVOX実測で約0.26〜0.29秒）のみ。文境界分割時は最低0.2秒を明示する | 文間無音実測 | R20 | docs/narration-style.md（参照: ../references/20260820-narration-gap-fix.md） |
| 2026-08-25 試写FB | 図解の採用テストと反復抑制を最上位規則として導入（「見て初めて増える情報」判定・同型上限・背景付きを既定に反転等） | 試写フィードバック | — | docs/diagram-guide.md |
| 2026-08-25 試写FB | 説明イラストで対立・議論・関係そのものが主題の場面は、静物メタファーへの言い換えを既定にせず主題を直接描く情景をまず検討する（婉曲に寄せすぎない） | 試写フィードバック・次回作からの宿題 | — | docs/asset-workflow.md |
| 2026-08-25 試写FB | 説明イラスト再生成3回目に入りそうな場合の converge への機械的切替を廃止 | 試写フィードバック | — | docs/asset-workflow.md |
| R25-1 | typo ビートを新規台本で使う場合は slot 指定または直前 image 素材の自動流用を既定にする | — | R25-1 | docs/diagram-guide.md |
| R25-2 | 図解の同型・同一 layout 反復にリント警告。図解総数目安は10分あたり5〜6箇所 | validate 側の同型反復リント | R25-2 | docs/diagram-guide.md |
| 2026-08-25/26 試写FB | 決め文の文字カット（emphasis＋typo）を新規台本では使わない。決め文は画面保持＋`pause_after` 2.0〜2.5秒の間で演出する | 大文字表示の機械感を避ける | — | docs/beat-guide.md |
| 2026-08-26 | アウトロは `--outro-seconds 8` を標準とする | 既定4秒では余韻が短い | — | docs/beat-guide.md |
| 2026-08-26 | 「シック」を既定にせず、台本着手時に話題に合わせてトーン（雰囲気・方向性）を決め、語り口・画風・BGM・演出をそれに沿わせる | ユーザー指示（話題によってはシックでなくてよい） | #16 | CLAUDE.md「トーン設計」, templates/script-template.md |
| 2026-08-31 / R27 | radiate の光の輪（halo）を既定装飾から `ornament` オプションに変更（既定は装飾なし。halo は題材が輪の比喩を持つ図解でのみ明示指定） | 試写FB（ドーパミン信号の図に無意味な輪が出た）。演出はテーマ・シーンに合わせて選ぶというユーザー方針 | #20 | script-to-video R27, docs/diagram-guide.md |
| 2026-09-01 | 非公開動画の修正アップロード運用: 新バージョンのアップロード後、新IDの再生確認が取れ次第、修正前の非公開動画は YouTube 上から削除する（旧IDと削除の記録は publish/{動画}/title-candidates.md に残す。ローカル mp4 は build/ に保持） | ユーザー方針（非公開版の氾濫防止） | #20 | publish/ 運用 |
