# K3 Vocabulary Practice

英文單字字卡練習網頁，共 177 張字卡。

## 線上版本

| 版本 | 連結 |
|------|------|
| 基本版 | https://e063047.github.io/k3-vocabulary/K3.html |
| 含發音版 | https://e063047.github.io/k3-vocabulary/K3-Sound.html |

## 功能

### 設定畫面
- **Test Mode** — 看圖猜單字，按 Show Answer 才顯示答案
- **Practise Mode** — 圖片與單字同時顯示
- **Specify start position** — 從指定題號開始（001–177）
- **Randomly allocated** — 全部 177 張隨機出現，每題只出現一次

### 練習畫面
- 圖片佔畫面 90%
- 下方顯示目前模式與進度（例如 Status: 3 / 177）
- **Show Answer** — 顯示被遮住的單字（Test Mode）
- **🔊 Play Sound** — 朗讀當前單字（含發音版專屬）
- **Next** — 下一張
- **Record** — 記錄答錯的單字
- **View Records** — 查看所有錯誤單字與錯誤次數

### 鍵盤快捷鍵
| 按鍵 | 功能 |
|------|------|
| 空白鍵 / → | 顯示答案 / 下一張 |
| P | 播放發音（含發音版） |
| R | Record |
| V | View Records |

## 本機執行

```bash
python server.py
```

自動開啟瀏覽器 `http://localhost:8000/K3.html`

## 檔案結構

```
k3-vocabulary/
├── K3.html            # 練習網頁（基本版）
├── K3-Sound.html      # 練習網頁（含發音版）
├── server.py          # 本機伺服器
├── 001-tape.jpg
├── 002-game.jpg
├── ...
└── 177-parrot.jpg     # 共 177 張字卡圖片
```
