# 雑学太郎 デイリーレポート 手順書（毎朝実行）

対象: **昨日（日本時間0:00〜23:59）の動き**と、**直近7日間の合計**。月曜の朝だけは、先週（月〜日）の振り返りも加える。Metricool（brandId `8198074`、timezone `Asia/Tokyo`）の `getAnalyticsDataByMetrics` で集計する。
Metricool無料プランは過去30日分しか取れないため、毎日の結果を `stats/YYYYMMDD.json`（昨日の日付）に保存して長期の記録にする。

## 1. 準備
GitHubリポジトリ zatsugakumainichitoukou-byte/zatsugaku-videos を追加して clone。`topics.json`（各日の見た目・声・構成・動画ID）と `sns_log.json`、過去の `stats/` を読む。

## 2. 数字を取る（動画ごと）
- YouTube（connector: all videos）: `YTVV02` 公開日時, `YTVV04` 動画ID, `YTVV17` タイトル, `YTVV06` 再生数, `YTVV09` 高評価, `YTVV11` コメント, `YTVV12` 共有, `YTVV08` 平均視聴時間
- TikTok（connector: posts）: `TKPO02` 公開日時, `TKPO03` URL, `TKPO07` 再生数, `TKPO08` いいね, `TKPO09` コメント, `TKPO10` シェア, `TKPO13` 完全視聴率
- Instagramリール（connector: reels）: `IGRE02` 公開日時, `IGRE06` URL, `IGRE23` 再生数, `IGRE10` いいね, `IGRE07` コメント, `IGRE21` シェア, `IGRE12` 保存
- YouTubeチャンネル全体（connector: evolution）: `YTEV01` 登録者数, `YTEV02` 総再生数, `YTEV05` 登録者増, `YTEV06` 登録者減
- InstagramとTikTokのフォロワー数・増減も取る。使えるIDが分からなければ `getAnalyticsAvailableMetrics` で各ネットワークの connector `evolution` などを調べる（"Deprecated" と書かれた項目は使わない）。
- TikTok・Instagramのアカウント全体の日別再生数（evolution）は空になることがあるため、再生・いいね・コメントは**動画ごとのデータ（posts / reels）の合計**を使う。公開日時はUTCの14桁（YYYYMMDDhhmmss）なので日本時間に直す。
- YouTubeの数字はMetricool側への反映が2〜3日遅れることがある。直近の動画の数字が0や空のときは「反映待ちの可能性」と書く。
- 取得に失敗した項目は推測で埋めず「取得できず」と書く。

- 前日にMetricoolで予約した投稿（YouTube・Instagram・TikTok）が公開されたかも確認し、されていなければ報告の冒頭に書く（`getScheduledPosts` に残っている／エラーになっているものがないか）。

## 3. 保存
`stats/YYYYMMDD.json` に、期間・SNS別合計・動画ごとの数字（YouTubeは topics.json と動画ID、または公開日とタイトルで突き合わせ、その日の theme / format / style / voice_preset と、横動画かショートかを付ける）を保存し、main に push。

## 4. 分析
- SNS別の、昨日1日分と直近7日の合計（再生・いいね・コメント・シェア・フォロワー増減）。前日比・前週比（過去の stats があれば）。
- 昨日公開した動画の初速（公開から半日〜1日の数字）を、過去の動画の同じタイミングと比べる。
- 直近7日で伸びた動画トップ3・伸びなかった動画ワースト2（ショートと横動画は分けて比べる）。
- 構成（format）・見た目（style）・声（voice_preset）・テーマのジャンル別に、ショートの平均再生数を比べる。**サンプルが少ないうちは「傾向の芽」として控えめに書く**（各条件3本未満なら断定しない）。
- 提案は毎日出さなくてよい。はっきりした変化があった日だけ1つ。月曜は先週の振り返りとして1〜3個（例：伸びたジャンルを増やす）。手順書（RUNBOOK.md）は勝手に書き換えず、提案にとどめる。

## 5. 報告
日本語で、スマホの1画面に収まる短さで報告する（昨日の数字 → 7日間の合計 → 目立った動画 → 気づき・提案）。投稿がまだ少ない時期は、数字が0でもそのまま正直に書く。

## 6. 月曜だけ：自動チューニング（毛糸さんの了承済み）
先週分までの stats/ と topics.json をもとに、伸びる傾向がはっきりしたものを `tuning.json` に反映し、翌日からの動画に効かせる。

**変えてよいもの**：`tuning.json` の重み（style / voice_preset / format / genre）と `title_tips`（タイトルやつかみの書き方のコツ）。
- 判断の基準：比べる条件ごとに**ショートが3本以上**あり、ショートの再生数の中央値が全体より**30%以上**高い（または低い）ときだけ動かす。1回で動かす幅は±0.3まで、範囲は0.3〜2.0。データが足りなければ何も変えない。
- 変えたら `tuning.json` の `updated` と `history` に「日付・何を・なぜ（数字つき）」を追記し、main に push。報告の「気づき」に変更内容を書く。

**変えないもの**（変えたくなったら提案にとどめる）：事実確認のルール、AI制作の明記、扱わない話題の決まり、動画の長さ（本編8分以上・TikTok版61秒以上）、投稿時刻と投稿先、費用がかかること、`pipeline/` のプログラム。

### 月曜だけ：競合チェック
Metricoolに登録した競合（9割が知らない雑学／雑学ミステリー通信／ヤマヤデの生き様ッ!／光と闇の雑学）の直近7日を取る：
`getAnalyticsDataByMetrics`（brandId 8198074）で YTCO04 名前, YTCO05 登録者, YTCO06 本数, YTCO11 再生, YTCO07 高評価, YTCO09 コメント。
- 前週の値を `stats/competitors_YYYYMMDD.json` に保存し、登録者の増減を前週と比べる。
- 報告に「競合」欄を3行程度で入れる：一番伸びたチャンネルと、そこから雑学太郎に取り入れられそうなこと（テーマ・タイトルの付け方・本数）。
- 取り入れる場合も、上の「変えてよいもの」の範囲（tuning.json の重みや title_tips）に限る。

## 7. 目標の段階
目標は「収益化達成 → 経費の回収（Claude代＋Metricool 25ドル）→ 月1万円 → 3万円 → 5万円 → 10万円」の順（ダッシュボードの「目標」欄と同じ）。直近30日のYouTube推定収益（YTEV03、1ドル＝157円）で判定する。報告の最後に「今の目標：◯◯（直近30日 ◯円 / ◯円）」を1行入れ、新しい段階に上がった日はそれを冒頭で知らせる。
