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
