# K3 Vocabulary Practice

英文單字字卡練習網頁，支援手機／平板自適應，共 177 張字卡。

## 線上版本

| 版本 | 連結 | 適合對象 |
|------|------|---------|
| 基本版 | https://e063047.github.io/k3-vocabulary/K3.html | 快速練習 |
| 含發音版 | https://e063047.github.io/k3-vocabulary/K3-Sound.html | 需要聽發音、記錄錯題 |
| SM-2 智慧複習版 | https://e063047.github.io/k3-vocabulary/K3-Sound-SM2.html | 長期記憶，每天複習（推薦）|

---

## 版本功能比較

| 功能 | K3 | K3-Sound | K3-Sound-SM2 |
|------|----|----------|--------------|
| Test / Practise Mode | ✅ | ✅ | ✅ |
| 指定起始位置 | ✅ | ✅ | — |
| 隨機順序 | ✅ | ✅ | — |
| 上一題 / 下一題 | ✅ | ✅ | ✅ |
| Play Sound 發音 | — | ✅ | ✅ |
| 錯題記錄 & 回顧 | — | ✅ | — |
| SM-2 間隔重複排程 | — | — | ✅ |
| 學習進度追蹤 | — | — | ✅ |
| 手機 / 平板自適應 | ✅ | ✅ | ✅ |

---

## 鍵盤快捷鍵

### K3 / K3-Sound 版

| 按鍵 | 功能 |
|------|------|
| `空白鍵` / `→` | 顯示答案 / 下一張 |
| `←` | 上一張 |
| `P` | 播放發音（K3-Sound）|
| `R` | 記錄錯誤（K3-Sound）|
| `V` | 開啟錯題回顧（K3-Sound）|

### K3-Sound-SM2 版

| 按鍵 | 功能 |
|------|------|
| `空白鍵` / `→` | 顯示答案 / 評分 Good（預設）|
| `←` | 上一張 |
| `P` | 播放發音 |
| `1` `2` `3` `4` | SM-2 評分（Again / Hard / Good / Easy）|
| `G` | 開啟 Progress 畫面 |

---

## SM-2 智慧複習說明

### 首頁統計

| 數字 | 意思 |
|------|------|
| Due Today | 今天需要複習的字 |
| New Cards | 還沒看過的新字 |
| Learned | 已熟練（複習間隔 ≥ 21 天）|

### 練習流程

- **Test Mode**：看圖 → `Show Answer` → 出現評分按鈕
- **Practise Mode**：圖＋單字同時顯示 → 直接評分

### 評分按鈕

| 按鈕 | 鍵盤 | 意思 | 效果 |
|------|------|------|------|
| 🔴 Again | `1` | 完全不記得 | 5 題後重考，明天再來 |
| 🟠 Hard  | `2` | 很吃力 | 間隔縮短 |
| 🔵 Good  | `3` | 正常記得 | 正常間隔 |
| 🟢 Easy  | `4` | 非常簡單 | 間隔拉長 |

每個按鈕上方會顯示下次複習的預計天數，例如 `6d`、`2mo`。

---

## 本機使用

```bash
python server.py
```

自動開啟瀏覽器 `http://localhost:8080/K3-Sound-SM2.html`

> 發音使用瀏覽器內建 Web Speech API，離線也能正常運作。

---

## 擴充題庫

### 步驟 1 — 準備 PDF

將新字卡加入 PDF（格式：奇數頁＝單字文字、偶數頁＝圖片）。

### 步驟 2 — 轉換圖片

```bash
python convert_flashcards.py 你的字卡.pdf
```

腳本會自動：
1. 將每兩頁合併成一張 JPEG，輸出到 `output_cards/`
2. 更新 `cards.json`（掃描 output_cards/ 重新產生清單）

### 步驟 3 — 確認 cards.json

打開 `cards.json`，確認新字卡名稱出現在清單末尾：

```json
  "177-parrot",
  "178-dog",
  "179-cat"
]
```

### 步驟 4 — 啟動伺服器確認

```bash
python server.py
```

設定畫面的範圍會自動更新為 `001 – 179`，SM-2 的 All 數字也會跟著更新。
**不需要修改任何 HTML 檔案。**

### 步驟 5 — 部署到 GitHub Pages

```bash
git add output_cards/ cards.json
git commit -m "新增 178-dog、179-cat"
git push
```

---

## cards.json 機制說明

三個 HTML 網頁啟動時會先用內建的硬寫清單顯示，同時非同步讀取 `cards.json`：

```
HTML 硬寫清單（後備，確保離線也能用）
       ↓
fetch("cards.json")  ←  每次跑 convert_flashcards.py 就會更新
       ↓ 成功
覆蓋 CARDS 清單 → 顯示最新題庫
       ↓ 失敗（直接開 .html 而非透過伺服器）
維持硬寫後備，不出錯
```

---

## 檔案結構

```
k3-vocabulary/
├── K3.html                  # 基本練習版
├── K3-Sound.html            # 含發音版
├── K3-Sound-SM2.html        # SM-2 智慧複習版（推薦）
├── cards.json               # 題庫清單（由 convert_flashcards.py 自動產生）
├── K3.pdf                   # 原始 PDF 字卡
├── server.py                # 本機伺服器
├── convert_flashcards.py    # PDF → 圖片 + 更新 cards.json
└── output_cards/
    ├── 001-tape.jpg
    ├── 002-game.jpg
    └── ...                  # 字卡圖片（NNN-word.jpg）
```
