"""自动模式检测 / 智能推荐工具.

让 AI 不必手选 ``gdi/dx/dx2/opengl``——直接调 ``detect_bind_mode(hwnd)``，
返回"推荐 + 备选 + 健康检查"。

**当前限制**（2026-06-13）：
``engine.bind_window`` 是 stub（永远返回 True），4 种 display_mode
实际**等价**——都走 pyautogui 截图。本工具暂时作为"健康检查"，
**固定推荐 gdi**（兼容性最好）。未来 ``engine.bind_window`` 实现
真检测后，本工具能自动给出"哪个 mode 真能 bind"的精确推荐。
"""
from __future__ import annotations

import logging
from typing import Any

from ..engine import com as engine
from ..engine.types import BindOptions

logger = logging.getLogger(__name__)


def detect_bind_mode(hwnd: int) -> dict:
    """自动检测 hwnd 的最佳绑定模式.

    **健康检查逻辑**（当前）：
    1. 依次尝试 4 种 display_mode（gdi → dx → dx2 → opengl）
    2. 每个 mode 都调 bind_window + screenshot
    3. 验证 screenshot 返回非空 PIL Image
    4. 报告哪些 mode 截图成功 / 失败

    **推荐逻辑**（当前）：
    固定返回 ``gdi``——兼容性最好、不需要 Hook 注入、不会触发反作弊。
    未来 engine.bind_window 真实现后，本函数能自动检测并返回最佳。

    **返回**::

        {
            "recommended": "gdi",
            "alternatives": ["dx", "dx2", "opengl"],
            "details": {
                "gdi":   {"bound": True, "screenshot_ok": True, "size": "1920x1080"},
                "dx":    {"bound": True, "screenshot_ok": True, "size": "1920x1080"},
                "dx2":   {"bound": True, "screenshot_ok": True, "size": "1920x1080"},
                "opengl": {"bound": True, "screenshot_ok": True, "size": "1920x1080"},
            },
            "note": "engine.bind_window 当前是 stub；4 种 mode 实际等价。推荐 gdi 因为兼容性最好。"
        }
    """
    modes = ["gdi", "dx", "dx2", "opengl"]
    details: dict[str, dict[str, Any]] = {}

    for mode in modes:
        try:
            # 1. bind
            opts = BindOptions(
                hwnd=hwnd,
                display_mode=mode,
                mouse_mode="normal",
                keyboard_mode="normal",
            )
            engine.bind_window(opts)
            # 2. 截图验证
            try:
                img = engine.screenshot(None)
                screenshot_ok = (
                    img is not None
                    and hasattr(img, "width")
                    and img.width > 0
                    and img.height > 0
                )
                size_str = f"{img.width}x{img.height}" if screenshot_ok else None
            except Exception as e:
                screenshot_ok = False
                size_str = None
                logger.debug(f"screenshot 失败 ({mode}): {e}")

            # 3. 立即解绑，避免影响后续测试
            try:
                engine.unbind_window(hwnd)
            except Exception:
                pass

            details[mode] = {
                "bound": True,
                "screenshot_ok": screenshot_ok,
                "size": size_str,
            }
        except Exception as e:
            details[mode] = {
                "bound": False,
                "screenshot_ok": False,
                "error": f"{type(e).__name__}: {e}",
            }

    # 当前固定推荐 gdi；未来根据 details 自动选
    all_ok = all(d.get("screenshot_ok") for d in details.values())
    return {
        "recommended": "gdi",
        "alternatives": [m for m in modes if m != "gdi"],
        "details": details,
        "all_modes_working": all_ok,
        "note": (
            "engine.bind_window 当前是 stub（永远 True），4 种 mode 实际等价。"
            "推荐 gdi 因为兼容性最好、不需要 Hook 注入。"
            "未来 engine.bind_window 真实现后，本函数能自动检测并返回最佳 mode。"
        ),
    }
