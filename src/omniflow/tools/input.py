"""键鼠模拟 Tools."""

from ..engine import com as engine


def press(key: str):
    engine.key_press(key)
    return {"status": "ok"}


def down(key: str):
    engine.key_down(key)
    return {"status": "ok"}


def up(key: str):
    engine.key_up(key)
    return {"status": "ok"}


def type_text(text: str, interval: float = 0.0):
    engine.key_type(text, interval)
    return {"status": "ok"}


def hotkey(*keys: str):
    engine.hotkey(*keys)
    return {"status": "ok"}


def move(x: int, y: int, duration: float = 0.0):
    engine.mouse_move(x, y, duration)
    return {"status": "ok"}


def click(x: int | None = None, y: int | None = None,
           button: str = "left", clicks: int = 1):
    engine.mouse_click(x, y, button, clicks)
    return {"status": "ok"}


def scroll(clicks: int):
    engine.mouse_scroll(clicks)
    return {"status": "ok"}


def get_pos():
    pos = engine.mouse_get_pos()
    return {"x": pos.x, "y": pos.y}
