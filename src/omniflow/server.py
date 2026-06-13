"""OmniFlow MCP Server - 主入口.

使用 MCP Python SDK 注册所有自动化 Tools。
"""

from __future__ import annotations

import base64
import io
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import (
    CallToolResult,
    TextContent,
    ImageContent,
    Tool,
)
from PIL import Image

from .engine import com as engine
from .engine.types import (
    BindOptions,
    Color,
    Rect,
)
from .tools import (
    binding,
    image,
    input as input_module,
    memory,
    ocr,
    plugin,
    system,
    window,
    workflow,
)

logger = logging.getLogger(__name__)

# ============================================================
# Workflow dispatcher：让 workflow 引擎能反向调用本 server 的工具
# ============================================================


async def _tool_dispatcher(tool_name: str, arguments: dict) -> dict:
    """异步 dispatcher：把 workflow 里的 TOOL_CALL 转发到本地 _handle_tool.

    workflow.py 的 _execute_step 会用 iscoroutine() 检查本返回值，
    是 coroutine 就 await。
    """
    return await _handle_tool(tool_name, arguments)


server = Server("omniflow")

# ============================================================
# 辅助函数
# ============================================================


def _to_json(obj: Any) -> str:
    """将对象序列化为 JSON 字符串."""
    import dataclasses

    class _Encoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

    return json.dumps(obj, ensure_ascii=False, cls=_Encoder)


def _image_to_base64(img: Image.Image, fmt: str = "png") -> str:
    """将 PIL Image 转为 base64 字符串."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ============================================================
# 工具定义
# ============================================================

TOOLS = [
    # ---- 窗口 ----
    Tool(
        name="window_find",
        description="按标题、类名或PID查找窗口",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "窗口标题"},
                "class_name": {"type": "string", "description": "窗口类名"},
                "pid": {"type": "integer", "description": "进程ID"},
            },
        },
    ),
    Tool(
        name="window_enum",
        description="枚举所有可见的顶层窗口",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="window_get_info",
        description="获取指定窗口的详细信息",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
            },
            "required": ["hwnd"],
        },
    ),
    Tool(
        name="window_set_top",
        description="设置窗口置顶或取消置顶",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
                "on_top": {"type": "boolean", "description": "是否置顶"},
            },
            "required": ["hwnd"],
        },
    ),
    Tool(
        name="window_show",
        description="显示或隐藏窗口",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
                "show": {"type": "boolean", "description": "True显示/False隐藏"},
            },
            "required": ["hwnd", "show"],
        },
    ),
    Tool(
        name="window_activate",
        description="激活窗口到前台",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
            },
            "required": ["hwnd"],
        },
    ),
    Tool(
        name="window_close",
        description="关闭窗口（发送 WM_CLOSE 消息，等同于点击右上角 X）",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
            },
            "required": ["hwnd"],
        },
    ),
    # ---- 绑定 ----
    Tool(
        name="bind_window",
        description="绑定窗口，设置图色和键鼠模式",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
                "display_mode": {"type": "string", "description": "图色模式: gdi/dx/dx2/opengl"},
                "mouse_mode": {"type": "string", "description": "鼠标模式: normal/windows"},
                "keyboard_mode": {"type": "string", "description": "键盘模式: normal/windows"},
            },
            "required": ["hwnd"],
        },
    ),
    Tool(
        name="unbind_window",
        description="解绑窗口",
        inputSchema={
            "type": "object",
            "properties": {
                "hwnd": {"type": "integer", "description": "窗口句柄"},
            },
            "required": ["hwnd"],
        },
    ),
    # ---- 图色 ----
    Tool(
        name="screenshot",
        description="截图指定区域，返回 Base64 编码的图片",
        inputSchema={
            "type": "object",
            "properties": {
                "left": {"type": "integer", "description": "区域左坐标"},
                "top": {"type": "integer", "description": "区域上坐标"},
                "right": {"type": "integer", "description": "区域右坐标"},
                "bottom": {"type": "integer", "description": "区域下坐标"},
            },
        },
    ),
    Tool(
        name="find_image",
        description="在屏幕指定区域查找图片，返回坐标和相似度",
        inputSchema={
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "模板图片路径"},
                "left": {"type": "integer", "description": "搜索区域左坐标"},
                "top": {"type": "integer", "description": "搜索区域上坐标"},
                "right": {"type": "integer", "description": "搜索区域右坐标"},
                "bottom": {"type": "integer", "description": "搜索区域下坐标"},
                "similarity": {"type": "number", "description": "相似度阈值 0.0-1.0"},
            },
            "required": ["image_path"],
        },
    ),
    Tool(
        name="find_color",
        description="在屏幕指定区域查找颜色，返回坐标",
        inputSchema={
            "type": "object",
            "properties": {
                "color": {"type": "string", "description": "颜色值，如 'FF0000'"},
                "left": {"type": "integer", "description": "搜索区域左坐标"},
                "top": {"type": "integer", "description": "搜索区域上坐标"},
                "right": {"type": "integer", "description": "搜索区域右坐标"},
                "bottom": {"type": "integer", "description": "搜索区域下坐标"},
                "tolerance": {"type": "integer", "description": "颜色容差 0-255"},
            },
            "required": ["color"],
        },
    ),
    Tool(
        name="compare_color",
        description="比较指定坐标的颜色是否匹配期望值",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X坐标"},
                "y": {"type": "integer", "description": "Y坐标"},
                "color": {"type": "string", "description": "期望颜色，如 'FF0000'"},
                "tolerance": {"type": "integer", "description": "颜色容差 0-255"},
            },
            "required": ["x", "y", "color"],
        },
    ),
    Tool(
        name="get_color",
        description="获取指定坐标的颜色值",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X坐标"},
                "y": {"type": "integer", "description": "Y坐标"},
            },
            "required": ["x", "y"],
        },
    ),
    # ---- OCR ----
    Tool(
        name="ocr",
        description="识别指定区域内的文字",
        inputSchema={
            "type": "object",
            "properties": {
                "left": {"type": "integer", "description": "区域左坐标"},
                "top": {"type": "integer", "description": "区域上坐标"},
                "right": {"type": "integer", "description": "区域右坐标"},
                "bottom": {"type": "integer", "description": "区域下坐标"},
            },
        },
    ),
    Tool(
        name="find_text",
        description="在屏幕上查找文字位置",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要查找的文字"},
                "left": {"type": "integer", "description": "搜索区域左坐标"},
                "top": {"type": "integer", "description": "搜索区域上坐标"},
                "right": {"type": "integer", "description": "搜索区域右坐标"},
                "bottom": {"type": "integer", "description": "搜索区域下坐标"},
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="set_ocr_dict",
        description="设置OCR字库文件路径",
        inputSchema={
            "type": "object",
            "properties": {
                "dict_path": {"type": "string", "description": "字库文件路径"},
            },
            "required": ["dict_path"],
        },
    ),
    # ---- 键鼠 ----
    Tool(
        name="key_press",
        description="按下并释放键盘按键",
        inputSchema={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "按键名称"},
            },
            "required": ["key"],
        },
    ),
    Tool(
        name="key_down",
        description="按住键盘按键不放",
        inputSchema={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "按键名称"},
            },
            "required": ["key"],
        },
    ),
    Tool(
        name="key_up",
        description="释放键盘按键",
        inputSchema={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "按键名称"},
            },
            "required": ["key"],
        },
    ),
    Tool(
        name="key_type",
        description="输入字符串文本",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要输入的文本"},
                "interval": {"type": "number", "description": "字间间隔(秒)"},
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="hotkey",
        description="发送组合键，如 Ctrl+C",
        inputSchema={
            "type": "object",
            "properties": {
                "keys": {"type": "array", "items": {"type": "string"}, "description": "按键列表"},
            },
            "required": ["keys"],
        },
    ),
    Tool(
        name="mouse_move",
        description="移动鼠标到指定坐标",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X坐标"},
                "y": {"type": "integer", "description": "Y坐标"},
                "duration": {"type": "number", "description": "移动耗时(秒)"},
            },
            "required": ["x", "y"],
        },
    ),
    Tool(
        name="mouse_click",
        description="鼠标点击",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X坐标（可选）"},
                "y": {"type": "integer", "description": "Y坐标（可选）"},
                "button": {"type": "string", "description": "按键: left/right/middle"},
                "clicks": {"type": "integer", "description": "点击次数"},
            },
        },
    ),
    Tool(
        name="mouse_scroll",
        description="鼠标滚轮",
        inputSchema={
            "type": "object",
            "properties": {
                "clicks": {"type": "integer", "description": "滚动量，正向上负向下"},
            },
            "required": ["clicks"],
        },
    ),
    Tool(
        name="mouse_get_pos",
        description="获取当前鼠标坐标",
        inputSchema={"type": "object", "properties": {}},
    ),
    # ---- 内存 ----
    Tool(
        name="mem_read",
        description="读取进程内存",
        inputSchema={
            "type": "object",
            "properties": {
                "pid": {"type": "integer", "description": "进程ID"},
                "address": {"type": "integer", "description": "内存地址"},
                "size": {"type": "integer", "description": "读取字节数"},
            },
            "required": ["pid", "address"],
        },
    ),
    Tool(
        name="mem_write",
        description="写入进程内存",
        inputSchema={
            "type": "object",
            "properties": {
                "pid": {"type": "integer", "description": "进程ID"},
                "address": {"type": "integer", "description": "内存地址"},
                "data_hex": {"type": "string", "description": "要写入的数据(十六进制字符串)"},
            },
            "required": ["pid", "address", "data_hex"],
        },
    ),
    Tool(
        name="get_module_base",
        description="获取进程模块基址",
        inputSchema={
            "type": "object",
            "properties": {
                "pid": {"type": "integer", "description": "进程ID"},
                "module_name": {"type": "string", "description": "模块名称"},
            },
            "required": ["pid"],
        },
    ),
    # ---- 系统 ----
    Tool(
        name="get_system_info",
        description="获取系统信息：CPU、内存、分辨率、操作系统",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_screen_size",
        description="获取屏幕分辨率",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="enum_process",
        description="枚举运行中的进程",
        inputSchema={"type": "object", "properties": {}},
    ),
    # ---- 工作流 ----
    Tool(
        name="workflow_run",
        description="执行指定工作流",
        inputSchema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID或名称"},
            },
            "required": ["workflow_id"],
        },
    ),
    Tool(
        name="workflow_list",
        description="列出所有已保存的工作流",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="workflow_save",
        description="保存工作流",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "工作流名称"},
                "steps": {"type": "array", "description": "工作流步骤列表"},
            },
            "required": ["name", "steps"],
        },
    ),
    Tool(
        name="workflow_delete",
        description="删除工作流",
        inputSchema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID或名称"},
            },
            "required": ["workflow_id"],
        },
    ),
    Tool(
        name="workflow_pause",
        description="暂停工作流执行",
        inputSchema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID"},
            },
            "required": ["workflow_id"],
        },
    ),
    Tool(
        name="workflow_resume",
        description="恢复工作流执行",
        inputSchema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "工作流ID"},
            },
            "required": ["workflow_id"],
        },
    ),
    # ---- 插件 ----
    Tool(
        name="plugin_list",
        description="列出已安装的插件",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="plugin_install",
        description="安装插件",
        inputSchema={
            "type": "object",
            "properties": {
                "plugin_path": {"type": "string", "description": "插件路径或名称"},
            },
            "required": ["plugin_path"],
        },
    ),
    Tool(
        name="plugin_uninstall",
        description="卸载插件",
        inputSchema={
            "type": "object",
            "properties": {
                "plugin_id": {"type": "string", "description": "插件ID"},
            },
            "required": ["plugin_id"],
        },
    ),
    Tool(
        name="plugin_enable",
        description="启用插件",
        inputSchema={
            "type": "object",
            "properties": {
                "plugin_id": {"type": "string", "description": "插件ID"},
            },
            "required": ["plugin_id"],
        },
    ),
    Tool(
        name="plugin_disable",
        description="禁用插件",
        inputSchema={
            "type": "object",
            "properties": {
                "plugin_id": {"type": "string", "description": "插件ID"},
            },
            "required": ["plugin_id"],
        },
    ),
]

# ============================================================
# 处理器注册
# ============================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
    """分发工具调用."""
    try:
        result = await _handle_tool(name, arguments)

        # 截图返回图片
        if name == "screenshot" and isinstance(result, dict) and "image_base64" in result:
            return [
                TextContent(type="text", text=f"截图完成，尺寸: {result.get('width')}x{result.get('height')}"),
                ImageContent(type="image", data=result["image_base64"], mimeType="image/png"),
            ]

        return [TextContent(type="text", text=_to_json(result))]
    except Exception as e:
        logger.exception(f"工具 {name} 执行失败")
        return [TextContent(type="text", text=_to_json({"error": str(e)}))]


async def _handle_tool(name: str, args: dict) -> Any:
    """实际处理工具调用."""
    # ---- 窗口 ----
    if name == "window_find":
        return engine.find_window(
            title=args.get("title", ""),
            class_name=args.get("class_name", ""),
            pid=args.get("pid", 0),
        )
    elif name == "window_enum":
        return engine.enum_windows()
    elif name == "window_get_info":
        return engine.get_window_info(args["hwnd"])
    elif name == "window_set_top":
        engine.set_window_top(args["hwnd"], args.get("on_top", True))
        return {"status": "ok"}
    elif name == "window_show":
        engine.show_window(args["hwnd"], args["show"])
        return {"status": "ok"}
    elif name == "window_activate":
        engine.activate_window(args["hwnd"])
        return {"status": "ok"}
    elif name == "window_close":
        engine.close_window(args["hwnd"])
        return {"status": "ok", "hwnd": args["hwnd"]}

    # ---- 绑定 ----
    elif name == "bind_window":
        opts = BindOptions(
            hwnd=args["hwnd"],
            display_mode=args.get("display_mode", "gdi"),
            mouse_mode=args.get("mouse_mode", "normal"),
            keyboard_mode=args.get("keyboard_mode", "normal"),
        )
        ok = engine.bind_window(opts)
        return {"status": "ok", "bound": ok}
    elif name == "unbind_window":
        engine.unbind_window(args["hwnd"])
        return {"status": "ok"}

    # ---- 图色 ----
    elif name == "screenshot":
        rect = _parse_rect(args) if any(k in args for k in ("left", "top", "right", "bottom")) else None
        img = engine.screenshot(rect)
        return {
            "image_base64": _image_to_base64(img),
            "width": img.width,
            "height": img.height,
        }
    elif name == "find_image":
        rect = _parse_rect(args)
        result = engine.find_image(
            image_path=args["image_path"],
            rect=rect,
            similarity=args.get("similarity", 0.9),
        )
        return result
    elif name == "find_color":
        rect = _parse_rect(args)
        result = engine.find_color(
            color=Color.from_hex(args["color"]),
            rect=rect,
            tolerance=args.get("tolerance", 0),
        )
        return result
    elif name == "compare_color":
        result = engine.compare_color(
            x=args["x"], y=args["y"],
            expected=Color.from_hex(args["color"]),
            tolerance=args.get("tolerance", 0),
        )
        return {"match": result}
    elif name == "get_color":
        color = engine.get_color(args["x"], args["y"])
        return {"hex": color.to_hex(), "r": color.r, "g": color.g, "b": color.b}

    # ---- OCR ----
    elif name == "ocr":
        rect = _parse_rect(args)
        text = ocr.ocr_region(rect)
        return {"text": text}
    elif name == "find_text":
        rect = _parse_rect(args)
        result = ocr.find_text_region(args["text"], rect)
        return result
    elif name == "set_ocr_dict":
        ocr.set_dict(args["dict_path"])
        return {"status": "ok"}

    # ---- 键鼠 ----
    elif name == "key_press":
        engine.key_press(args["key"])
        return {"status": "ok"}
    elif name == "key_down":
        engine.key_down(args["key"])
        return {"status": "ok"}
    elif name == "key_up":
        engine.key_up(args["key"])
        return {"status": "ok"}
    elif name == "key_type":
        engine.key_type(args["text"], args.get("interval", 0.0))
        return {"status": "ok"}
    elif name == "hotkey":
        engine.hotkey(*args["keys"])
        return {"status": "ok"}
    elif name == "mouse_move":
        engine.mouse_move(args["x"], args["y"], args.get("duration", 0.0))
        return {"status": "ok"}
    elif name == "mouse_click":
        engine.mouse_click(
            x=args.get("x"), y=args.get("y"),
            button=args.get("button", "left"),
            clicks=args.get("clicks", 1),
        )
        return {"status": "ok"}
    elif name == "mouse_scroll":
        engine.mouse_scroll(args["clicks"])
        return {"status": "ok"}
    elif name == "mouse_get_pos":
        pos = engine.mouse_get_pos()
        return {"x": pos.x, "y": pos.y}

    # ---- 内存 ----
    elif name == "mem_read":
        data = engine.mem_read(args["pid"], args["address"], args.get("size", 4))
        return {"data_hex": data.hex(), "size": len(data)}
    elif name == "mem_write":
        data_hex = args["data_hex"]
        data = bytes.fromhex(data_hex)
        ok = engine.mem_write(args["pid"], args["address"], data)
        return {"status": "ok", "written": ok}
    elif name == "get_module_base":
        base = engine.get_module_base(args["pid"], args.get("module_name", ""))
        return {"base": base}

    # ---- 系统 ----
    elif name == "get_system_info":
        return engine.get_system_info()
    elif name == "get_screen_size":
        w, h = engine.get_screen_size()
        return {"width": w, "height": h}
    elif name == "enum_process":
        return engine.enum_processes()
    elif name == "run_program":
        return system.run_program(
            args["program_path"],
            args.get("args"),
            args.get("cwd")
        )

    # ---- 工作流 ----
    elif name == "workflow_run":
        # 注入 dispatcher：让 workflow 里的 TOOL_CALL 步骤真调本地工具
        return await workflow.run(
            args["workflow_id"],
            tool_dispatcher=_tool_dispatcher,
        )
    elif name == "workflow_list":
        return workflow.list_workflows()
    elif name == "workflow_save":
        return workflow.save(args["name"], args["steps"])
    elif name == "workflow_delete":
        return workflow.delete(args["workflow_id"])
    elif name == "workflow_pause":
        return workflow.pause(args["workflow_id"])
    elif name == "workflow_resume":
        return workflow.resume(args["workflow_id"])

    # ---- 插件 ----
    elif name == "plugin_list":
        return plugin.list_plugins()
    elif name == "plugin_install":
        return plugin.install(args["plugin_path"])
    elif name == "plugin_uninstall":
        return plugin.uninstall(args["plugin_id"])
    elif name == "plugin_enable":
        return plugin.enable(args["plugin_id"])
    elif name == "plugin_disable":
        return plugin.disable(args["plugin_id"])

    else:
        raise ValueError(f"未知工具: {name}")


def _parse_rect(args: dict) -> Rect | None:
    """从参数中解析 Rect."""
    keys = {"left", "top", "right", "bottom"}
    if keys.intersection(args):
        return Rect(
            left=args.get("left", 0),
            top=args.get("top", 0),
            right=args.get("right", 0),
            bottom=args.get("bottom", 0),
        )
    return None


# ============================================================
# 入口
# ============================================================


async def main():
    """启动 MCP Server."""
    import mcp.server.stdio

    logger.info("OmniFlow MCP Server 启动中...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
