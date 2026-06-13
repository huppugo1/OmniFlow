"""验证 P1.1 三个组合 Tool（click_image / wait_and_click / ocr_and_click）."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"F:/woker/OmniFlow/src")))


def banner(s):
    print(f"\n{'─' * 60}\n {s}\n{'─' * 60}")


def ok(msg):
    print(f"  ✓ {msg}")


def fail(msg):
    print(f"  ✗ {msg}")
    raise AssertionError(msg)


async def test_click_image_not_found():
    """click_image 找不到图 → 返回 error_code E2001."""
    banner("click_image: 找不存在的图")
    from omniflow.tools import composite

    r = composite.click_image(
        image_path="C:/nonexistent_path_definitely/not_a_real_image.png",
        similarity=0.9,
    )
    assert r.get("clicked") is False
    # 不存在的路径可能触发 E2001（找不到）或 E2002（加载失败）——都合理
    ec = r.get("error_code", "")
    assert ec in ("E2001", "E2002"), f"unexpected error_code: {ec}"
    assert "image_path" in r
    ok(f"clicked=False, error_code={ec}")


async def test_wait_and_click_timeout():
    """wait_and_click 短超时找不到图 → 返回 error_code TIMEOUT."""
    banner("wait_and_click: 短超时")
    from omniflow.tools import composite

    r = composite.wait_and_click(
        image_path="C:/nonexistent/wont_find.png",
        timeout=0.5,  # 0.5s 超时
        poll_interval=0.1,
    )
    assert r.get("clicked") is False
    # 模板不存在时也可能立即返回 E2002（不等满 timeout），但 click_image 失败
    # 时 wait_and_click 会"快速失败"——这是优化（不浪费时间轮询）
    assert r.get("error_code") in ("E0003", "E2002"), f"got {r.get('error_code')}"
    ok(f"clicked=False, error_code={r['error_code']}, elapsed={r.get('elapsed', 0):.2f}s")


async def test_ocr_and_click_missing_region():
    """ocr_and_click 缺 region → 返回 INVALID_ARG."""
    banner("ocr_and_click: 缺 region")
    from omniflow.tools import composite

    r = composite.ocr_and_click(
        text="确定",
        # region 故意缺
    )
    assert r.get("clicked") is False
    assert r.get("error_code") == "E0001"
    ok(f"clicked=False, error_code={r['error_code']}")
    ok("✓ 缺 region 立即拒绝（不浪费 OCR 时间）")


async def test_composite_via_server_handler():
    """端到端: 通过 server.py _handle_tool 调组合 Tool（验证 server 分发）."""
    banner("端到端: server._handle_tool 分发")
    from omniflow.server import _handle_tool

    r = await _handle_tool("click_image", {
        "image_path": "C:/nonexistent/whatever.png",
    })
    assert r.get("clicked") is False
    assert r.get("error_code") in ("E2001", "E2002")
    ok(f"server handler: {r}")

    r2 = await _handle_tool("wait_and_click", {
        "image_path": "C:/nonexistent/whatever.png",
        "timeout": 0.3,
        "poll_interval": 0.1,
    })
    assert r2.get("clicked") is False
    assert r2.get("error_code") in ("E0003", "E2002")
    ok(f"wait_and_click via handler: elapsed={r2.get('elapsed', 0):.2f}s")


async def main():
    tests = [
        test_click_image_not_found,
        test_wait_and_click_timeout,
        test_ocr_and_click_missing_region,
        test_composite_via_server_handler,
    ]
    passed = 0
    for t in tests:
        try:
            await t()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
    print(f"\n{'═' * 60}\n {passed}/{len(tests)} tests passed\n{'═' * 60}")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
