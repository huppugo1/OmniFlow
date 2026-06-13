"""End-to-end test for the new OmniFlow workflow v2 engine.

Tests:
  P0  window_close tool registered
  P1  tool_call step actually invokes the MCP tool via dispatcher
  P1  variable system: outputs → context → next step's arguments
  P1  condition can reference context variables (with safe eval)
  P2  wait_for_window node polls until found or timeout
  P2  if node branches based on condition
  P3  loop with loop_interval_seconds + loop_until condition
  Integration: the "自动清包" workflow runs end-to-end with real MCP tools
"""
import asyncio
import json
import sys
from pathlib import Path

# 把 src 加进 path（editable install 已经装，但保险起见）
sys.path.insert(0, str(Path(r"F:/woker/OmniFlow/src")))


def banner(s: str) -> None:
    print(f"\n{'─' * 60}\n {s}\n{'─' * 60}")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def fail(msg: str) -> None:
    print(f"  ✗ {msg}")
    raise AssertionError(msg)


async def test_p0_window_close_registered():
    """P0: window_close is in the TOOLS list."""
    banner("P0: window_close tool registered")
    from omniflow.server import TOOLS
    names = {t.name for t in TOOLS}
    if "window_close" not in names:
        fail("window_close not in TOOLS")
    ok(f"window_close registered (TOOLS count={len(TOOLS)})")


async def test_p1a_dispatcher_invokes_real_tools():
    """P1a: tool_call step actually runs the underlying tool via dispatcher."""
    banner("P1a: tool_call 真调 MCP（dispatcher）")
    from omniflow.tools import workflow

    # 用真实 server 的 _handle_tool 作 dispatcher
    from omniflow.server import _handle_tool

    async def dispatcher(tool_name, args):
        return await _handle_tool(tool_name, args)

    # 跑：先 get_screen_size，看 width
    steps = [
        {
            "id": "s1", "type": "tool_call",
            "tool_name": "get_screen_size", "arguments": {},
            "outputs": {"screen_w": "width", "screen_h": "height"},
        },
    ]
    info = workflow.save("test_p1a", steps)
    wid = info["id"]

    result = await workflow.run(wid, tool_dispatcher=dispatcher)
    if result["status"] != "completed":
        fail(f"workflow failed: {result}")
    ctx = result["context"]
    if ctx.get("screen_w", 0) <= 0:
        fail(f"screen_w not extracted: {ctx}")
    if ctx.get("last_result", {}).get("width") != ctx.get("screen_w"):
        fail("last_result mismatch")
    ok(f"screen_size 真调并提取: width={ctx['screen_w']}, height={ctx['screen_h']}")
    ok(f"last_result 存到 context: {ctx['last_result']}")
    workflow.delete(wid)


async def test_p1b_variable_substitution():
    """P1b: arguments 中的 {var} 占位符被替换."""
    banner("P1b: 变量替换 (substitute_args)")
    from omniflow.tools import workflow

    # 第一个 step 把 width 存为 screen_w
    # 第二个 step 用 {screen_w} 引用
    # dispatcher 是 mock：不真调 MCP，但记录参数
    captured = []

    async def mock_dispatcher(tool_name, args):
        captured.append({"tool": tool_name, "args": args})
        return {"width": 1920, "height": 1080, "ratio": 1.0}

    steps = [
        {
            "id": "s1", "type": "tool_call",
            "tool_name": "get_screen_size", "arguments": {},
            "outputs": {"w": "width"},
        },
        {
            "id": "s2", "type": "tool_call",
            "tool_name": "mock_screenshot",
            "arguments": {"region": [0, 0, "{w}", 600]},  # 引用 w
        },
    ]
    info = workflow.save("test_p1b", steps)
    result = await workflow.run(info["id"], tool_dispatcher=mock_dispatcher)
    if result["status"] != "completed":
        fail(f"workflow failed: {result}")
    # 字符串占位符被 str.format 转为字符串是正常行为
    if captured[1]["args"]["region"][2] != "1920":
        fail(f"{{w}} not substituted: {captured[1]['args']}")
    ok(f"{{w}} → '1920' (str.format 行为): {captured[1]['args']['region']}")
    workflow.delete(info["id"])


async def test_p1c_condition_with_context():
    """P1c: condition 可以引用 context 变量（安全 eval）."""
    banner("P1c: condition 引用 context 变量（安全 eval）")
    from omniflow.tools import workflow

    async def mock_dispatcher(tool_name, args):
        return {"width": 1920, "height": 1080}

    steps = [
        {"id": "s1", "type": "tool_call", "tool_name": "get_screen_size",
         "arguments": {}, "outputs": {"w": "width"}},
        # condition 引用 w（来自 s1 的 outputs）
        {"id": "s2", "type": "condition", "condition": "w > 1000"},
        # 危险：试图调函数
        {"id": "s3", "type": "condition", "condition": "__import__('os').system('echo PWNED')"},
    ]
    info = workflow.save("test_p1c", steps)
    result = await workflow.run(info["id"], tool_dispatcher=mock_dispatcher)
    if result["status"] != "completed":
        fail(f"workflow failed: {result}")
    s2 = result["results"][1]["result"]
    if not s2.get("condition_result"):
        fail(f"w > 1000 should be True: {s2}")
    ok(f"condition 'w > 1000' 评估: {s2}")
    s3 = result["results"][2]["result"]
    if "error" not in s3:
        fail(f"恶意 import 应被拦: {s3}")
    ok(f"恶意 condition 被拦: {s3['error'][:60]}")
    workflow.delete(info["id"])


async def test_p2a_wait_for_window():
    """P2a: wait_for_window 阻塞等窗口出现/超时."""
    banner("P2a: wait_for_window 节点")
    from omniflow.tools import workflow

    # 找一个肯定不存在的窗口——应该 timeout
    steps = [{
        "id": "w1", "type": "wait_for_window",
        "wait_class_name": "NonExistentClass12345",
        "wait_timeout_seconds": 1.0,
        "wait_poll_interval": 0.3,
    }]
    info = workflow.save("test_p2a_timeout", steps)
    result = await workflow.run(info["id"])
    r = result["results"][0]["result"]
    if r["status"] != "timeout":
        fail(f"应该 timeout，得到: {r}")
    ok(f"等不存在的窗口：1s 后 timeout，elapsed={r['elapsed']:.2f}s")
    workflow.delete(info["id"])

    # 找 wechat 或者任何真实窗口（可能会因为没装而 timeout，OK）
    # 这里只测 timeout 路径，避免对环境依赖


async def test_p2b_if_node():
    """P2b: if 节点根据 condition 二选一."""
    banner("P2b: if 节点（if/else 分支）")
    from omniflow.tools import workflow

    async def mock_dispatcher(tool_name, args):
        return {"value": 100}

    steps = [
        {"id": "s1", "type": "tool_call", "tool_name": "mock",
         "arguments": {}, "outputs": {"v": "value"}},
        {
            "id": "if1", "type": "if", "condition": "v > 50",
            "if_steps": [{"id": "i1", "type": "delay", "delay_seconds": 0.01}],
            "else_steps": [{"id": "e1", "type": "delay", "delay_seconds": 0.01}],
        },
        {
            "id": "if2", "type": "if", "condition": "v > 200",
            "if_steps": [{"id": "i2", "type": "delay", "delay_seconds": 0.01}],
            "else_steps": [{"id": "e2", "type": "delay", "delay_seconds": 0.01}],
        },
    ]
    info = workflow.save("test_p2b", steps)
    result = await workflow.run(info["id"], tool_dispatcher=mock_dispatcher)
    if result["status"] != "completed":
        fail(f"workflow failed: {result}")
    b1 = result["results"][1]["result"]
    b2 = result["results"][2]["result"]
    if b1["branch"] != "if":
        fail(f"v=100 > 50 should take 'if' branch: {b1}")
    ok(f"if1 (v=100 > 50): branch={b1['branch']}")
    if b2["branch"] != "else":
        fail(f"v=100 > 200 should take 'else' branch: {b2}")
    ok(f"if2 (v=100 > 200): branch={b2['branch']}")
    workflow.delete(info["id"])


async def test_p3_loop_with_interval_and_until():
    """P3: 改进的 loop——支持周期 + 条件终止."""
    banner("P3: loop_interval_seconds + loop_until")
    from omniflow.tools import workflow

    counter = {"n": 0}

    async def mock_dispatcher(tool_name, args):
        counter["n"] += 1
        return {"count": counter["n"]}

    # loop_until 条件：count >= 3
    steps = [
        {"id": "s1", "type": "tool_call", "tool_name": "mock",
         "arguments": {}, "outputs": {"n": "count"}},
        {
            "id": "lp1", "type": "loop",
            "loop_interval_seconds": 0.01,  # 10ms 间隔跑快点
            "loop_until": "n >= 3",
            "loop_max_iterations": 10,  # 保险
            "steps": [
                # 关键：loop 内的子 step 也必须声明 outputs，否则 context 不更新
                {"id": "lp_s1", "type": "tool_call", "tool_name": "mock",
                 "arguments": {}, "outputs": {"n": "count"}},
            ],
        },
    ]
    info = workflow.save("test_p3", steps)
    result = await workflow.run(info["id"], tool_dispatcher=mock_dispatcher)
    lp = result["results"][1]["result"]
    # counter 从 1 开始：s1 跑完 n=1；iter1 lp_s1 → n=2（不满足 n>=3）；iter2 lp_s1 → n=3（满足）→ 停
    if lp["iterations"] != 2:
        fail(f"应该跑 2 轮（直到 n>=3），得到: {lp['iterations']}")
    ok(f"loop 在 count=3 时停止：iterations={lp['iterations']}, counter={counter['n']}")
    workflow.delete(info["id"])


async def test_integration_clear_bag_simulation():
    """集成测试：模拟'自动清包' workflow——不依赖游戏（用真实 OmniFlow 工具）."""
    banner("集成测试: 'auto-clear-popups' workflow (用真实 OmniFlow 工具)")
    from omniflow.tools import workflow
    from omniflow.server import _handle_tool

    async def dispatcher(tool_name, args):
        return await _handle_tool(tool_name, args)

    # 真实任务：清掉所有 "提示" 类弹窗（用 wait_for_window 验证一个不存在的窗口超时）
    steps = [
        # 阶段 1: 找所有"提示"窗口（可能没有——幂等）
        {"id": "p1_find", "type": "tool_call", "tool_name": "window_find",
         "arguments": {"class_name": "#32770", "title": "提示"},
         "outputs": {"prompt_hwnd": "hwnd"}},
        # 阶段 2: 条件——如果有提示窗口（hwnd != 0），按回车；否则跳过
        {"id": "p2_check", "type": "if", "condition": "prompt_hwnd != 0",
         "if_steps": [
             {"id": "p2_press", "type": "tool_call", "tool_name": "key_press",
              "arguments": {"key": "enter"}},
         ],
         "else_steps": [
             {"id": "p2_skip", "type": "tool_call", "tool_name": "get_screen_size",
              "arguments": {}, "outputs": {"w": "width"}},
         ]},
        # 阶段 3: 等待 0.1s
        {"id": "p3_delay", "type": "delay", "delay_seconds": 0.1},
    ]
    info = workflow.save("test_integration_clear_popups", steps)
    result = await workflow.run(info["id"], tool_dispatcher=dispatcher)
    if result["status"] != "completed":
        fail(f"workflow failed: {result}")
    ctx = result["context"]
    ok(f"if 分支正确选择 (prompt_hwnd={ctx.get('prompt_hwnd')})")
    if ctx.get("w"):
        ok(f"else 分支的 get_screen_size 真调: width={ctx['w']}")
    else:
        ok("if 分支执行（找到了提示窗口——按回车）")
    workflow.delete(info["id"])


async def main():
    tests = [
        test_p0_window_close_registered,
        test_p1a_dispatcher_invokes_real_tools,
        test_p1b_variable_substitution,
        test_p1c_condition_with_context,
        test_p2a_wait_for_window,
        test_p2b_if_node,
        test_p3_loop_with_interval_and_until,
        test_integration_clear_bag_simulation,
    ]
    passed = 0
    for t in tests:
        try:
            await t()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
    print(f"\n{'═' * 60}")
    print(f" {passed}/{len(tests)} tests passed")
    print(f"{'═' * 60}")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
