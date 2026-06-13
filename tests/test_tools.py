"""OmniFlow 核心功能测试."""

import pytest

from omniflow.engine.types import (
    BindOptions,
    Color,
    FindResult,
    Point,
    ProcessInfo,
    Rect,
    SystemInfo,
    WindowInfo,
)


# ============================================================
# 类型测试
# ============================================================


class TestPoint:
    def test_create(self):
        p = Point(10, 20)
        assert p.x == 10
        assert p.y == 20

    def test_add(self):
        a = Point(10, 20)
        b = Point(5, 5)
        c = a + b
        assert c.x == 15
        assert c.y == 25

    def test_sub(self):
        a = Point(10, 20)
        b = Point(5, 5)
        c = a - b
        assert c.x == 5
        assert c.y == 15

    def test_to_tuple(self):
        p = Point(10, 20)
        assert p.to_tuple() == (10, 20)


class TestRect:
    def test_create(self):
        r = Rect(0, 0, 100, 200)
        assert r.left == 0
        assert r.top == 0
        assert r.right == 100
        assert r.bottom == 200

    def test_size(self):
        r = Rect(10, 20, 110, 220)
        assert r.width == 100
        assert r.height == 200

    def test_center(self):
        r = Rect(0, 0, 100, 100)
        assert r.center == Point(50, 50)

    def test_to_tuple(self):
        r = Rect(1, 2, 3, 4)
        assert r.to_tuple() == (1, 2, 3, 4)


class TestColor:
    def test_from_hex(self):
        c = Color.from_hex("FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_from_hex_with_hash(self):
        c = Color.from_hex("#00FF00")
        assert c.r == 0
        assert c.g == 255
        assert c.b == 0

    def test_from_int(self):
        c = Color.from_int(0x0000FF)
        assert c.r == 0
        assert c.g == 0
        assert c.b == 255

    def test_to_hex(self):
        c = Color(255, 128, 64)
        assert c.to_hex() == "FF8040"

    def test_to_int(self):
        c = Color(0xFF, 0x80, 0x40)
        assert c.to_int() == 0xFF8040

    def test_to_tuple(self):
        c = Color(10, 20, 30)
        assert c.to_tuple() == (10, 20, 30)


class TestFindResult:
    def test_default(self):
        r = FindResult()
        assert r.found is False
        assert r.x == 0
        assert r.y == 0
        assert r.similarity == 0.0

    def test_found(self):
        r = FindResult(found=True, x=100, y=200, similarity=0.95, name="test")
        assert r.found is True
        assert r.x == 100
        assert r.y == 200
        assert r.similarity == 0.95
        assert r.name == "test"


class TestProcessInfo:
    def test_create(self):
        p = ProcessInfo(pid=1234, name="test.exe", title="Test", hwnd=5678)
        assert p.pid == 1234
        assert p.name == "test.exe"

    def test_hash(self):
        p1 = ProcessInfo(pid=1)
        p2 = ProcessInfo(pid=1)
        p3 = ProcessInfo(pid=2)
        assert hash(p1) == hash(p2)
        assert hash(p1) != hash(p3)


class TestSystemInfo:
    def test_default(self):
        s = SystemInfo()
        assert s.cpu_percent == 0.0
        assert s.screen_width == 0

    def test_full(self):
        s = SystemInfo(
            cpu_percent=50.5,
            memory_total_gb=16.0,
            memory_used_gb=8.0,
            screen_width=1920,
            screen_height=1080,
            os_version="Windows 10",
        )
        assert s.cpu_percent == 50.5
        assert s.screen_width == 1920


class TestBindOptions:
    def test_default(self):
        o = BindOptions()
        assert o.display_mode == "gdi"
        assert o.mouse_mode == "normal"

    def test_custom(self):
        o = BindOptions(
            hwnd=123,
            display_mode="dx",
            mouse_mode="windows",
            keyboard_mode="windows",
        )
        assert o.hwnd == 123
        assert o.display_mode == "dx"
        assert o.mouse_mode == "windows"


# ============================================================
# 工作流测试
# ============================================================


class TestWorkflowSaveList:
    def test_save_and_list(self):
        from omniflow.tools.workflow import save, list_workflows, delete

        steps = [
            {"id": "s1", "type": "tool_call", "tool_name": "key_press", "arguments": {"key": "enter"}},
            {"id": "s2", "type": "delay", "delay_seconds": 1.0},
            {"id": "s3", "type": "tool_call", "tool_name": "mouse_click", "arguments": {"button": "left"}},
        ]
        result = save("test_workflow", steps)
        assert "id" in result

        lst = list_workflows()
        assert lst["count"] >= 1

        delete(result["id"])
        lst2 = list_workflows()
        # 确认已删除
        ids = [w["id"] for w in lst2["workflows"]]
        assert result["id"] not in ids


class TestWorkflowRun:
    @pytest.mark.asyncio
    async def test_run_simple(self):
        from omniflow.tools.workflow import save, run, delete

        steps = [
            {"id": "s1", "type": "delay", "delay_seconds": 0.1},
            {"id": "s2", "type": "delay", "delay_seconds": 0.1},
        ]
        result = save("test_run", steps)
        exec_result = await run(result["id"])
        assert exec_result["status"] == "completed"
        assert len(exec_result["results"]) == 2
        delete(result["id"])

    @pytest.mark.asyncio
    async def test_run_condition(self):
        from omniflow.tools.workflow import save, run, delete

        steps = [
            {"id": "s1", "type": "condition", "condition": "1 + 1 == 2"},
        ]
        result = save("test_cond", steps)
        exec_result = await run(result["id"])
        assert exec_result["status"] == "completed"
        assert exec_result["results"][0]["result"]["condition_result"] is True
        delete(result["id"])


# ============================================================
# 插件测试
# ============================================================


class TestPlugin:
    def test_list(self):
        from omniflow.tools.plugin import list_plugins

        result = list_plugins()
        assert "plugins" in result
        assert "count" in result
        assert isinstance(result["plugins"], list)

    def test_uninstall_nonexistent(self):
        from omniflow.tools.plugin import uninstall

        result = uninstall("nonexistent_plugin")
        assert "error" in result
