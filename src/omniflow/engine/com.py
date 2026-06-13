"""Win32 自动化引擎 - 基于 pywin32 + pyautogui 实现.

提供窗口操作、图色识别、键鼠模拟、内存操作等底层能力。
"""

from __future__ import annotations

import ctypes
import time
from ctypes import wintypes

import pyautogui
import win32api
import win32con
import win32gui
import win32process
from PIL import Image

from .types import (
    BindOptions,
    Color,
    FindResult,
    Point,
    ProcessInfo,
    Rect,
    SystemInfo,
    WindowInfo,
)

# --- 窗口操作 ---


def enum_windows() -> list[WindowInfo]:
    """枚举所有顶层窗口."""
    windows: list[WindowInfo] = []

    def _callback(hwnd: int, _param: list) -> bool:
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            rect = get_window_rect(hwnd)
            is_minimized = win32gui.IsIconic(hwnd)
            info = WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                pid=pid,
                rect=rect,
                is_visible=True,
                is_minimized=is_minimized,
            )
            windows.append(info)
        return True

    win32gui.EnumWindows(_callback, None)
    return windows


def find_window(title: str = "", class_name: str = "", pid: int = 0) -> WindowInfo | None:
    """查找窗口."""
    hwnd = win32gui.FindWindow(class_name or None, title or None)
    if hwnd:
        return get_window_info(hwnd)

    # 按标题部分匹配搜索
    if title:
        for w in enum_windows():
            if title.lower() in w.title.lower():
                if pid and w.pid != pid:
                    continue
                return w

    return None


def get_window_info(hwnd: int) -> WindowInfo:
    """获取窗口详细信息."""
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    rect = get_window_rect(hwnd)
    is_visible = win32gui.IsWindowVisible(hwnd)
    is_minimized = win32gui.IsIconic(hwnd)
    parent_hwnd = win32gui.GetParent(hwnd)
    return WindowInfo(
        hwnd=hwnd,
        title=title,
        class_name=class_name,
        pid=pid,
        rect=rect,
        is_visible=is_visible,
        is_minimized=is_minimized,
        parent_hwnd=parent_hwnd,
    )


def get_window_rect(hwnd: int) -> Rect:
    """获取窗口矩形."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return Rect(left=left, top=top, right=right, bottom=bottom)


def set_window_top(hwnd: int, on_top: bool = True) -> None:
    """设置窗口置顶."""
    flag = win32con.HWND_TOPMOST if on_top else win32con.HWND_NOTOPMOST
    win32gui.SetWindowPos(hwnd, flag, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


def show_window(hwnd: int, show: bool = True) -> None:
    """显示 / 隐藏窗口."""
    if show:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)


def close_window(hwnd: int) -> None:
    """关闭窗口（向窗口发送 WM_CLOSE 消息，触发 OnClose 事件优雅退出）.

    与 ``show_window(show=False)`` 不同：``WM_CLOSE`` 给予程序保存
    确认的机会（适用于"按 X 按钮"语义）。如果目标进程没有响应
    WM_CLOSE，窗口不会关闭——这种情况下可改用 ``force_close_window``
    强制 ``TerminateProcess``。
    """
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def activate_window(hwnd: int) -> None:
    """激活窗口到前台."""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)


# --- 绑定 (占位，后续接入乐玩等后端) ---

_bindings: dict[int, BindOptions] = {}


def bind_window(options: BindOptions) -> bool:
    """绑定窗口."""
    _bindings[options.hwnd] = options
    return True


def unbind_window(hwnd: int) -> bool:
    """解绑窗口."""
    return _bindings.pop(hwnd, None) is not None


def is_bound(hwnd: int) -> bool:
    """检查窗口是否已绑定."""
    return hwnd in _bindings


# --- 图色操作 ---


def screenshot(rect: Rect | None = None) -> Image.Image:
    """截图，返回 PIL Image."""
    if rect:
        img = pyautogui.screenshot(region=(rect.left, rect.top, rect.width, rect.height))
    else:
        img = pyautogui.screenshot()
    return img


def _image_search(
    big_img: Image.Image,
    small_img: Image.Image,
    similarity: float = 0.8,
) -> tuple[bool, int, int, float]:
    """核心图片搜索算法."""
    import numpy as np

    big = np.array(big_img)
    small = np.array(small_img)

    bh, bw = big.shape[:2]
    sh, sw = small.shape[:2]

    if sh > bh or sw > bw:
        return False, 0, 0, 0.0

    best_score = 0.0
    best_x, best_y = 0, 0

    # 滑动窗口匹配
    for y in range(0, bh - sh + 1, max(1, sh // 4)):
        for x in range(0, bw - sw + 1, max(1, sw // 4)):
            roi = big[y:y + sh, x:x + sw]
            # 归一化互相关
            score = _match_similarity(roi, small)
            if score > best_score:
                best_score = score
                best_x, best_y = x, y
            if best_score >= similarity:
                return True, best_x, best_y, float(best_score)

    if best_score >= similarity:
        return True, best_x, best_y, float(best_score)
    return False, 0, 0, float(best_score)


def _match_similarity(roi, template) -> float:
    """计算两张图片的相似度."""
    import numpy as np
    roi_f = roi.astype(np.float32)
    tmpl_f = template.astype(np.float32)

    # MSE -> similarity
    diff = roi_f - tmpl_f
    mse = np.mean(diff * diff)
    if mse == 0:
        return 1.0
    max_mse = 255.0 * 255.0
    return 1.0 - mse / max_mse


def find_image(
    image_path: str,
    rect: Rect | None = None,
    similarity: float = 0.9,
) -> FindResult:
    """在屏幕指定区域查找图片."""
    small = Image.open(image_path)
    big = screenshot(rect)

    found, x, y, sim = _image_search(big, small, similarity)

    if rect:
        x += rect.left
        y += rect.top

    return FindResult(found=found, x=x, y=y, similarity=sim)


def find_color(
    color: Color,
    rect: Rect | None = None,
    tolerance: int = 0,
) -> FindResult:
    """查找指定颜色."""
    img = screenshot(rect)
    import numpy as np
    arr = np.array(img)

    target = np.array([color.r, color.g, color.b], dtype=np.int32)

    if tolerance == 0:
        mask = np.all(arr == target, axis=2)
    else:
        diff = np.abs(arr.astype(np.int32) - target)
        mask = np.all(diff <= tolerance, axis=2)

    indices = np.argwhere(mask)
    if len(indices) > 0:
        y, x = indices[0]
        if rect:
            x += rect.left
            y += rect.top
        return FindResult(found=True, x=int(x), y=int(y), similarity=1.0)

    return FindResult()


def get_color(x: int, y: int) -> Color:
    """获取指定坐标颜色."""
    color = pyautogui.pixel(x, y)
    return Color(r=color[0], g=color[1], b=color[2])


def compare_color(x: int, y: int, expected: Color, tolerance: int = 0) -> bool:
    """比较指定坐标颜色."""
    actual = get_color(x, y)
    if tolerance == 0:
        return actual == expected
    return (
        abs(actual.r - expected.r) <= tolerance
        and abs(actual.g - expected.g) <= tolerance
        and abs(actual.b - expected.b) <= tolerance
    )


# --- 键鼠操作 ---


def key_press(key: str) -> None:
    """按下并释放按键."""
    pyautogui.press(key)


def key_down(key: str) -> None:
    """按住按键."""
    pyautogui.keyDown(key)


def key_up(key: str) -> None:
    """释放按键."""
    pyautogui.keyUp(key)


def key_type(text: str, interval: float = 0.0) -> None:
    """输入字符串."""
    pyautogui.typewrite(text, interval=interval)


def hotkey(*keys: str) -> None:
    """组合键."""
    pyautogui.hotkey(*keys)


def mouse_move(x: int, y: int, duration: float = 0.0) -> None:
    """移动鼠标."""
    pyautogui.moveTo(x, y, duration=duration)


def mouse_click(x: int | None = None, y: int | None = None,
                button: str = "left", clicks: int = 1) -> None:
    """鼠标点击."""
    if x is not None and y is not None:
        pyautogui.click(x, y, button=button, clicks=clicks)
    else:
        pyautogui.click(button=button, clicks=clicks)


def mouse_scroll(clicks: int, x: int | None = None, y: int | None = None) -> None:
    """鼠标滚轮."""
    if x is not None and y is not None:
        pyautogui.scroll(clicks, x, y)
    else:
        pyautogui.scroll(clicks)


def mouse_get_pos() -> Point:
    """获取当前鼠标位置."""
    x, y = pyautogui.position()
    return Point(x=x, y=y)


# --- 内存操作 ---

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400


def _open_process(pid: int, access: int) -> int:
    """打开进程."""
    handle = _kernel32.OpenProcess(access, False, pid)
    if not handle:
        raise OSError(f"无法打开进程 {pid}")
    return handle


def _close_process(handle: int) -> None:
    """关闭进程句柄."""
    _kernel32.CloseHandle(handle)


def mem_read(pid: int, address: int, size: int = 4) -> bytes:
    """读取进程内存."""
    handle = _open_process(pid, PROCESS_VM_READ | PROCESS_QUERY_INFORMATION)
    try:
        buf = ctypes.create_string_buffer(size)
        bytes_read = wintypes.SIZE_T(0)
        if not _kernel32.ReadProcessMemory(
            handle,
            wintypes.LPCVOID(address),
            buf,
            size,
            ctypes.byref(bytes_read),
        ):
            raise OSError(f"读取内存失败: 0x{address:X}")
        return buf.raw[:bytes_read.value]
    finally:
        _close_process(handle)


def mem_write(pid: int, address: int, data: bytes) -> bool:
    """写入进程内存."""
    handle = _open_process(pid, PROCESS_VM_WRITE | PROCESS_VM_OPERATION)
    try:
        bytes_written = wintypes.SIZE_T(0)
        result = _kernel32.WriteProcessMemory(
            handle,
            wintypes.LPVOID(address),
            data,
            len(data),
            ctypes.byref(bytes_written),
        )
        return bool(result)
    finally:
        _close_process(handle)


def get_module_base(pid: int, module_name: str = "") -> int:
    """获取模块基址."""
    import psutil  # type: ignore
    try:
        proc = psutil.Process(pid)
        # 等待模块列表加载
        time.sleep(0.1)
        for module in proc.memory_maps():
            if module_name.lower() in module.path.lower():
                return module.path  # type: ignore
        return 0
    except Exception:
        return 0


# --- 系统信息 ---


def get_system_info() -> SystemInfo:
    """获取系统信息."""
    import platform
    import psutil  # type: ignore

    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    os_ver = f"{platform.system()} {platform.release()}"

    return SystemInfo(
        cpu_percent=cpu,
        memory_total_gb=round(mem.total / (1024 ** 3), 1),
        memory_used_gb=round(mem.used / (1024 ** 3), 1),
        screen_width=screen_w,
        screen_height=screen_h,
        os_version=os_ver,
    )


def get_screen_size() -> tuple[int, int]:
    """获取屏幕分辨率."""
    w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return (w, h)


def enum_processes() -> list[ProcessInfo]:
    """枚举运行中的进程."""
    results: list[ProcessInfo] = []
    seen_pids: set[int] = set()

    def _callback(hwnd: int, _param: list) -> bool:
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid not in seen_pids:
                seen_pids.add(pid)
                try:
                    import psutil  # type: ignore
                    name = psutil.Process(pid).name()
                except Exception:
                    name = "unknown"
                results.append(ProcessInfo(
                    pid=pid,
                    name=name,
                    title=win32gui.GetWindowText(hwnd),
                    hwnd=hwnd,
                ))
        return True

    win32gui.EnumWindows(_callback, None)
    return results
