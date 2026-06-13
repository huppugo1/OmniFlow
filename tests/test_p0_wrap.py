"""验证 OmniFlow 统一返回格式 + 错误码体系（OPTIMIZATION_PLAN P0.1 + P0.2）."""
import asyncio
import json
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


async def test_wrap_success():
    """P0.1: 成功返回的包装格式."""
    banner("P0.1 统一返回格式: 成功")
    from omniflow.server import _wrap_result

    # 典型成功返回
    wrapped = _wrap_result({"status": "ok", "hwnd": 1234})
    assert wrapped["success"] is True, wrapped
    assert wrapped["data"] == {"status": "ok", "hwnd": 1234}, wrapped
    assert wrapped["message"] == "ok", wrapped
    assert wrapped["error_code"] is None, wrapped
    ok(f"成功: success=True, data 保留原 dict, message={wrapped['message']!r}")

    # 非 dict 返回
    wrapped2 = _wrap_result("just a string")
    assert wrapped2["success"] is True
    assert wrapped2["data"] == "just a string"
    ok("非 dict 返回: 也正确包装")


async def test_wrap_error_with_known_code():
    """P0.1 + P0.2: 失败返回带 error_code → 自动注入 recovery_suggestions."""
    banner("P0.2 错误码统一: 失败 + 自动注入恢复建议")
    from omniflow.server import _wrap_result
    from omniflow.tools.errors import ErrorCode, get_recovery_suggestions

    # 工具主动用 ErrorCode
    result = {
        "error": "未找到 'QQPCMgr.exe' 进程",
        "error_code": ErrorCode.PROCESS_NOT_FOUND,
    }
    wrapped = _wrap_result(result)
    assert wrapped["success"] is False
    assert wrapped["error_code"] == "E5003"
    assert "PROCESS_NOT_FOUND" in ErrorCode.PROCESS_NOT_FOUND or wrapped["error_code"] == ErrorCode.PROCESS_NOT_FOUND
    assert len(wrapped["recovery_suggestions"]) > 0
    assert "tasklist" in str(wrapped["recovery_suggestions"])
    ok(f"PROCESS_NOT_FOUND: error_code={wrapped['error_code']}")
    ok(f"recovery_suggestions: {wrapped['recovery_suggestions']}")

    # 工具不传 error_code（向后兼容）
    wrapped2 = _wrap_result({"error": "some error"})
    assert wrapped2["error_code"] == ErrorCode.UNKNOWN
    assert len(wrapped2["recovery_suggestions"]) > 0  # UNKNOWN 也有建议
    ok(f"未传 error_code: 默认 E0000 + UNKNOWN 建议")

    # status=='error' 形式
    wrapped3 = _wrap_result({"status": "error", "error": "x"})
    assert wrapped3["success"] is False
    ok("status=='error' 形式: 正确识别为失败")


async def test_all_error_codes_have_suggestions():
    """P0.2: 验证 ErrorCode 全集都有 recovery_suggestions（除了 UNKNOWN 等）."""
    banner("P0.2 错误码完整性检查")
    from omniflow.tools.errors import ErrorCode, RECOVERY_SUGGESTIONS, get_recovery_suggestions

    # 遍历所有 ErrorCode 字段
    code_attrs = [v for k, v in vars(ErrorCode).items() if not k.startswith("_") and isinstance(v, str)]
    missing = [c for c in code_attrs if c not in RECOVERY_SUGGESTIONS]
    if missing:
        fail(f"未在 RECOVERY_SUGGESTIONS 注册的 codes: {missing}")
    ok(f"全部 {len(code_attrs)} 个错误码都有恢复建议")

    # 抽样验证
    for code in [ErrorCode.WINDOW_NOT_FOUND, ErrorCode.IMAGE_NOT_FOUND,
                 ErrorCode.MEM_READ_FAILED, ErrorCode.PROGRAM_LAUNCH_FAILED]:
        sug = get_recovery_suggestions(code)
        assert len(sug) >= 2, f"{code} 建议过少: {sug}"
        ok(f"{code}: {len(sug)} 条建议")

    # 未知错误码也要兜底
    sug = get_recovery_suggestions("E9999")
    assert isinstance(sug, list) and len(sug) >= 1
    ok("未知错误码: 兜底返回通用建议")


async def test_end_to_end_real_tool():
    """端到端: 真实调一个 tool，验证包装生效."""
    banner("端到端: 真实 tool 调用 → 包装生效")
    from omniflow.server import _handle_tool

    # 调一个简单 tool
    r = await _handle_tool("get_screen_size", {})
    print(f"  raw: {r}")
    # 在 call_tool 之外直接调 _handle_tool 不会包装
    assert r == {"width": 1920, "height": 1080} or "width" in r, f"unexpected: {r}"
    ok(f"raw _handle_tool 返回未包装: {r}")

    # 但通过 _wrap_result 包装后
    from omniflow.server import _wrap_result
    wrapped = _wrap_result(r)
    assert wrapped["success"] is True
    assert wrapped["data"] == r
    assert wrapped["error_code"] is None
    ok(f"_wrap_result 包装: {list(wrapped.keys())}")


async def main():
    tests = [
        test_wrap_success,
        test_wrap_error_with_known_code,
        test_all_error_codes_have_suggestions,
        test_end_to_end_real_tool,
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
