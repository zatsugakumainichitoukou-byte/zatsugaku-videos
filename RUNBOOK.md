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
  - `10選` … 「その1〜その10」。
  - `クイズ` … 「第1問〜第10問」。1シーン目で問題を出し「3秒で考えてみてください」と言い、そのシーンに `"pause": 3` を付ける（captionは問題文だけにする）。2シーン目で「正解は…」と解説。
  - `ランキング` … 「第10位〜第1位」の順に、意外度などの基準を最初に宣言して紹介。
  - `本当？ウソ？` … 「1つ目〜10個目」。それっぽい説を言い、2シーン目で本当かウソかを明かして理由を説明（ウソの説も、世間でよく信じられている誤解に限る。でっち上げはしない）。
  - `深掘り` … 1つの大きなテーマ（例：「なぜ空は青い？」）を8〜10段階で掘り下げる。tagは「ステップ1〜10」。
- tag の文言は構成に合わせて変える。`short.segment` はそのtagの値を指定する。

## 2. 台本づくり（毎回いちばん手をかける工程）
- テーマを1つ決める（食べ物／動物／人体／宇宙／日本語／歴史／生活用品／地理 など。直近7日と同じジャンルは避け、過去と同じ雑学は使わない）。
- **本編は8〜10分**にする（YouTubeの再生時間を稼ぎ、8分以上で動画の途中に広告を入れられるようにするため）。そのため雑学は**10個**選ぶ。**1つずつWebSearchで裏付けを取る**。確認できないもの・俗説・諸説あるものは使わない（使うなら「〜という説があります」と明示）。
- 医療・お金・事件など繊細な話題、実在の人物の噂話、ネガティブで不快な内容は扱わない。
- 毎回、冒頭のつかみ・言い回し・タイトルの型を変える。前日までと同じ構成文を使い回さない（YouTubeの「量産型コンテンツ」判定を避けるため）。
- `scripts/YYYYMMDD.json` を作る。形式は `scripts/food5.json` と同じ:
  - `slug`: `YYYYMMDD`、`channel`: `雑学太郎`、`style`、`voice_preset`、`format`（上で決めたもの）
  - `scenes`: 導入1〜2＋各ネタ3〜4シーン×10＋まとめ1。各ネタは「つかみ（問いかけ）→答え→理由・しくみ→意外な補足や身近な例」の流れで、ただの言い換えで水増ししない。各シーンに `tag`（構成に合わせた文言／"まとめ"）、`theme`（同じtagは同じ番号。0〜5を順に繰り返す）、`heading`（15字前後）、`emoji`（1文字。シーンごとに変えてよい）、`say`（ナレーション。1シーン80〜130字）。
  - `tiktok_tags`: TikTok版に入れるパートを、いちばん意外な**3つ**のtagで指定（例：`["その3","その7","その9"]`）。冒頭とまとめは自動で入る。2〜3分になる。
  - `chapter_names`（任意）: チャプター名を変えたいときだけ `{"その1": "バナナはベリー"}` のように書く。
  - `thumbnail`: text（20字以内）, sub, emoji, tag
  - `short`: 10個のうち**いちばん意外な雑学**を `segment` に指定。`hook`（「〜って知ってましたか？」型のつかみ）と `outro`（続きは本編へ誘導）を書く。切り出すパートの1シーン目が「ふたつめは〜」等で始まる場合は `say_short` を付ける。
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
- 本編は**8分以上**、TikTok版は**61秒以上**にする（どちらも短いとWARNINGが出る）。出たら台本を足して作り直す。
- 本編の作成には20分ほどかかる。

## 4. 公開用URLの用意
動画ファイルは main に入れない。別ディレクトリで孤立ブランチ `upload-YYYYMMDD` を作り、4ファイル（long / short / tiktok / thumb）だけをコミットして push する。
URL: `https://raw.githubusercontent.com/zatsugakumainichitoukou-byte/zatsugaku-videos/upload-YYYYMMDD/<ファイル名>`

## 5. YouTubeへ投稿予約（Metricool。blogId `8198074`、`createScheduledPost`）
Metricoolは予約時に動画を自社サーバーへコピーするので、GitHubのURLは予約の時点で読めればよい。Zapierはもう使わない。
1. **横動画**：公開日時は今日の **19:00**（timezone `Asia/Tokyo`。すでに過ぎていたら今から5分後）。
   - `providers`: `[{"network":"youtube"}]`、`media`: 横動画のraw URL、`videoThumbnailUrl`: サムネのraw URL
   - `text`: 説明文。`out/YYYYMMDD_meta.json` の `long.chapters` を「■目次」の見出しの下にそのまま貼る（YouTubeが自動で目次にする）。最後に「※この動画はAIツールを使って制作しています。」
   - `youtubeData`: `{"title": "<タイトル>", "type": "video", "privacy": "public", "tags": [...], "category": "EDUCATION", "madeForKids": false, "isAiGeneratedContent": false}`
2. **ショート**：公開日時は今日の **19:05**。`media`: ショートのraw URL。`youtubeData` の `type` は `"short"`、ほかは同じ（サムネは付けない）。説明文の1行目付近に「▶本編（フル版）はこちら https://www.youtube.com/channel/UC5btyvlkpQWNlyMhDj2I6Rg/videos」を入れる。
3. 横動画・ショートとも `firstCommentText` に、チャンネルからの最初のコメントを入れる（あとで毛糸さんが手で「固定」する）。横動画は「どの雑学がいちばん意外でしたか？番号でコメントしてね！」のような、答えやすい問いかけ。ショートは「この続きと残り9個の雑学は本編で▶ https://www.youtube.com/channel/UC5btyvlkpQWNlyMhDj2I6Rg/videos」。もし `firstCommentText` 付きでエラーになったら、外して予約し直し、報告に書く。
4. 返ってきた `uuid` と `plannerUrl` を控える。エラーが出たら1回だけ再試行し、それでも失敗したらそこで止めて報告する。
5. 予約したら作業を終えてよい（公開はMetricoolが行う）。翌日のレポートで公開を確認する。

## 6. 記録
- `topics.json` に `{"date", "theme", "format", "style", "voice_preset", "facts":[...], "long_title", "short_title", "metricool_uuids":[...]}（YouTubeの動画IDは予約時点では分からないので、タイトルで記録する）` を追記。
- `scripts/YYYYMMDD.json` と `topics.json` を main にコミットして push（`git -c push.negotiate=true push origin main`）。
- 最後に、タイトル2本・動画URL2本・扱った雑学の一覧を短く報告する。

## 7. Instagramリール・TikTokへの投稿予約（Metricool、毎日）
有料プラン（Starter）なので投稿数の上限はない。**毎日**両方に出す。
1. `getBrandSettings` で instagram と tiktok が接続済みか確認。未接続のネットワークは飛ばす。
2. 使う動画は、**Instagramは今日のショート**（`YYYYMMDD_short.mp4`）、**TikTokは今日のTikTok版**（`YYYYMMDD_tiktok.mp4`、厳選3パートの縦型・1分以上）。どちらも `upload-YYYYMMDD` ブランチの raw URL。
3. `createScheduledPost` を**ネットワークごとに1件ずつ**作る。公開日時は今日の **19:10**（YouTubeのショートの直後。timezone `Asia/Tokyo`。すでに過ぎていたら今から5分後）。
   - Instagram: providers `[{"network":"instagram"}]`、`instagramData`: `{"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`。キャプションは2〜3行＋改行＋ハッシュタグ5〜8個（#雑学 #豆知識 ほか内容に合うもの）＋「YouTubeで本編公開中」。
   - TikTok: providers `[{"network":"tiktok"}]`、`tiktokData`: `{"privacyOption":"PUBLIC_TO_EVERYONE","isAigc":true,"title":"<短いタイトル>"}`。キャプションは1〜2行（本編から選りすぐった3つの雑学だと分かるように）＋ハッシュタグ3〜5個。
   - Instagramは `firstCommentText` に「答えがわかった人はコメントで教えてね！」のような答えやすい問いかけを入れる（あとで毛糸さんが手で固定する）。エラーになったら外して予約し直し、**報告の最後に「Instagramに投稿するコメント」としてその文面を書く**（毛糸さんが手で投稿・固定する）。
   - TikTokは外部からコメントを付けられないので、**毛糸さんが手で投稿・固定する**。その日のTikTok版に合ったコメント文（答えやすい問いかけ。1〜2行、絵文字1つ程度、URLは入れない）を作り、**報告の最後に「TikTokに投稿するコメント」としてそのまま貼れる形で書く**。
   - 文面はYouTubeのコピペにせず、各SNS向けに書き分ける。
4. エラーが出たら1回だけ再試行し、それでも失敗したら記録して報告する。
5. `sns_log.json` に `{"date","instagram":true/false,"tiktok":true/false}` を追記して main に push。
