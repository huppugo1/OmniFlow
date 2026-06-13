"""工作流引擎 - 自动化任务编排与执行.

支持:
- JSON/YAML 定义工作流
- 条件判断、循环、延迟等待
- 子流程嵌套
- 暂停/恢复/取消
- 工作流持久化存储
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 工作流存储目录
WORKFLOW_DIR = Path(os.environ.get("OMNIFLOW_WORKFLOW_DIR", Path.home() / ".omniflow" / "workflows"))
WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)


class StepType(str, Enum):
    """步骤类型."""
    TOOL_CALL = "tool_call"              # 调用 MCP Tool
    CONDITION = "condition"              # 条件判断（eval 表达式，引用 context 变量）
    LOOP = "loop"                        # 循环（支持固定次数 / 条件终止 / 周期）
    DELAY = "delay"                      # 延迟等待
    SUBFLOW = "subflow"                  # 子流程
    PARALLEL = "parallel"                # 并行执行
    IF = "if"                            # 条件分支（if/else，两个子流程二选一）
    WAIT_FOR_WINDOW = "wait_for_window"  # 阻塞等到指定窗口出现 / 超时


class WorkflowStatus(str, Enum):
    """工作流状态."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Step:
    """工作流步骤."""
    id: str
    type: StepType
    tool_name: str = ""
    arguments: dict = field(default_factory=dict)
    condition: str = ""              # CONDITION/IF 节点用：Python 表达式
    loop_count: int = 1              # LOOP 节点用：固定循环次数
    loop_interval_seconds: float = 0.0  # LOOP 节点用：每轮间隔（实现"定时器循环"）
    loop_until: str = ""             # LOOP 节点用：表达式满足时停止（替代 loop_count）
    loop_max_iterations: int = 0     # LOOP 节点用：0 = 无限；>0 = 最多 N 轮
    delay_seconds: float = 0.0
    steps: list[Step] = field(default_factory=list)
    on_success: str = ""             # 成功时跳转的 step id
    on_failure: str = ""             # 失败时跳转的 step id
    # 变量系统
    outputs: dict = field(default_factory=dict)  # {var_name: result_field}：从此 step 结果提取变量到 context
    # WAIT_FOR_WINDOW 节点
    wait_class_name: str = ""
    wait_title: str = ""
    wait_timeout_seconds: float = 30.0
    wait_poll_interval: float = 0.5
    # IF 节点：两个子流程
    if_steps: list[Step] = field(default_factory=list)  # condition 为真时执行
    else_steps: list[Step] = field(default_factory=list)  # condition 为假时执行

    @classmethod
    def from_dict(cls, data: dict) -> Step:
        steps_data = data.get("steps", [])
        return cls(
            id=data.get("id", ""),
            type=StepType(data.get("type", "tool_call")),
            tool_name=data.get("tool_name", ""),
            arguments=data.get("arguments", {}),
            condition=data.get("condition", ""),
            loop_count=data.get("loop_count", 1),
            loop_interval_seconds=data.get("loop_interval_seconds", 0.0),
            loop_until=data.get("loop_until", ""),
            loop_max_iterations=data.get("loop_max_iterations", 0),
            delay_seconds=data.get("delay_seconds", 0.0),
            steps=[cls.from_dict(s) for s in steps_data],
            on_success=data.get("on_success", ""),
            on_failure=data.get("on_failure", ""),
            outputs=data.get("outputs", {}),
            wait_class_name=data.get("wait_class_name", ""),
            wait_title=data.get("wait_title", ""),
            wait_timeout_seconds=data.get("wait_timeout_seconds", 30.0),
            wait_poll_interval=data.get("wait_poll_interval", 0.5),
            if_steps=[cls.from_dict(s) for s in data.get("if_steps", [])],
            else_steps=[cls.from_dict(s) for s in data.get("else_steps", [])],
        )


@dataclass
class Workflow:
    """工作流定义."""
    id: str
    name: str
    description: str = ""
    steps: list[Step] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Workflow:
        steps_data = data.get("steps", [])
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            steps=[Step.from_dict(s) for s in steps_data],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def _step_to_dict(s: Step) -> dict:
    """序列化 Step 为 dict（含所有新字段）."""
    d: dict[str, Any] = {
        "id": s.id,
        "type": s.type.value,
        "tool_name": s.tool_name,
        "arguments": s.arguments,
        "condition": s.condition,
        "loop_count": s.loop_count,
        "loop_interval_seconds": s.loop_interval_seconds,
        "loop_until": s.loop_until,
        "loop_max_iterations": s.loop_max_iterations,
        "delay_seconds": s.delay_seconds,
        "on_success": s.on_success,
        "on_failure": s.on_failure,
        "outputs": s.outputs,
    }
    if s.steps:
        d["steps"] = [_step_to_dict(st) for st in s.steps]
    if s.if_steps:
        d["if_steps"] = [_step_to_dict(st) for st in s.if_steps]
    if s.else_steps:
        d["else_steps"] = [_step_to_dict(st) for st in s.else_steps]
    if s.type == StepType.WAIT_FOR_WINDOW:
        d.update({
            "wait_class_name": s.wait_class_name,
            "wait_title": s.wait_title,
            "wait_timeout_seconds": s.wait_timeout_seconds,
            "wait_poll_interval": s.wait_poll_interval,
        })
    return d


# 给 Step 加 to_dict 方法（dataclass 不自动生成）
Step.to_dict = lambda self: _step_to_dict(self)


# ============================================================
# 变量系统 & 表达式求值（workflow 引擎核心）
# ============================================================


def _substitute_args(arguments: Any, context: dict) -> Any:
    """递归地把 arguments 里的 ``{var_name}`` 占位符替换为 context 里的值.

    支持 str / dict / list 嵌套。对非容器类型原样返回。
    """
    if isinstance(arguments, str):
        # 只在含花括号时才 format（性能 + 避免误判）
        if "{" in arguments and "}" in arguments:
            try:
                return arguments.format(**context)
            except (KeyError, IndexError):
                return arguments  # 占位符引用了不存在的变量，原样保留
        return arguments
    if isinstance(arguments, dict):
        return {k: _substitute_args(v, context) for k, v in arguments.items()}
    if isinstance(arguments, list):
        return [_substitute_args(v, context) for v in arguments]
    return arguments


def _extract_outputs(result: Any, outputs_schema: dict) -> dict:
    """从 step 返回值里按 outputs schema 提取变量.

    outputs_schema 格式: ``{"var_name": "result_field"}``。
    也支持点路径: ``{"bag_hwnd": "data.hwnd"}``（浅层 dict.get 链）。
    """
    extracted: dict[str, Any] = {}
    if not outputs_schema or not isinstance(result, dict):
        return extracted
    for var_name, field_path in outputs_schema.items():
        # 支持点路径
        value: Any = result
        for part in str(field_path).split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        extracted[var_name] = value
    return extracted


def _eval_condition(expr: str, context: dict) -> tuple[bool, str | None]:
    """安全地 eval 条件表达式.

    ``__builtins__`` 设为空 dict 防止任意代码执行；表达式只能引用
    context 里的变量、字面量、关键字（and/or/not/if/True/False/None）
    和运算符（比较、布尔、算术）。

    返回 (bool, error_message)。error_message 不为空表示求值失败。
    """
    if not expr:
        return True, None  # 空表达式视为 True（向后兼容）
    try:
        # 只允许 Names / Constants / 简单运算，禁止属性访问 / 调用
        import ast
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if isinstance(node, (ast.Call, ast.Attribute, ast.Import, ast.ImportFrom)):
                return False, f"condition 禁止调用/属性/import: {type(node).__name__}"
        result = eval(compile(tree, "<condition>", "eval"),
                      {"__builtins__": {}}, context)
        return bool(result), None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# 内存中的工作流注册表
_workflows: dict[str, Workflow] = {}
# 运行中的工作流实例
_running: dict[str, tuple[WorkflowStatus, int]] = {}  # workflow_id -> (status, current_step_idx)


def _load_all() -> None:
    """从磁盘加载所有工作流."""
    global _workflows
    _workflows.clear()
    for f in WORKFLOW_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            wf = Workflow.from_dict(data)
            _workflows[wf.id] = wf
        except Exception as e:
            logger.warning(f"加载工作流失败 {f}: {e}")


def _save_one(wf: Workflow) -> None:
    """保存单个工作流到磁盘."""
    path = WORKFLOW_DIR / f"{wf.id}.json"
    path.write_text(json.dumps(wf.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def list_workflows() -> dict:
    """列出所有工作流."""
    _load_all()
    return {
        "workflows": [
            {"id": w.id, "name": w.name, "description": w.description, "step_count": len(w.steps)}
            for w in _workflows.values()
        ],
        "count": len(_workflows),
    }


def save(name: str, steps: list[dict]) -> dict:
    """保存工作流."""
    _load_all()

    # 生成 ID
    import hashlib
    wid = hashlib.md5(name.encode()).hexdigest()[:12]

    now = datetime.now().isoformat()
    step_objects = [Step.from_dict(s) for s in steps]

    if wid in _workflows:
        wf = _workflows[wid]
        wf.name = name
        wf.steps = step_objects
        wf.updated_at = now
    else:
        wf = Workflow(
            id=wid, name=name, steps=step_objects,
            created_at=now, updated_at=now,
        )

    _workflows[wid] = wf
    _save_one(wf)
    return {"id": wid, "name": name, "status": "saved"}


def delete(workflow_id: str) -> dict:
    """删除工作流."""
    _load_all()
    if workflow_id in _workflows:
        del _workflows[workflow_id]
    path = WORKFLOW_DIR / f"{workflow_id}.json"
    if path.exists():
        path.unlink()
    return {"id": workflow_id, "status": "deleted"}


async def run(workflow_id: str, tool_dispatcher=None) -> dict:
    """执行工作流.

    Args:
        workflow_id: 要执行的工作流 ID.
        tool_dispatcher: 可调用对象 (tool_name, arguments) -> dict。
                         None 时 TOOL_CALL 步骤返回 stub（向后兼容）。
                         由 server.py 在 workflow_run 时注入。
    """
    _load_all()
    wf = _workflows.get(workflow_id)
    if not wf:
        return {"error": f"工作流不存在: {workflow_id}"}

    _running[workflow_id] = (WorkflowStatus.RUNNING, 0)
    results: list[dict] = []
    context: dict = {}  # 变量池：跨 step 共享

    try:
        for i, step in enumerate(wf.steps):
            status, _ = _running.get(workflow_id, (WorkflowStatus.CANCELLED, 0))
            if status == WorkflowStatus.CANCELLED:
                return {"status": "cancelled", "results": results, "context": context}

            while status == WorkflowStatus.PAUSED:
                await asyncio.sleep(0.5)
                status, _ = _running.get(workflow_id, (WorkflowStatus.CANCELLED, 0))
                if status == WorkflowStatus.CANCELLED:
                    return {"status": "cancelled", "results": results, "context": context}

            _running[workflow_id] = (WorkflowStatus.RUNNING, i)

            step_result = await _execute_step(step, context, tool_dispatcher)

            # last_result 仅在顶层 step 上更新（子 step 由 _execute_step 内部维护）
            context["last_result"] = step_result

            results.append({"step_id": step.id, "result": step_result})

            if isinstance(step_result, dict) and step_result.get("error"):
                # CONDITION / WAIT_FOR_WINDOW 的失败是"业务失败"，不算 workflow 失败
                if step.type in (StepType.CONDITION, StepType.WAIT_FOR_WINDOW):
                    pass
                else:
                    return {"status": "failed", "results": results,
                            "error_at": step.id, "context": context}

        _running[workflow_id] = (WorkflowStatus.COMPLETED, len(wf.steps))
        return {"status": "completed", "results": results, "context": context}

    except Exception as e:
        logger.exception("工作流执行异常")
        _running[workflow_id] = (WorkflowStatus.FAILED, 0)
        return {"status": "failed", "error": str(e), "results": results, "context": context}


async def _execute_step(step: Step, context: dict, dispatcher) -> dict:
    """执行单个步骤.

    注意：递归子流程（LOOP / SUBFLOW / IF 内的子 step）的 outputs 也会
    写回 context——这样条件循环（loop_until）能读到子 step 的最新值。
    """
    if step.type == StepType.DELAY:
        await asyncio.sleep(step.delay_seconds)
        result: dict = {"status": "ok", "delayed": step.delay_seconds}
    else:
        if step.type == StepType.TOOL_CALL:
            resolved_args = _substitute_args(step.arguments, context)
            if dispatcher is None:
                result = {"status": "ok", "tool": step.tool_name,
                          "args": resolved_args, "stub": True}
            else:
                r = dispatcher(step.tool_name, resolved_args)
                if asyncio.iscoroutine(r):
                    r = await r
                result = r if isinstance(r, dict) else {"status": "ok", "value": r}

        elif step.type == StepType.CONDITION:
            ok, err = _eval_condition(step.condition, context)
            result = {"status": "error", "error": err} if err else {"status": "ok", "condition_result": ok}

        elif step.type == StepType.IF:
            ok, err = _eval_condition(step.condition, context)
            if err:
                result = {"status": "error", "error": err}
            else:
                chosen = step.if_steps if ok else step.else_steps
                results = []
                for sub in chosen:
                    r = await _execute_step(sub, context, dispatcher)
                    results.append(r)
                result = {"status": "ok", "branch": "if" if ok else "else", "results": results}

        elif step.type == StepType.LOOP:
            results = []
            iteration = 0
            result: dict = {"status": "ok", "iterations": 0, "results": []}  # 默认（无子 step）
            while True:
                iteration += 1
                if step.loop_max_iterations and iteration > step.loop_max_iterations:
                    result = {"status": "ok", "iterations": iteration - 1, "results": results}
                    break
                if step.loop_interval_seconds and iteration > 1:
                    await asyncio.sleep(step.loop_interval_seconds)
                for sub in step.steps:
                    r = await _execute_step(sub, context, dispatcher)
                    results.append(r)
                if step.loop_until:
                    ok, err = _eval_condition(step.loop_until, context)
                    if err:
                        result = {"status": "error", "error": err}
                        break
                    if ok:
                        result = {"status": "ok", "iterations": iteration, "results": results}
                        break
                else:
                    if iteration >= step.loop_count:
                        result = {"status": "ok", "iterations": iteration, "results": results}
                        break

        elif step.type == StepType.SUBFLOW:
            results = []
            for sub in step.steps:
                r = await _execute_step(sub, context, dispatcher)
                results.append(r)
            result = {"status": "ok", "subflow_results": results}

        elif step.type == StepType.WAIT_FOR_WINDOW:
            from . import window as window_tool
            loop = asyncio.get_event_loop()
            start = loop.time()
            while True:
                elapsed = loop.time() - start
                if elapsed > step.wait_timeout_seconds:
                    result = {"status": "timeout", "elapsed": elapsed,
                              "wait_class_name": step.wait_class_name,
                              "wait_title": step.wait_title}
                    break
                try:
                    win = window_tool.find(
                        title=step.wait_title or "",
                        class_name=step.wait_class_name or "",
                    )
                    if win and win.get("hwnd"):
                        result = {"status": "ok", "hwnd": win["hwnd"], "elapsed": elapsed}
                        break
                except Exception:
                    pass
                await asyncio.sleep(step.wait_poll_interval)
        else:
            result = {"status": "ok"}

    # 变量提取：子 step 和顶层 step 同样把 outputs 写回 context
    if step.outputs and isinstance(result, dict):
        extracted = _extract_outputs(result, step.outputs)
        context.update(extracted)
    return result


def pause(workflow_id: str) -> dict:
    """暂停工作流."""
    if workflow_id in _running:
        status, idx = _running[workflow_id]
        _running[workflow_id] = (WorkflowStatus.PAUSED, idx)
        return {"status": "paused"}
    return {"error": "工作流未在运行"}


def resume(workflow_id: str) -> dict:
    """恢复工作流."""
    if workflow_id in _running:
        status, idx = _running[workflow_id]
        if status == WorkflowStatus.PAUSED:
            _running[workflow_id] = (WorkflowStatus.RUNNING, idx)
            return {"status": "resumed"}
    return {"error": "工作流未暂停"}
