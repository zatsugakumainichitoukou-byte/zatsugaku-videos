# 雑学太郎 毎日投稿 手順書（スケジュール実行用）

YouTubeチャンネル「雑学太郎」（チャンネルID: UC5btyvlkpQWNlyMhDj2I6Rg）に、毎日19時ごろ
**横動画（本編）1本＋その一部を切り出したショート1本**を公開する。人の確認なしで最後まで実行する。

## 0. 準備
1. このリポジトリが無ければ `mcp__claude-code-remote__add_repo`（owner: zatsugakumainichitoukou-byte, repo: zatsugaku-videos, access: push）→ 指示どおり clone。
2. `pip install --break-system-packages -q edge-tts numpy pillow`
3. `topics.json` を読み、過去に扱ったテーマ・雑学を把握する。

## 1. 日替わりの組み合わせを決める（量産型に見せないため）
`topics.json` の直近の記録を見て、**前日と同じものを避けて**次の3つを選ぶ（同じ組み合わせが直近7日に無いように）。
- **見た目** `style`: `pastel` / `night` / `note` / `pop`
- **声** `voice_preset`: `nanami` / `nanami_calm` / `keita` / `keita_bright`
- **構成** `format`（直近3日と同じものは避ける）:
  - `5選` … 「その1〜その5」。各雑学2シーン。
  - `クイズ` … 「第1問〜第5問」。1シーン目で問題を出し「3秒で考えてみてください」と言い、そのシーンに `"pause": 3` を付ける（captionは問題文だけにする）。2シーン目で「正解は…」と解説。
  - `ランキング` … 「第5位〜第1位」の順に、意外度などの基準を最初に宣言して紹介。
  - `本当？ウソ？` … 「1つ目〜5つ目」。それっぽい説を言い、2シーン目で本当かウソかを明かして理由を説明（ウソの説も、世間でよく信じられている誤解に限る。でっち上げはしない）。
  - `深掘り` … 1つのテーマ（例：「なぜ空は青い？」）を5段階で掘り下げる。tagは「ステップ1〜5」。
- tag の文言は構成に合わせて変える。`short.segment` はそのtagの値を指定する。

## 2. 台本づくり（毎回いちばん手をかける工程）
- テーマを1つ決める（食べ物／動物／人体／宇宙／日本語／歴史／生活用品／地理 など。直近7日と同じジャンルは避け、過去と同じ雑学は使わない）。
- 雑学を5つ選ぶ。**1つずつWebSearchで裏付けを取る**。確認できないもの・俗説・諸説あるものは使わない（使うなら「〜という説があります」と明示）。
- 医療・お金・事件など繊細な話題、実在の人物の噂話、ネガティブで不快な内容は扱わない。
- 毎回、冒頭のつかみ・言い回し・タイトルの型を変える。前日までと同じ構成文を使い回さない（YouTubeの「量産型コンテンツ」判定を避けるため）。
- `scripts/YYYYMMDD.json` を作る。形式は `scripts/food5.json` と同じ:
  - `slug`: `YYYYMMDD`、`channel`: `雑学太郎`、`style`、`voice_preset`、`format`（上で決めたもの）
  - `scenes`: 導入1＋各ネタ2シーン×5＋まとめ1（深掘りは各ステップ1〜2シーン）。各シーンに `tag`（構成に合わせた文言／"まとめ"）、`theme`（同じtagは同じ番号0〜5）、`heading`（15字前後）、`emoji`（1文字）、`say`（ナレーション。1シーン60〜110字）。
  - `thumbnail`: text（20字以内）, sub, emoji, tag
  - `short`: 5つのうち**いちばん意外な雑学**を `segment` に指定。`hook`（「〜って知ってましたか？」型のつかみ）と `outro`（続きは本編へ誘導）を書く。切り出すパートの1シーン目が「ふたつめは〜」等で始まる場合は `say_short` を付ける。
  - 「まとめ」シーンの呼びかけはYouTube・TikTok共通で使うので、「チャンネル登録」「フォロー」など特定のSNSの言葉は使わない（例：「毎日ひとつ雑学をお届けしています。また明日！」）。
  - タイトル・説明文・タグ（long と short それぞれ）。説明文の最後に必ず「※この動画はAIツールを使って制作しています。」を入れる。ショートのタイトル末尾に `#雑学 #shorts`。

## 3. 動画の生成
```
python3 pipeline/make_video.py scripts/YYYYMMDD.json out --frames   # 静止画チェック
```
`out/work_long/` と `out/work_short/` のJPGを数枚 Read で目視し、文字のはみ出し・不自然な改行（行頭の「」」「ゃ」、行末の「「」など）や、見出しが単語の途中で折り返していないか確認。気になる場合は見出しを短くする。問題があれば台本の文言を直す。
```
python3 pipeline/make_video.py scripts/YYYYMMDD.json out
```
出力: `out/YYYYMMDD_long.mp4`, `out/YYYYMMDD_short.mp4`, `out/YYYYMMDD_tiktok.mp4`（本編と同じ内容の縦型・TikTok用）, `out/YYYYMMDD_thumb.png`
- TikTok版は収益化（Creator Rewards）の対象になるよう**必ず61秒以上**にする。WARNINGが出たら台本のシーンを足して作り直す。

## 4. 公開用URLの用意
動画ファイルは main に入れない。別ディレクトリで孤立ブランチ `upload-YYYYMMDD` を作り、4ファイル（long / short / tiktok / thumb）だけをコミットして push する。
URL: `https://raw.githubusercontent.com/zatsugakumainichitoukou-byte/zatsugaku-videos/upload-YYYYMMDD/<ファイル名>`

## 5. YouTubeへ投稿（Zapier の YouTube: selected_api `YouTubeV4CLIAPI`）
1. 横動画: `upload_video`（privacy_status: public, category_id: "27", default_language/default_audio_language: "ja", made_for_kids: "false"）。返ってきた動画IDを控える。
2. サムネ: `upload_video_thumbnail`（video_id, thumbnail=サムネURL）。
3. ショート: `upload_video`（privacy_status: public, made_for_kids: "false"）。説明文の1行目付近に「▶本編はこちら https://www.youtube.com/watch?v=<横動画ID>」を入れる。
4. 失敗したら1回だけ再試行。それでも失敗したら、そこで止めて内容を報告する。

## 6. 記録
- `topics.json` に `{"date", "theme", "format", "style", "voice_preset", "facts":[...], "long_id", "short_id"}` を追記。
- `scripts/YYYYMMDD.json` と `topics.json` を main にコミットして push（`git -c push.negotiate=true push origin main`）。
- 最後に、タイトル2本・動画URL2本・扱った雑学の一覧を短く報告する。

## 7. Instagramリール・TikTokへの転載（Metricool、月20投稿を使い切る）
Metricool（blogId: `8198074`）の無料枠は**月20投稿**。リールとTikTokを別々の投稿として数え、**毎月ちょうど10回ずつ（計20）**、月内に均等に出す。
1. `getBrandSettings` で instagram と tiktok が接続済みか確認。どちらも未接続ならこの章は飛ばす（片方だけなら、その1つで月20回を目標にする）。
2. `sns_log.json` から今月の転載回数 `n`（日本時間の暦月）を数える。目標 `N`=10（片方だけなら20）、今日が月の `d` 日目、月の日数 `D` として、**`n < ceil(N × d / D)` のときだけ**今日転載する。`n >= N` なら絶対に転載しない。
3. 転載する動画は、**Instagramは今日のショート**（`YYYYMMDD_short.mp4`）、**TikTokは今日のTikTok版**（`YYYYMMDD_tiktok.mp4`、本編と同じ内容の縦型・1分以上）。どちらも `upload-YYYYMMDD` ブランチの raw URL。
4. `createScheduledPost` を**ネットワークごとに1件ずつ**作る。公開日時は今日の20:00（timezone `Asia/Tokyo`）。
   - Instagram: providers `[{"network":"instagram"}]`、`instagramData`: `{"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`。キャプションは2〜3行＋改行＋ハッシュタグ5〜8個（#雑学 #豆知識 ほか内容に合うもの）＋「YouTubeで本編公開中」。
   - TikTok: providers `[{"network":"tiktok"}]`、`tiktokData`: `{"privacyOption":"PUBLIC_TO_EVERYONE","isAigc":true,"title":"<短いタイトル>"}`。キャプションは1〜2行（雑学5つが入ったフル版だと分かるように）＋ハッシュタグ3〜5個。
   - 文面はYouTubeのコピペにせず、各SNS向けに書き分ける。
5. 投稿上限などのエラーが出たら再試行せず、その旨を記録して報告する。
6. `sns_log.json` に `{"date","short_id","instagram":true/false,"tiktok":true/false}` を追記して main に push。
