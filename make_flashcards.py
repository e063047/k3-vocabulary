#!/usr/bin/env python3
"""
Flashcard PDF Generator
=======================
將字卡圖片排版到 A4 PDF，列印後剪開、對摺、護貝。

使用方式：
    python make_flashcards.py

修改下方 CONFIGURATION 區塊的參數即可調整輸出結果。
"""

import os
import glob
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image


# ===========================================================
#  CONFIGURATION  ← 在這裡調整參數
# ===========================================================

# ----- 路徑 -----
INPUT_FOLDER = r'C:\Users\23002697\Desktop\ClaudeCode\output_cards'
OUTPUT_PDF   = r'C:\Users\23002697\Desktop\ClaudeCode\flashcards_print.pdf'
IMAGE_EXTS   = ('*.jpg', '*.jpeg', '*.png')   # 要讀取的副檔名

# ----- 護貝膜尺寸 (mm) -----
POUCH_W = 95   # 護貝膜寬度
POUCH_H = 60   # 護貝膜高度

# ----- 對摺方向 -----
# 'horizontal' : 橫向卡片，左右對摺（圖片與單字左右並排，適合寬版圖）
# 'vertical'   : 直向卡片，上下對摺（圖片與單字上下排列，適合長版圖）
FOLD_DIRECTION = 'horizontal'

# ----- 列印卡片尺寸 (mm)，留 None 表示自動計算 -----
# horizontal 模式：card_w 預設 = 2 × POUCH_W，card_h 依圖片比例自動計算
# vertical   模式：card_h 預設 = 2 × POUCH_H，card_w 依圖片比例自動計算
# 若自動算出的尺寸不合適，可手動指定（可能輕微拉伸圖片）
CARD_W_MM = None
CARD_H_MM = None

# ----- 頁面設定 (mm) -----
PAGE_W = 210   # A4 寬
PAGE_H = 297   # A4 高
MARGIN_TOP    = 10
MARGIN_BOTTOM = 10
MARGIN_LEFT   = 10
MARGIN_RIGHT  = 10

# ----- 卡片間距 (mm) -----
CARD_GAP = 2   # 相鄰卡片之間的空白（用於剪裁時的容錯空間）

# ----- 輔助線顯示 -----
SHOW_FOLD_LINE = True   # 對摺線（卡片中央虛線）
SHOW_BORDER    = True   # 卡片外框（剪裁參考）
SHOW_CUT_LINE  = True   # 卡片之間的剪裁虛線

FOLD_LINE_COLOR = '#bbbbbb'   # 對摺線顏色
BORDER_COLOR    = '#888888'   # 外框顏色
CUT_LINE_COLOR  = '#cccccc'   # 剪裁線顏色

# ----- PDF 輸出品質 -----
PDF_DPI = 300   # 建議 300（列印標準），預覽用可改 150 加快速度

# ===========================================================
#  以下不需要修改
# ===========================================================

def collect_images():
    files = []
    for ext in IMAGE_EXTS:
        files += glob.glob(os.path.join(INPUT_FOLDER, ext))
    files = sorted(set(files))
    if not files:
        sys.exit(f'[ERROR] 找不到圖片：{INPUT_FOLDER}')
    return files


def detect_image_size(files):
    w, h = Image.open(files[0]).size
    return w, h


def calc_card_size(img_w, img_h):
    if FOLD_DIRECTION == 'horizontal':
        w = CARD_W_MM if CARD_W_MM else 2 * POUCH_W
        h = CARD_H_MM if CARD_H_MM else w * img_h / img_w
    else:  # vertical
        h = CARD_H_MM if CARD_H_MM else 2 * POUCH_H
        w = CARD_W_MM if CARD_W_MM else h * img_w / img_h
    return w, h


def calc_grid(card_w, card_h):
    usable_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    usable_h = PAGE_H - MARGIN_TOP  - MARGIN_BOTTOM
    cols = int((usable_w + CARD_GAP) / (card_w + CARD_GAP))
    rows = int((usable_h + CARD_GAP) / (card_h + CARD_GAP))
    if cols < 1 or rows < 1:
        sys.exit(
            f'[ERROR] 卡片尺寸 {card_w:.1f}×{card_h:.1f}mm 超過可用版面 '
            f'{usable_w:.1f}×{usable_h:.1f}mm。\n'
            '請調整 POUCH_W/H、CARD_W/H_MM 或邊距設定。'
        )
    return cols, rows


def _dashed(fig, x1, y1, x2, y2, color, lw, dash=(4, 4)):
    """在 figure 座標中畫虛線（輸入單位為 mm，以頁面左下角為原點）。"""
    fig.add_artist(plt.Line2D(
        [x1 / PAGE_W, x2 / PAGE_W],
        [y1 / PAGE_H, y2 / PAGE_H],
        transform=fig.transFigure,
        color=color, linewidth=lw,
        linestyle=(0, dash),
        solid_capstyle='butt',
        zorder=20
    ))


def build_pdf(files, card_w, card_h, cols, rows):
    cpp  = cols * rows
    pages = math.ceil(len(files) / cpp)

    usable_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    usable_h = PAGE_H - MARGIN_TOP  - MARGIN_BOTTOM
    grid_w   = cols * card_w + (cols - 1) * CARD_GAP
    grid_h   = rows * card_h + (rows - 1) * CARD_GAP

    # 將整個格線群組在可用區域中置中
    x0 = MARGIN_LEFT + (usable_w - grid_w) / 2   # 從頁面左緣起算 (mm)
    y0 = MARGIN_TOP  + (usable_h - grid_h) / 2   # 從頁面上緣起算 (mm)

    with PdfPages(OUTPUT_PDF) as pdf:
        for pg in range(pages):
            batch = files[pg * cpp : (pg + 1) * cpp]

            fig = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
            fig.patch.set_facecolor('white')

            for i, path in enumerate(batch):
                r, c = divmod(i, cols)

                # 卡片左上角座標（從頁面上/左緣起算，mm）
                cx = x0 + c * (card_w + CARD_GAP)
                cy = y0 + r * (card_h + CARD_GAP)

                # matplotlib 的 y 軸從頁面底部往上，需轉換
                cy_bot = PAGE_H - cy - card_h   # 卡片底部距頁面底部 (mm)
                cy_top = cy_bot + card_h         # 卡片頂部距頁面底部 (mm)

                # 插入圖片
                ax = fig.add_axes([
                    cx     / PAGE_W, cy_bot / PAGE_H,
                    card_w / PAGE_W, card_h / PAGE_H
                ])
                ax.imshow(mpimg.imread(path), aspect='auto', interpolation='lanczos')
                ax.set_axis_off()

                # 外框（剪裁參考線）
                if SHOW_BORDER:
                    fig.add_artist(patches.Rectangle(
                        (cx / PAGE_W, cy_bot / PAGE_H),
                        card_w / PAGE_W, card_h / PAGE_H,
                        linewidth=0.5, edgecolor=BORDER_COLOR,
                        facecolor='none', transform=fig.transFigure, zorder=15
                    ))

                # 對摺線
                if SHOW_FOLD_LINE:
                    if FOLD_DIRECTION == 'horizontal':
                        fx = cx + card_w / 2
                        _dashed(fig, fx, cy_bot, fx, cy_top, FOLD_LINE_COLOR, 0.5)
                    else:
                        fy = cy_bot + card_h / 2
                        _dashed(fig, cx, fy, cx + card_w, fy, FOLD_LINE_COLOR, 0.5)

                # 卡片間剪裁虛線
                if SHOW_CUT_LINE:
                    if c < cols - 1:   # 右側縱向虛線
                        vx = cx + card_w + CARD_GAP / 2
                        _dashed(fig, vx, cy_bot, vx, cy_top, CUT_LINE_COLOR, 0.4, (3, 3))
                    if r < rows - 1:   # 下方橫向虛線
                        hy = cy_bot - CARD_GAP / 2
                        _dashed(fig, cx, hy, cx + card_w, hy, CUT_LINE_COLOR, 0.4, (3, 3))

            pdf.savefig(fig, dpi=PDF_DPI, bbox_inches=None)
            plt.close(fig)
            print(f'  第 {pg + 1}/{pages} 頁', end='\r')

    print(f'\n完成！輸出：{OUTPUT_PDF}')


def main():
    files          = collect_images()
    img_w, img_h   = detect_image_size(files)
    card_w, card_h = calc_card_size(img_w, img_h)
    cols, rows     = calc_grid(card_w, card_h)
    cpp            = cols * rows
    pages          = math.ceil(len(files) / cpp)

    if FOLD_DIRECTION == 'horizontal':
        fold_result = f'對摺後 {card_w/2:.1f} × {card_h:.1f} mm'
    else:
        fold_result = f'對摺後 {card_w:.1f} × {card_h/2:.1f} mm'

    print(f'圖片數量    : {len(files)} 張')
    print(f'圖片像素    : {img_w} × {img_h} px')
    print(f'列印尺寸    : {card_w:.1f} × {card_h:.1f} mm  →  {fold_result}  (護貝膜 {POUCH_W}×{POUCH_H} mm)')
    print(f'每頁排版    : {cols} 欄 × {rows} 列 = {cpp} 張/頁')
    print(f'總頁數      : {pages} 頁')
    print(f'輸出路徑    : {OUTPUT_PDF}')
    print('產生 PDF 中...')

    build_pdf(files, card_w, card_h, cols, rows)


if __name__ == '__main__':
    main()
