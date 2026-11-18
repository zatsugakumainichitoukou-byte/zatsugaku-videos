# 雑学太郎 毎日投稿 手順書（スケジュール実行用）

YouTubeチャンネル「雑学太郎」（チャンネルID: UC5btyvlkpQWNlyMhDj2I6Rg）に、毎日19時ごろ
**横動画（本編）1本＋その一部を切り出したショート1本**を公開する。人の確認なしで最後まで実行する。

## 0. 準備
1. このリポジトリが無ければ `mcp__claude-code-remote__add_repo`（owner: zatsugakumainichitoukou-byte, repo: zatsugaku-videos, access: push）→ 指示どおり clone。
2. `pip install --break-system-packages -q edge-tts numpy pillow`
3. `topics.json` を読み、過去に扱ったテーマ・雑学を把握する。

## 1. 台本づくり（毎回いちばん手をかける工程）
- テーマを1つ決める（食べ物／動物／人体／宇宙／日本語／歴史／生活用品／地理 など。直近7日と同じジャンルは避け、過去と同じ雑学は使わない）。
- 雑学を5つ選ぶ。**1つずつWebSearchで裏付けを取る**。確認できないもの・俗説・諸説あるものは使わない（使うなら「〜という説があります」と明示）。
- 医療・お金・事件など繊細な話題、実在の人物の噂話、ネガティブで不快な内容は扱わない。
- 毎回、冒頭のつかみ・言い回し・タイトルの型を変える。前日までと同じ構成文を使い回さない（YouTubeの「量産型コンテンツ」判定を避けるため）。
- `scripts/YYYYMMDD.json` を作る。形式は `scripts/food5.json` と同じ:
  - `slug`: `YYYYMMDD`、`channel`: `雑学太郎`
  - `scenes`: 導入1＋各雑学2シーン×5＋まとめ1。各シーンに `tag`（"その1"…/"まとめ"）、`theme`（同じtagは同じ番号0〜5）、`heading`（15字前後）、`emoji`（1文字）、`say`（ナレーション。1シーン60〜110字）。
  - `thumbnail`: text（20字以内）, sub, emoji, tag
  - `short`: 5つのうち**いちばん意外な雑学**を `segment` に指定。`hook`（「〜って知ってましたか？」型のつかみ）と `outro`（続きは本編へ誘導）を書く。切り出すパートの1シーン目が「ふたつめは〜」等で始まる場合は `say_short` を付ける。
  - タイトル・説明文・タグ（long と short それぞれ）。説明文の最後に必ず「※この動画はAIツールを使って制作しています。」を入れる。ショートのタイトル末尾に `#雑学 #shorts`。

## 2. 動画の生成
```
python3 pipeline/make_video.py scripts/YYYYMMDD.json out --frames   # 静止画チェック
```
`out/work_long/` と `out/work_short/` のJPGを数枚 Read で目視し、文字のはみ出し・不自然な改行（行頭の「」」「ゃ」など）がないか確認。問題があれば台本の文言を直す。
```
python3 pipeline/make_video.py scripts/YYYYMMDD.json out
```
出力: `out/YYYYMMDD_long.mp4`, `out/YYYYMMDD_short.mp4`, `out/YYYYMMDD_thumb.png`

## 3. 公開用URLの用意
動画ファイルは main に入れない。別ディレクトリで孤立ブランチ `upload-YYYYMMDD` を作り、3ファイルだけをコミットして push する。
URL: `https://raw.githubusercontent.com/zatsugakumainichitoukou-byte/zatsugaku-videos/upload-YYYYMMDD/<ファイル名>`

## 4. YouTubeへ投稿（Zapier の YouTube: selected_api `YouTubeV4CLIAPI`）
1. 横動画: `upload_video`（privacy_status: public, category_id: "27", default_language/default_audio_language: "ja", made_for_kids: "false"）。返ってきた動画IDを控える。
2. サムネ: `upload_video_thumbnail`（video_id, thumbnail=サムネURL）。
3. ショート: `upload_video`（privacy_status: public, made_for_kids: "false"）。説明文の1行目付近に「▶本編はこちら https://www.youtube.com/watch?v=<横動画ID>」を入れる。
4. 失敗したら1回だけ再試行。それでも失敗したら、そこで止めて内容を報告する。

## 5. 記録
- `topics.json` に `{"date", "theme", "facts":[...], "long_id", "short_id"}` を追記。
- `scripts/YYYYMMDD.json` と `topics.json` を main にコミットして push（`git -c push.negotiate=true push origin main`）。
- 最後に、タイトル2本・動画URL2本・扱った雑学の一覧を短く報告する。
