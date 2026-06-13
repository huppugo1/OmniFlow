"""系统相关 Tools."""

from __future__ import annotations

import subprocess

import win32api
import win32con

from ..engine import com as engine


def get_info():
    return engine.get_system_info()


def get_screen_size():
    w, h = engine.get_screen_size()
    return {"width": w, "height": h}


def enum_process():
    return engine.enum_processes()


def run_program(program_path: str, args: list[str] | None = None, cwd: str | None = None) -> dict:
    """启动一个程序.

    Args:
        program_path: 完整可执行文件路径，或系统可解析的名称（ShellExecute 会按
                       PATH 搜索、识别 .lnk 快捷方式）。
        args: 命令行参数列表（可选）。为 None 时走 ShellExecute；非空时走
              subprocess.Popen。
        cwd: 进程工作目录（可选）。

    Returns:
        ``{"status": "ok", "pid": int, "path": str}`` 成功时；
        ``{"status": "error", "error": str}`` 失败时。
    """
    try:
        if args is None:
            # ShellExecute: 能解析 .lnk 快捷方式、按 PATH 搜索、关联文件类型
            win32api.ShellExecute(
                None, "open", program_path, None, cwd, win32con.SW_SHOWNORMAL,
            )
            return {"status": "ok", "pid": None, "path": program_path}
        else:
            cmd = [program_path] + list(args)
            proc = subprocess.Popen(cmd, cwd=cwd)
            return {"status": "ok", "pid": proc.pid, "path": program_path}
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}

