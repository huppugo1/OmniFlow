"""窗口操作 Tools."""

from ..engine import com as engine


def find(title: str = "", class_name: str = "", pid: int = 0):
    return engine.find_window(title=title, class_name=class_name, pid=pid)


def enum():
    return engine.enum_windows()


def get_info(hwnd: int):
    return engine.get_window_info(hwnd)


def set_top(hwnd: int, on_top: bool = True):
    engine.set_window_top(hwnd, on_top)
    return {"status": "ok"}


def show(hwnd: int, show: bool = True):
    engine.show_window(hwnd, show)
    return {"status": "ok"}


def activate(hwnd: int):
    engine.activate_window(hwnd)
    return {"status": "ok"}


def close(hwnd: int):
    """关闭窗口（发送 WM_CLOSE）."""
    engine.close_window(hwnd)
    return {"status": "ok", "hwnd": hwnd}
