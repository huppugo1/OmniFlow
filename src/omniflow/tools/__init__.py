"""OmniFlow MCP Tools 模块."""

from . import (
    binding,
    composite,
    detect,
    errors,
    image,
    input,
    memory,
    ocr,
    plugin,
    system,
    window,
    workflow,
)

__all__ = [
    "binding",
    "composite",   # 组合 Tool（click_image / wait_and_click / ocr_and_click）
    "detect",      # 自动模式检测（detect_bind_mode）
    "errors",      # 错误码常量 + 恢复建议
    "image",
    "input",
    "memory",
    "ocr",
    "plugin",
    "system",
    "window",
    "workflow",
]
