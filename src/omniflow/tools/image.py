"""图色识别 Tools."""

import io
import base64

from ..engine import com as engine
from ..engine.types import Color, Rect


def screenshot(rect: Rect | None = None):
    img = engine.screenshot(rect)
    buf = io.BytesIO()
    img.save(buf, format="png")
    return {
        "image_base64": base64.b64encode(buf.getvalue()).decode("ascii"),
        "width": img.width,
        "height": img.height,
    }


def find_image(image_path: str, rect: Rect | None = None, similarity: float = 0.9):
    return engine.find_image(image_path, rect, similarity)


def find_color(color_hex: str, rect: Rect | None = None, tolerance: int = 0):
    return engine.find_color(Color.from_hex(color_hex), rect, tolerance)


def compare(x: int, y: int, color_hex: str, tolerance: int = 0):
    return engine.compare_color(x, y, Color.from_hex(color_hex), tolerance)


def get_color(x: int, y: int):
    c = engine.get_color(x, y)
    return {"hex": c.to_hex(), "r": c.r, "g": c.g, "b": c.b}
