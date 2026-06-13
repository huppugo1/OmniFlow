"""文字识别 (OCR) Tools.

使用 Tesseract OCR 或 Windows OCR 引擎。
"""

from __future__ import annotations

import logging
from typing import Any

from ..engine.types import FindResult, Rect

logger = logging.getLogger(__name__)

_dict_path: str | None = None


def set_dict(path: str) -> dict[str, str]:
    """设置字库路径."""
    global _dict_path
    _dict_path = path
    return {"status": "ok", "dict_path": path}


def ocr_region(rect: Rect | None = None) -> str:
    """识别指定区域文字.

    优先尝试 Tesseract，回退到 Windows OCR.
    """
    from ..engine import com as engine

    img = engine.screenshot(rect)
    result = _tesseract_ocr(img)
    if result:
        return result
    return _windows_ocr(img)


def find_text_region(text: str, rect: Rect | None = None) -> dict[str, Any]:
    """查找文字位置.

    通过 OCR 识别全区域文字，然后查找目标文字。
    """
    recognized = ocr_region(rect)
    if text in recognized:
        return {"found": True, "text": text}
    return {"found": False, "text": text}


def _tesseract_ocr(img) -> str:
    """使用 Tesseract 进行 OCR."""
    try:
        import pytesseract  # type: ignore
        return pytesseract.image_to_string(img, lang="chi_sim+eng")
    except ImportError:
        return ""
    except Exception as e:
        logger.debug(f"Tesseract OCR 失败: {e}")
        return ""


def _windows_ocr(img) -> str:
    """使用 Windows OCR 引擎或 EasyOCR."""
    # 尝试使用 EasyOCR 作为备选方案
    try:
        import easyocr  # type: ignore
        import numpy as np
        
        if not hasattr(_windows_ocr, "_reader"):
            _windows_ocr._reader = easyocr.Reader(["ch_sim", "en"], gpu=False)  # type: ignore
        
        img_array = np.array(img)
        result = _windows_ocr._reader.readtext(img_array, detail=0)  # type: ignore
        return " ".join(result)
    except ImportError:
        logger.debug("EasyOCR 未安装，尝试使用 Windows.Media.Ocr")
    except Exception as e:
        logger.debug(f"EasyOCR 失败: {e}")
    
    # 尝试使用 Windows.Media.Ocr via PowerShell
    try:
        import subprocess
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="png")
            tmp_path = f.name

        ps_script = f'''
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime] | Out-Null

$file = [Windows.Storage.StorageFile]::GetFileFromPathAsync("{tmp_path.replace(chr(92), chr(92)*2)}")
$file.GetAwaiter().GetResult() | Out-Null
$stream = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read)
$stream.GetAwaiter().GetResult() | Out-Null
$decoder = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
$decoder.GetAwaiter().GetResult() | Out-Null
$bitmap = $decoder.GetSoftwareBitmapAsync()
$bitmap.GetAwaiter().GetResult() | Out-Null

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$result = $engine.RecognizeAsync($bitmap)
$ocrResult = $result.GetAwaiter().GetResult()

$ocrResult.Text
'''
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        logger.debug(f"Windows OCR 失败: {result.stderr}")
        return ""
    
    except subprocess.TimeoutExpired:
        logger.debug("Windows OCR 超时")
        return ""
    except Exception as e:
        logger.debug(f"Windows OCR 异常: {e}")
        return ""
