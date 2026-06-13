"""窗口绑定 Tools."""

from ..engine import com as engine
from ..engine.types import BindOptions


def bind(hwnd: int, display_mode: str = "gdi",
         mouse_mode: str = "normal", keyboard_mode: str = "normal"):
    opts = BindOptions(
        hwnd=hwnd,
        display_mode=display_mode,
        mouse_mode=mouse_mode,
        keyboard_mode=keyboard_mode,
    )
    ok = engine.bind_window(opts)
    return {"status": "ok", "bound": ok}


def unbind(hwnd: int):
    engine.unbind_window(hwnd)
    return {"status": "ok"}
