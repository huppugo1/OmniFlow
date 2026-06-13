"""插件系统 - 扩展 OmniFlow 能力.

支持:
- 插件热加载 (Python 模块)
- 自定义 MCP Tool 注册
- 插件生命周期管理 (安装/卸载/启用/禁用)
"""

from __future__ import annotations

import importlib
import json
import logging
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PLUGIN_DIR = Path(__file__).parent.parent.parent / "plugins"
PLUGIN_DIR.mkdir(parents=True, exist_ok=True)


class PluginStatus(str, Enum):
    """插件状态."""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginInfo:
    """插件元信息."""
    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    status: PluginStatus = PluginStatus.INSTALLED
    tools: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> PluginInfo:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            status=PluginStatus(data.get("status", "installed")),
            tools=data.get("tools", []),
        )


# 插件注册表
_plugins: dict[str, PluginInfo] = {}


def _load_plugins() -> None:
    """扫描并加载插件目录."""
    global _plugins
    _plugins.clear()

    manifest_path = PLUGIN_DIR / "plugins.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in data.get("plugins", []):
                info = PluginInfo.from_dict(item)
                _plugins[info.id] = info
        except Exception as e:
            logger.warning(f"加载插件清单失败: {e}")


def _save_manifest() -> None:
    """保存插件清单."""
    manifest = {
        "plugins": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "status": p.status.value,
                "tools": p.tools,
            }
            for p in _plugins.values()
        ]
    }
    manifest_path = PLUGIN_DIR / "plugins.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def list_plugins() -> dict:
    """列出已安装的插件."""
    _load_plugins()
    return {
        "plugins": [
            {
                "id": p.id, "name": p.name, "version": p.version,
                "description": p.description, "author": p.author,
                "status": p.status.value, "tools": p.tools,
            }
            for p in _plugins.values()
        ],
        "count": len(_plugins),
    }


def install(plugin_path: str) -> dict:
    """安装插件.

    支持:
    - 本地路径 (目录或 .py 文件)
    - 插件名称 (从内置仓库安装)
    """
    _load_plugins()

    path = Path(plugin_path)

    if not path.exists():
        # 尝试作为内置插件名
        builtin = PLUGIN_DIR / plugin_path
        if builtin.exists():
            path = builtin
        else:
            return {"error": f"插件未找到: {plugin_path}"}

    plugin_id = path.stem

    if plugin_id in _plugins:
        return {"error": f"插件已安装: {plugin_id}"}

    info = PluginInfo(
        id=plugin_id,
        name=plugin_id,
        description=f"Plugin from {plugin_path}",
    )
    _plugins[plugin_id] = info
    _save_manifest()

    # 尝试加载插件模块
    try:
        if path.is_dir():
            sys.path.insert(0, str(path.parent))
            mod = importlib.import_module(plugin_id)
        else:
            spec = importlib.util.spec_from_file_location(plugin_id, str(path))  # type: ignore
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            else:
                raise ImportError(f"无法加载模块: {path}")

        # 尝试获取插件元信息
        if hasattr(mod, "PLUGIN_INFO"):
            pinfo = mod.PLUGIN_INFO
            _plugins[plugin_id].name = pinfo.get("name", plugin_id)
            _plugins[plugin_id].version = pinfo.get("version", "0.1.0")
            _plugins[plugin_id].description = pinfo.get("description", "")
            _plugins[plugin_id].author = pinfo.get("author", "")

        # 记录插件提供的工具
        if hasattr(mod, "get_tools"):
            _plugins[plugin_id].tools = [t.__name__ if callable(t) else str(t) for t in mod.get_tools()]  # type: ignore

        _plugins[plugin_id].status = PluginStatus.ENABLED
        _save_manifest()

        return {"id": plugin_id, "status": "installed and enabled"}
    except Exception as e:
        _plugins[plugin_id].status = PluginStatus.ERROR
        _save_manifest()
        return {"id": plugin_id, "status": "installed", "load_error": str(e)}


def uninstall(plugin_id: str) -> dict:
    """卸载插件."""
    _load_plugins()
    if plugin_id not in _plugins:
        return {"error": f"插件不存在: {plugin_id}"}

    # 尝试从 sys.modules 移除
    if plugin_id in sys.modules:
        del sys.modules[plugin_id]

    del _plugins[plugin_id]
    _save_manifest()
    return {"id": plugin_id, "status": "uninstalled"}


def enable(plugin_id: str) -> dict:
    """启用插件."""
    _load_plugins()
    if plugin_id not in _plugins:
        return {"error": f"插件不存在: {plugin_id}"}
    _plugins[plugin_id].status = PluginStatus.ENABLED
    _save_manifest()
    return {"id": plugin_id, "status": "enabled"}


def disable(plugin_id: str) -> dict:
    """禁用插件."""
    _load_plugins()
    if plugin_id not in _plugins:
        return {"error": f"插件不存在: {plugin_id}"}
    _plugins[plugin_id].status = PluginStatus.DISABLED
    _save_manifest()
    return {"id": plugin_id, "status": "disabled"}
