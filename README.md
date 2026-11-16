# Long Range 3D（狙撃ゲーム）

ブラウザで遊ぶ3D狙撃ゲーム（iPhone / PC）。

- 遊ぶ: https://hiro11sbr.github.io/game_Git/ （`game_Git` は大文字のG。小文字だと404）
- 必要環境: Safari 16.4 以降 / 最近のChrome。外部の three.js(0.160) を読み込むので通信が必要

## ステージ
| ステージ | 内容 |
|---|---|
| 射撃場 | 鉄板の的（200〜3,540m） |
| 猟場 | ヒグマ3頭 |
| 都市 | 屋上の敵兵。設定で「カジュアル（敵10人・100〜1,200m）」「長距離（敵1人・3,540m）」を選べる |

## 武器
M110（半自動）／TAC-50／PX-20（架空レーザー）／モシン・ナガン／M82A1。⚙設定から切り替え。

## 得点
命中で +100（頭・急所 +150、手足 +50）。最高得点はステージ別にこの端末へ保存。

## 制限時間
⚙設定「制限時間：30秒チャレンジ」で、最初の1発から30秒で何点取れるか競う。0秒で結果（得点・最高・命中率）が出て、「もう一度」で再開。最高得点はチャレンジ用に別保存。

## ファイル
| ファイル | 役割 |
|---|---|
| `index.html` | ゲーム本体（銃の形データを含む1ファイル） |
| `docs/index.html` | 公開用（`python3 tools/build_pages.py` で作る。**index.html を直したら必ず実行**） |
| `tools/glb_to_data.py` | GLB(3Dモデル)→銃の形データ。`python3 -I tools/glb_to_data.py 入力.glb 名前 [--rot 度] [--axis x\|z]` |

## 更新して公開するまで
1. `index.html` を編集
2. `python3 tools/build_pages.py`
3. 公開元ブランチ `claude/sniper-range-3d` の `/docs` に反映（GitHub Pages）。1〜2分で更新

## 銃の差し替え（メモ）
形データ(`window.XXX_POS/IDX`)を貼り、`buildRealGun` の定義（長さ K・傾き tilt・スコープ軸 scopeY・銃身 boreY・横ずれ w0・位置 zoff・部位判定 classify）を合わせる。
色は `wornTex` が線形変換するため、見た目より明るい16進を渡す。アップロード名と中身が違うことがあるので、必ず見た目で確認する。
