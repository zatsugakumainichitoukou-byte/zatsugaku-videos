# 雑学太郎 週次レポート 手順書（毎週月曜の朝に実行）

対象期間: **先週の月曜0:00〜日曜23:59（日本時間）**。Metricool（brandId `8198074`、timezone `Asia/Tokyo`）の `getAnalyticsDataByMetrics` で集計する。
Metricool無料プランは過去30日分しか取れないため、毎週の結果を `stats/YYYY-Www.json` に保存して長期の記録にする。

## 1. 準備
GitHubリポジトリ zatsugakumainichitoukou-byte/zatsugaku-videos を追加して clone。`topics.json`（各日の見た目・声・構成・動画ID）と `sns_log.json`、過去の `stats/` を読む。

## 2. 数字を取る（動画ごと）
- YouTube（connector: all videos）: `YTVV02` 公開日時, `YTVV04` 動画ID, `YTVV17` タイトル, `YTVV06` 再生数, `YTVV09` 高評価, `YTVV11` コメント, `YTVV12` 共有, `YTVV08` 平均視聴時間
- TikTok（connector: posts）: `TKPO02` 公開日時, `TKPO03` URL, `TKPO07` 再生数, `TKPO08` いいね, `TKPO09` コメント, `TKPO10` シェア, `TKPO13` 完全視聴率
- Instagramリール（connector: reels）: `IGRE02` 公開日時, `IGRE06` URL, `IGRE23` 再生数, `IGRE10` いいね, `IGRE07` コメント, `IGRE21` シェア, `IGRE12` 保存
- フォロワー数（チャンネル登録者）の増減も各SNSで取る。使えるIDが分からなければ `getAnalyticsAvailableMetrics` で各ネットワークの connector `evolution` などを調べる（"Deprecated" と書かれた項目は使わない）。
- 取得に失敗した項目は推測で埋めず「取得できず」と書く。

## 3. 保存
`stats/YYYY-Www.json` に、期間・SNS別合計・動画ごとの数字（YouTubeは topics.json と動画IDで突き合わせ、その日の theme / format / style / voice_preset と、横動画かショートかを付ける）を保存し、main に push。

## 4. 分析
- SNS別の合計（再生・いいね・コメント・シェア・フォロワー増減）と、前週比（前週の stats があれば）。
- 伸びた動画トップ3・伸びなかった動画ワースト2（ショートと横動画は分けて比べる）。
- 構成（format）・見た目（style）・声（voice_preset）・テーマのジャンル別に、ショートの平均再生数を比べる。**サンプルが少ないうちは「傾向の芽」として控えめに書く**（各条件3本未満なら断定しない）。
- 来週に向けた提案を1〜3個（例：伸びたジャンルを増やす）。手順書（RUNBOOK.md）は勝手に書き換えず、提案にとどめる。

## 5. 報告
日本語で、スマホで読みやすい短さにまとめて報告する（合計 → トップ動画 → 傾向 → 提案の順）。
