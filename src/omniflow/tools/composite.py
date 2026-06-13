"""AI 友好的组合 Tool.

每个组合 Tool 合并 2-3 个原子 Tool 的常见组合，**让 LLM 一次调用
搞定**——降低 token 消耗、降低编排错误率。

**设计原则**：
- **不引入新概念**——只是原子 Tool 的便捷封装
- **返回原子 Tool 的结果**——LLM 仍能识别字段
- **错误码沿用 ErrorCode**——AI 看到的还是统一体系
"""
from __future__ import annotations

import logging
import time
from typing import Any

from .errors import ErrorCode

logger = logging.getLogger(__name__)


def _to_rect(region: dict | None) -> Any:
    """转换 region dict 为 engine.Rect（None 时返回 None）."""
    if not region:
        return None
    from ..engine.types import Rect
    return Rect(
        left=region.get("left", 0),
        top=region.get("top", 0),
        right=region.get("right", 0),
        bottom=region.get("bottom", 0),
    )


# ============================================================
# 1. click_image —— 找图并点击
# ============================================================


def click_image(
    image_path: str,
    similarity: float = 0.9,
    region: dict | None = None,
    button: str = "left",
    clicks: int = 1,
) -> dict:
    """在屏幕找图片，找到后点击其中心.

    合并 ``find_image`` + ``mouse_move`` + ``mouse_click`` 三步为一步。
    """
    from . import image as image_tool
    from . import input as input_tool

    rect = _to_rect(region)
    # 容错：模板图加载失败（FileNotFoundError / PIL.UnidentifiedImageError）转 error_code
    try:
        result = image_tool.find_image(
            image_path=image_path, rect=rect, similarity=similarity,
        )
    except (FileNotFoundError, OSError) as e:
        return {
            "clicked": False,
            "error": f"无法加载模板图: {image_path} ({type(e).__name__}: {e})",
            "error_code": ErrorCode.TEMPLATE_LOAD_FAILED,
            "image_path": image_path,
        }
    if not result.get("found"):
        return {
            "clicked": False,
            "error": f"未找到图片: {image_path}",
            "error_code": ErrorCode.IMAGE_NOT_FOUND,
            "image_path": image_path,
        }

    x, y = result["x"], result["y"]
    input_tool.move(x, y, 0.0)
    input_tool.click(x, y, button, clicks)
    return {
        "clicked": True,
        "x": x,
        "y": y,
        "similarity": result.get("similarity"),
        "image_path": image_path,
    }


# ============================================================
# 2. wait_and_click —— 轮询等图片出现后点击
# ============================================================


def wait_and_click(
    image_path: str,
    timeout: float = 10.0,
    poll_interval: float = 0.5,
    similarity: float = 0.9,
    region: dict | None = None,
    button: str = "left",
    clicks: int = 1,
) -> dict:
    """轮询等图片出现，找到后点击.

    典型用法：等"加载完成"图标消失 / 等"开始游戏"按钮出现。
    """
    start = time.time()
    while time.time() - start < timeout:
        result = click_image(
            image_path=image_path, similarity=similarity,
            region=region, button=button, clicks=clicks,
        )
        if result.get("clicked"):
            result["elapsed"] = time.time() - start
            return result
        time.sleep(poll_interval)

    return {
        "clicked": False,
        "error": f"timeout 等图片出现: {image_path}",
        "error_code": ErrorCode.TIMEOUT,
        "elapsed": timeout,
        "image_path": image_path,
    }


# ============================================================
# 3. ocr_and_click —— OCR 找文字并点击（粗略版）
# ============================================================


def ocr_and_click(
    text: str,
    region: dict | None = None,
    timeout: float = 10.0,
    poll_interval: float = 0.5,
    button: str = "left",
    clicks: int = 1,
) -> dict:
    """OCR 识别区域找文字，找到后点击区域中心.

    ⚠️ **精度警告**：OCR 不返回文字的精确坐标，本 tool 在 ``region`` 的
    **中心点**点击。如果文字不在中心，请用 ``find_image`` 找文字
    的图像模板（更精确）。

    适合：点击区域中央的固定文字（"确定"按钮在对话框中央）。
    """
    from . import ocr as ocr_tool
    from . import input as input_tool

    if not region:
        return {
            "clicked": False,
            "error": "ocr_and_click 需要指定 region（OCR 不返回文字精确坐标）",
            "error_code": ErrorCode.INVALID_ARG,
            "text": text,
        }

    rect = _to_rect(region)
    start = time.time()
    while time.time() - start < timeout:
        recognized = ocr_tool.ocr_region(rect)
        if text in recognized:
            cx = (region["left"] + region["right"]) // 2
            cy = (region["top"] + region["bottom"]) // 2
            input_tool.click(cx, cy, button, clicks)
            return {
                "clicked": True,
                "x": cx,
                "y": cy,
                "text": text,
                "elapsed": time.time() - start,
            }
        time.sleep(poll_interval)

    return {
        "clicked": False,
        "error": f"timeout 等文字出现: {text}",
        "error_code": ErrorCode.TIMEOUT,
        "elapsed": timeout,
        "text": text,
    }
