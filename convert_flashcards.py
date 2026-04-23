#!/usr/bin/env python3
"""
convert_flashcards.py — PDF 字卡轉 JPEG 圖片工具

每兩頁 PDF 合併成一張 JPEG，命名為 001-tape.jpg, 002-game.jpg ...
假設奇數頁為文字頁（可提取單字），偶數頁為圖片頁。

用法：
  python convert_flashcards.py K3.pdf
  python convert_flashcards.py K3.pdf -o 我的輸出資料夾
  python convert_flashcards.py K3.pdf --dpi 200
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

# ── pdftotext 偵測位置 ─────────────────────────────────────────────────────────

PDFTOTEXT_CANDIDATES = [
    r"C:\Users\{}\AppData\Local\Programs\Git\mingw64\bin\pdftotext.exe".format(os.environ.get("USERNAME", "")),
    r"C:\Program Files\Git\mingw64\bin\pdftotext.exe",
    r"C:\poppler\bin\pdftotext.exe",
    r"C:\Program Files\poppler\bin\pdftotext.exe",
    r"C:\Program Files (x86)\poppler\bin\pdftotext.exe",
]

# ── 內嵌 PowerShell 腳本（負責 WinRT 渲染與圖片合併）─────────────────────────

_PS1_TEMPLATE = r"""
param(
    [string]$PdfPath,
    [string]$OutputDir,
    [int]$DPI,
    [string]$WordsFile
)

Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Drawing

$null = [Windows.Data.Pdf.PdfDocument,       Windows.Data.Pdf,    ContentType=WindowsRuntime]
$null = [Windows.Data.Pdf.PdfPageRenderOptions, Windows.Data.Pdf, ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile,        Windows.Storage,     ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType=WindowsRuntime]

function Await {
    param($AsyncOp, $ResultType)
    $m = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 } |
        Where-Object { $_.GetParameters()[0].ParameterType.Name -like 'IAsyncOperation*' } |
        Select-Object -First 1
    $task = $m.MakeGenericMethod($ResultType).Invoke($null, @($AsyncOp))
    $task.Wait() | Out-Null
    return $task.Result
}

function AwaitAction {
    param($AsyncAction)
    $m = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 } |
        Where-Object { $_.GetParameters()[0].ParameterType.Name -like 'IAsyncAction*' } |
        Select-Object -First 1
    $m.Invoke($null, @($AsyncAction)).Wait() | Out-Null
}

function Read-WinRTStream {
    param($stream)
    $size   = [uint32]$stream.Size
    $reader = [Windows.Storage.Streams.DataReader]::new($stream.GetInputStreamAt(0))
    $m = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 } |
        Where-Object { $_.GetParameters()[0].ParameterType.Name -like 'IAsyncOperation*' } |
        Select-Object -First 1
    $m.MakeGenericMethod([uint32]).Invoke($null, @($reader.LoadAsync($size))).Wait() | Out-Null
    $bytes = New-Object byte[] $size
    $reader.ReadBytes($bytes)
    return [System.IO.MemoryStream]::new($bytes)
}

# 讀取 Python 傳來的單字清單
$words = Get-Content -Path $WordsFile -Encoding UTF8

# 建立輸出資料夾
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# 載入 PDF
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($PdfPath)) ([Windows.Storage.StorageFile])
$pdf  = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file))      ([Windows.Data.Pdf.PdfDocument])
$totalPages = $pdf.PageCount

$scale     = $DPI / 96.0
$cardIndex = 0
$errors    = 0

for ($i = 0; $i -lt $totalPages; $i += 2) {
    if ($cardIndex -ge $words.Count) { break }

    $word    = $words[$cardIndex]
    $cardNum = "{0:D3}" -f ($cardIndex + 1)
    $outPath = Join-Path $OutputDir "$cardNum-$word.jpg"

    Write-Host ("PROGRESS:{0}:{1}" -f $cardNum, $word)

    try {
        $p1 = $pdf.GetPage([uint32]$i)
        $s1 = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
        $o1 = [Windows.Data.Pdf.PdfPageRenderOptions]::new()
        $o1.DestinationWidth  = [uint32]($p1.Size.Width  * $scale)
        $o1.DestinationHeight = [uint32]($p1.Size.Height * $scale)
        AwaitAction ($p1.RenderToStreamAsync($s1, $o1))
        $bmp1 = [System.Drawing.Bitmap]::new((Read-WinRTStream $s1))

        $bmp2 = $null
        if (($i + 1) -lt $totalPages) {
            $p2 = $pdf.GetPage([uint32]($i + 1))
            $s2 = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
            $o2 = [Windows.Data.Pdf.PdfPageRenderOptions]::new()
            $o2.DestinationWidth  = [uint32]($p2.Size.Width  * $scale)
            $o2.DestinationHeight = [uint32]($p2.Size.Height * $scale)
            AwaitAction ($p2.RenderToStreamAsync($s2, $o2))
            $bmp2 = [System.Drawing.Bitmap]::new((Read-WinRTStream $s2))
        }

        if ($bmp2) {
            $w      = $bmp1.Width + $bmp2.Width
            $h      = [Math]::Max($bmp1.Height, $bmp2.Height)
            $canvas = [System.Drawing.Bitmap]::new($w, $h)
            $g      = [System.Drawing.Graphics]::FromImage($canvas)
            $g.Clear([System.Drawing.Color]::White)
            $g.DrawImage($bmp1, 0, 0)
            $g.DrawImage($bmp2, $bmp1.Width, 0)
            $g.Dispose()
            $canvas.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
            $canvas.Dispose()
        } else {
            $bmp1.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
        }

        $bmp1.Dispose()
        if ($bmp2) { $bmp2.Dispose() }

    } catch {
        Write-Host ("ERROR:{0}:{1}" -f $cardNum, $_.Exception.Message)
        $errors++
    }

    $cardIndex++
}

Write-Host ("DONE:{0}:{1}" -f ($cardIndex - $errors), $errors)
"""


# ── 工具函式 ───────────────────────────────────────────────────────────────────

def find_pdftotext():
    found = shutil.which("pdftotext") or shutil.which("pdftotext.exe")
    if found:
        return found
    for path in PDFTOTEXT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def extract_words(pdftotext, pdf_path):
    result = subprocess.run(
        [pdftotext, "-layout", pdf_path, "-"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    words = []
    for section in result.stdout.split("\x0c"):
        word = section.replace("\r", "").replace("\n", "").strip()
        if word:
            words.append(word)
    return words


def needs_ascii_copy(path: str) -> bool:
    try:
        path.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


# ── 主程式 ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDF 字卡轉 JPEG 圖片 — 每兩頁合併成一張圖",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            範例：
              python convert_flashcards.py K3.pdf
              python convert_flashcards.py "C:\\字卡\\K3.pdf" -o "C:\\輸出"
              python convert_flashcards.py K3.pdf --dpi 200
        """),
    )
    parser.add_argument("pdf", help="PDF 檔案路徑")
    parser.add_argument("-o", "--output", default="", help="輸出資料夾（預設：PDF 旁的 output_cards）")
    parser.add_argument("--dpi", type=int, default=150, help="圖片解析度，預設 150")
    args = parser.parse_args()

    # ── 驗證輸入 ─────────────────────────────────────────────────────────────
    pdf_path = os.path.abspath(args.pdf)
    if not os.path.isfile(pdf_path):
        print(f"錯誤：找不到檔案 {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output or os.path.join(os.path.dirname(pdf_path), "output_cards")
    output_dir = os.path.abspath(output_dir)

    pdftotext = find_pdftotext()
    if not pdftotext:
        print("錯誤：找不到 pdftotext.exe。", file=sys.stderr)
        print("請確認已安裝 Git for Windows（內含 poppler），或另行安裝 poppler。", file=sys.stderr)
        sys.exit(1)

    print(f"PDF：{pdf_path}")
    print(f"輸出：{output_dir}")
    print(f"DPI：{args.dpi}")
    print(f"pdftotext：{pdftotext}")
    print()

    # ── 提取單字 ─────────────────────────────────────────────────────────────
    print("正在提取單字...")
    words = extract_words(pdftotext, pdf_path)
    if not words:
        print("錯誤：無法從 PDF 提取任何文字。", file=sys.stderr)
        print("可能原因：PDF 為純圖片、字型未嵌入，或需要 OCR。", file=sys.stderr)
        sys.exit(1)
    print(f"找到 {len(words)} 個單字（對應 {len(words)} 張字卡）")

    # ── 處理 Unicode 路徑 ────────────────────────────────────────────────────
    work_pdf = pdf_path
    tmp_pdf = None
    if needs_ascii_copy(pdf_path):
        tmp_fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf", prefix="flashcard_")
        os.close(tmp_fd)
        shutil.copy2(pdf_path, tmp_pdf)
        work_pdf = tmp_pdf
        print(f"路徑含非 ASCII 字元，已複製到暫存位置：{tmp_pdf}")

    # ── 寫入 PowerShell 腳本與單字清單到暫存檔 ──────────────────────────────
    tmp_dir = tempfile.mkdtemp(prefix="flashcard_")
    ps1_path    = os.path.join(tmp_dir, "render.ps1")
    words_path  = os.path.join(tmp_dir, "words.txt")

    with open(ps1_path, "w", encoding="utf-8") as f:
        f.write(_PS1_TEMPLATE)

    with open(words_path, "w", encoding="utf-8") as f:
        f.write("\n".join(words))

    # ── 執行 PowerShell 渲染 ─────────────────────────────────────────────────
    print("\n開始渲染（每張約 0.5–1 秒）...")
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "powershell", "-ExecutionPolicy", "Bypass", "-File", ps1_path,
        "-PdfPath",   work_pdf,
        "-OutputDir", output_dir,
        "-DPI",       str(args.dpi),
        "-WordsFile", words_path,
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
    )

    done_count = error_count = 0
    for line in proc.stdout:
        line = line.rstrip()
        if line.startswith("PROGRESS:"):
            _, num, word = line.split(":", 2)
            print(f"  [{num}] {word}")
        elif line.startswith("ERROR:"):
            _, num, msg = line.split(":", 2)
            print(f"  [錯誤 {num}] {msg}", file=sys.stderr)
        elif line.startswith("DONE:"):
            _, done_count, error_count = line.split(":")
            done_count, error_count = int(done_count), int(error_count)
        elif line:
            print(f"  {line}")

    proc.wait()

    # ── 清理暫存檔 ────────────────────────────────────────────────────────────
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        if tmp_pdf:
            os.remove(tmp_pdf)
    except Exception:
        pass

    # ── 結果報告 ──────────────────────────────────────────────────────────────
    print()
    if proc.returncode != 0 and done_count == 0:
        print("錯誤：PowerShell 渲染失敗，請確認 Windows 10/11 且 PowerShell 5+ 可用。", file=sys.stderr)
        sys.exit(1)

    print(f"完成！共產生 {done_count} 張圖片")
    if error_count:
        print(f"警告：{error_count} 張轉換失敗")
    print(f"輸出位置：{output_dir}")


if __name__ == "__main__":
    main()
