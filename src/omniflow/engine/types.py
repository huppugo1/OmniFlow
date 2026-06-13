"""类型定义 - 引擎层的通用数据结构."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Point:
    """坐标点."""
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


@dataclass
class Rect:
    """矩形区域."""
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def center(self) -> Point:
        return Point(
            self.left + self.width // 2,
            self.top + self.height // 2,
        )

    def to_tuple(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.right, self.bottom)


@dataclass
class WindowInfo:
    """窗口信息."""
    hwnd: int
    title: str = ""
    class_name: str = ""
    pid: int = 0
    rect: Optional[Rect] = None
    is_visible: bool = False
    is_minimized: bool = False
    parent_hwnd: int = 0


@dataclass
class Color:
    """颜色."""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """从十六进制字符串创建颜色，如 'FF0000' 或 '#FF0000'."""
        hex_str = hex_str.lstrip("#")
        return cls(
            r=int(hex_str[0:2], 16),
            g=int(hex_str[2:4], 16),
            b=int(hex_str[4:6], 16),
        )

    @classmethod
    def from_int(cls, value: int) -> "Color":
        """从 0xRRGGBB 整数创建颜色."""
        return cls(
            r=(value >> 16) & 0xFF,
            g=(value >> 8) & 0xFF,
            b=value & 0xFF,
        )

    def to_hex(self) -> str:
        return f"{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_int(self) -> int:
        return (self.r << 16) | (self.g << 8) | self.b

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)


@dataclass
class FindResult:
    """查找结果."""
    found: bool = False
    x: int = 0
    y: int = 0
    similarity: float = 0.0
    name: str = ""


@dataclass
class ProcessInfo:
    """进程信息."""
    pid: int
    name: str = ""
    title: str = ""
    hwnd: int = 0

    def __hash__(self) -> int:
        return hash(self.pid)


@dataclass
class SystemInfo:
    """系统信息."""
    cpu_percent: float = 0.0
    memory_total_gb: float = 0.0
    memory_used_gb: float = 0.0
    screen_width: int = 0
    screen_height: int = 0
    os_version: str = ""


@dataclass
class BindOptions:
    """窗口绑定选项."""
    hwnd: int = 0
    display_mode: str = "gdi"      # gdi / dx / dx2 / opengl
    mouse_mode: str = "normal"     # normal / windows
    keyboard_mode: str = "normal"
