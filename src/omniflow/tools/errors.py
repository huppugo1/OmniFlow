"""OmniFlow 错误码定义与恢复建议.

格式: ``E + 3 位数字``，按模块分段::

    E0xxx  通用
    E1xxx  窗口相关
    E2xxx  图像/截图相关
    E3xxx  OCR 相关
    E4xxx  键鼠输入相关
    E5xxx  进程内存相关
    E6xxx  系统/程序启动
    E7xxx  工作流
    E8xxx  插件
    E9xxx  workflow 引擎专用

AI 友好的设计：每个错误码都有"恢复建议"（recovery_suggestions），
让 LLM 在看到 error_code 后**自动**知道下一步该做什么，而不必
靠 try-error 反复试错。

用法::

    from omniflow.tools.errors import ErrorCode, get_recovery_suggestions

    # tool 内部出错时：
    return {
        "status": "error",
        "error": "未找到 'QQPCMgr.exe' 进程",
        "error_code": ErrorCode.PROCESS_NOT_FOUND,
    }
    # call_tool 包装层自动加 recovery_suggestions
"""
from __future__ import annotations


class ErrorCode:
    """OmniFlow 统一错误码（字符串常量）."""

    # 通用 (E0xxx)
    UNKNOWN = "E0000"
    INVALID_ARG = "E0001"          # 参数非法
    MISSING_DEP = "E0002"          # 缺依赖（如 OCR 引擎未装）
    TIMEOUT = "E0003"              # 操作超时
    PERMISSION_DENIED = "E0004"    # 权限不足（需 admin）

    # 窗口 (E1xxx)
    WINDOW_NOT_FOUND = "E1001"
    WINDOW_BIND_FAILED = "E1002"
    WINDOW_INVALID_HWND = "E1003"
    WINDOW_CLOSE_FAILED = "E1004"

    # 图像/截图 (E2xxx)
    IMAGE_NOT_FOUND = "E2001"
    TEMPLATE_LOAD_FAILED = "E2002"
    SCREENSHOT_FAILED = "E2003"
    INVALID_REGION = "E2004"

    # OCR (E3xxx)
    OCR_ENGINE_ERROR = "E3001"
    TEXT_NOT_FOUND = "E3002"
    OCR_NOT_INSTALLED = "E3003"

    # 键鼠 (E4xxx)
    INPUT_SEND_FAILED = "E4001"
    INVALID_KEY = "E4002"
    BIND_REQUIRED = "E4003"        # 后台操作需要先 bind_window

    # 内存 (E5xxx)
    MEM_READ_FAILED = "E5001"
    MEM_WRITE_FAILED = "E5002"
    PROCESS_NOT_FOUND = "E5003"
    INVALID_ADDRESS = "E5004"

    # 系统/程序启动 (E6xxx)
    SYSTEM_INFO_FAILED = "E6001"
    PROGRAM_LAUNCH_FAILED = "E6002"
    PROGRAM_NOT_FOUND = "E6003"

    # 工作流 (E7xxx)
    WORKFLOW_NOT_FOUND = "E7001"
    WORKFLOW_VALIDATION_FAILED = "E7002"
    WORKFLOW_SAVE_FAILED = "E7003"

    # 插件 (E8xxx)
    PLUGIN_NOT_FOUND = "E8001"
    PLUGIN_LOAD_FAILED = "E8002"


# ============================================================
# 恢复建议字典
# ============================================================

RECOVERY_SUGGESTIONS: dict[str, list[str]] = {
    # 通用
    ErrorCode.UNKNOWN: [
        "查看 server 日志（agent.log 或启动时 INFO 级日志）获取详细 traceback",
        "检查参数是否符合工具 schema",
    ],
    ErrorCode.INVALID_ARG: [
        "检查参数类型（string/int/float/bool）",
        "检查必填参数是否缺失",
        "参考工具描述中的'参数'部分",
    ],
    ErrorCode.MISSING_DEP: [
        "pip install 缺失的依赖（如 easyocr / pytesseract）",
        "参考 requirements.txt 的可选依赖注释",
    ],
    ErrorCode.TIMEOUT: [
        "增加 wait_timeout_seconds（如 wait_for_window）",
        "检查目标是否真的存在（screenshot 看一下）",
    ],
    ErrorCode.PERMISSION_DENIED: [
        "以管理员身份重新启动 Hermes / OmniFlow",
        "内存读写 / 全局快捷键等需要 admin 权限",
    ],

    # 窗口
    ErrorCode.WINDOW_NOT_FOUND: [
        "用 window_enum 列出所有窗口，确认目标存在",
        "检查 class_name / title 是否拼写正确（部分游戏标题会随状态变）",
        "等待目标程序启动完成（启动后窗口可能延迟出现）",
        "对长生命周期流程改用 wait_for_window 节点（polling 等待）",
    ],
    ErrorCode.WINDOW_BIND_FAILED: [
        "确认窗口未最小化（gdi 模式不能用于最小化窗口）",
        "尝试不同 display_mode：gdi → dx → dx2 → opengl",
        "确认窗口是 32/64 位兼容的（部分老游戏只支持 32 位 OmniFlow 客户端）",
    ],
    ErrorCode.WINDOW_INVALID_HWND: [
        "句柄可能已失效（窗口关闭后），重新 window_find 获取",
        "确认 hwnd 是整数而非字符串",
    ],
    ErrorCode.WINDOW_CLOSE_FAILED: [
        "目标进程可能无响应（卡死），用 taskkill 强制结束",
        "确认窗口存在（window_get_info 验证）",
    ],

    # 图像
    ErrorCode.IMAGE_NOT_FOUND: [
        "降低 similarity 阈值到 0.7-0.8（默认 0.9 偏严）",
        "确认窗口在前台 / 屏幕未被遮挡",
        "用 screenshot 重新截取模板（按当前主题/分辨率）",
        "检查 image_path 路径是否存在（用绝对路径更稳）",
        "如果按钮有 hover/active 状态，准备多张模板",
    ],
    ErrorCode.TEMPLATE_LOAD_FAILED: [
        "检查 image_path 是否为绝对路径",
        "确认文件格式（PIL 支持 PNG/JPG/BMP，不支持 WebP/GIF）",
        "确认文件未损坏（用图片查看器打开）",
    ],
    ErrorCode.SCREENSHOT_FAILED: [
        "检查 DPI 缩放（用 get_screen_size 拿真实像素）",
        "多屏环境确认 region 坐标在主显示器范围内",
        "权限问题：以管理员身份运行",
    ],
    ErrorCode.INVALID_REGION: [
        "region 必须是 {left, top, right, bottom} 且 right > left, bottom > top",
        "坐标不能超出 get_screen_size 范围",
    ],

    # OCR
    ErrorCode.OCR_ENGINE_ERROR: [
        "确认 Tesseract 已安装且在 PATH 中",
        "中文识别需要 Tesseract 的 chi_sim 训练包",
        "查看 server 日志获取 OCR 引擎详细错误",
    ],
    ErrorCode.TEXT_NOT_FOUND: [
        "OCR 准确率受字体/分辨率影响，先 ocr() 看完整识别结果",
        "改用 find_image 找文字的图像模板（更稳）",
        "尝试不同区域 / 缩放",
    ],
    ErrorCode.OCR_NOT_INSTALLED: [
        "pip install pytesseract（最简单）",
        "或安装 Tesseract 完整版 + 语言包",
        "或 pip install easyocr（首次运行会下载模型）",
    ],

    # 输入
    ErrorCode.INPUT_SEND_FAILED: [
        "确认窗口已绑定（后台操作需要 bind_window）",
        "前台操作：确认目标窗口在前台",
    ],
    ErrorCode.INVALID_KEY: [
        "检查 key 是否在合法集合（a-z, 0-9, enter, tab, esc, f1-f12, ctrl, alt, shift, win, space, backspace, arrows）",
        "组合键用 hotkey(keys=['ctrl', 's']) 形式",
    ],
    ErrorCode.BIND_REQUIRED: [
        "后台操作前先 bind_window",
        "前台操作不需要 bind，但要先 window_activate",
    ],

    # 内存
    ErrorCode.MEM_READ_FAILED: [
        "以管理员身份重新启动（读其他进程内存需要 admin）",
        "确认 pid 存在（用 enum_process 查）",
        "确认 address 是 10 进制整数（不是 hex 字符串）",
    ],
    ErrorCode.MEM_WRITE_FAILED: [
        "写入有写保护的进程会被拒绝",
        "以管理员身份运行",
        "反作弊软件可能拦截了 WriteProcessMemory",
    ],
    ErrorCode.PROCESS_NOT_FOUND: [
        "确认进程已启动（tasklist | findstr <name>）",
        "有些进程名带 .exe 后缀（如 notepad.exe）",
    ],
    ErrorCode.INVALID_ADDRESS: [
        "地址必须为非负整数（10 进制）",
        "用 get_module_base + 偏移计算地址",
    ],

    # 系统
    ErrorCode.SYSTEM_INFO_FAILED: [
        "psutil 缺失：pip install psutil",
    ],
    ErrorCode.PROGRAM_LAUNCH_FAILED: [
        "检查 program_path 是绝对路径",
        "ShellExecute 找不到时尝试加 .exe 后缀",
        "用 cmd /c start <name> 替代（PATH 搜索）",
    ],
    ErrorCode.PROGRAM_NOT_FOUND: [
        "确认 program_path 存在（os.path.exists 检查）",
        "PATH 搜索：传短名（如 'notepad'）让 ShellExecute 按 PATH 找",
    ],

    # 工作流
    ErrorCode.WORKFLOW_NOT_FOUND: [
        "workflow_id 是 md5(name)[:12]，用 workflow_list 查 ID",
    ],
    ErrorCode.WORKFLOW_VALIDATION_FAILED: [
        "检查 workflow JSON 的 step 类型是否合法",
        "检查 condition 表达式语法（ast.parse 合法）",
    ],
    ErrorCode.WORKFLOW_SAVE_FAILED: [
        "检查 ~/.omniflow/workflows/ 目录权限",
    ],

    # 插件
    ErrorCode.PLUGIN_NOT_FOUND: [
        "用 plugin_list 查可用插件 ID",
    ],
    ErrorCode.PLUGIN_LOAD_FAILED: [
        "确认 plugin_path 是有效 Python 包",
        "查看 server 日志获取 ImportError 详情",
    ],
}


def get_recovery_suggestions(error_code: str) -> list[str]:
    """根据错误码返回恢复建议."""
    return RECOVERY_SUGGESTIONS.get(error_code, [
        f"未知错误码 {error_code}，请查看 server 日志",
    ])
