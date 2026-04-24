# K3 Vocabulary Practice

英文單字字卡練習網頁，共 177 張字卡。

## 線上版本

| 版本 | 連結 | 說明 |
|------|------|------|
| 基本版 | https://e063047.github.io/k3-vocabulary/K3.html | 練習 / 測驗模式 |
| 含發音版 | https://e063047.github.io/k3-vocabulary/K3-Sound.html | 發音 + 記錄錯誤 |
| SM-2 智慧複習版 | https://e063047.github.io/k3-vocabulary/K3-Sound-SM2.html | 間隔重複演算法 + 發音 |

---

## 版本功能比較

| 功能 | K3 | K3-Sound | K3-Sound-SM2 |
|------|----|----------|--------------|
| Test / Practise Mode | ✅ | ✅ | ✅ |
| 指定起始位置 | ✅ | ✅ | — |
| 隨機順序 | ✅ | ✅ | — |
| Play Sound 發音 | — | ✅ | ✅ |
| 上一題 / 下一題 | — | ✅ | ✅ |
| 錯題記錄 & 回顧 | — | ✅ | — |
| SM-2 間隔重複排程 | — | — | ✅ |
| 學習進度追蹤 | — | — | ✅ |

---

## 鍵盤快捷鍵

### K3-Sound 版

| 按鍵 | 功能 |
|------|------|
| 空白鍵 / `→` | 顯示答案 / 下一張 |
| `←` | 上一張 |
| `P` | 播放發音 |
| `R` | 記錄錯誤 |
| `V` | 開啟記錄回顧 |

### K3-Sound-SM2 版

| 按鍵 | 功能 |
|------|------|
| 空白鍵 / `→` | 顯示答案 / 評分 Good（預設）|
| `←` | 上一張 |
| `P` | 播放發音 |
| `1` / `2` / `3` / `4` | SM-2 評分（Again / Hard / Good / Easy）|
| `G` | 開啟 Progress 畫面 |

---

## K3-Sound-SM2 功能說明

### 首頁統計
- **Due Today** — 今天需要複習的字
- **New Cards** — 還沒學過的新字
- **Learned** — 已熟練（複習間隔 ≥ 21 天）

### 練習流程
- **Test Mode**：看圖 → Show Answer → 出現評分按鈕
- **Practise Mode**：圖＋單字同時顯示 → 直接評分

### SM-2 評分按鈕
| 按鈕 | 鍵盤 | 意思 | 效果 |
|------|------|------|------|
| 🔴 Again | `1` | 完全不記得 | 5 題後重考，明天再來 |
| 🟠 Hard  | `2` | 很吃力     | 間隔縮短 |
| 🔵 Good  | `3` | 正常記得   | 正常間隔 |
| 🟢 Easy  | `4` | 非常簡單   | 間隔拉長 |

> 每個按鈕上會顯示下次複習預計天數（如 `6d`、`2mo`）

---

## 離線使用（不需網路）

```bash
python server.py
```

自動開啟瀏覽器 `http://localhost:8080/K3-Sound-SM2.html`

> 發音功能使用瀏覽器內建 Web Speech API，離線也能正常運作。

---

## PDF 轉字卡圖片

若需要重新從 PDF 生成圖片：

```bash
python convert_flashcards.py K3.pdf
```

每兩頁合併為一張橫向圖片，輸出到 `output_cards/`，檔名格式為 `NNN-word.jpg`。

---

## 檔案結構

```
k3-vocabulary/
├── K3.html                  # 基本練習版
├── K3-Sound.html            # 含發音版
├── K3-Sound-SM2.html        # SM-2 智慧複習版（推薦）
├── K3.pdf                   # 原始 PDF 字卡
├── server.py                # 本機伺服器
├── convert_flashcards.py    # PDF → 圖片轉換工具
└── output_cards/
    ├── 001-tape.jpg
    ├── 002-game.jpg
    └── ...                  # 共 177 張字卡圖片
```
