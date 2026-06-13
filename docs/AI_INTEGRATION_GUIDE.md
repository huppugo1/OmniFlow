# OmniFlow AI 集成指南

> 让 AI 客户端（Claude Desktop / Cursor / Windsurf / Hermes / Claude Code）正确使用 OmniFlow 的实践指南。

---

## 1. MCP 客户端配置

OmniFlow 通过 **stdio 协议**和 MCP 客户端通信。配置本质上是"告诉客户端怎么启动 OmniFlow server"。

### 1.1 通用配置模板

```json
{
  "mcpServers": {
    "omniflow": {
      "command": "<venv-python>",
      "args": ["-m", "omniflow"],
      "cwd": "<本地 OmniFlow 仓库路径>"
    }
  }
}
```

| 字段 | 说明 |
|---|---|
| `command` | venv 里的 `python.exe` 绝对路径（**不**用系统 `python`——会找不到 omniflow 包） |
| `args` | `["-m", "omniflow"]`（以模块方式运行，**必须**先 `pip install -e .`） |
| `cwd` | OmniFlow 仓库根目录（部分客户端支持，如 Hermes） |

### 1.2 各客户端的配置文件位置

| 客户端 | 配置文件位置 |
|---|---|
| **Hermes** | `~/.hermes/config.yaml` 的 `mcp.servers.omniflow` 段（用 `hermes mcp add omniflow ...` 命令管理） |
| **Claude Desktop** | Windows: `%APPDATA%\Claude\claude_desktop_config.json`<br>macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Cursor** | Settings → MCP → Add new global MCP server |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **VS Code + Continue** | `.continue/config.json` 的 `experimental.mcpServers` 段 |
| **Cline** | VS Code 设置 → Cline → MCP Servers |

### 1.3 Hermes 推荐配置

```bash
# 用 hermes mcp add 注册（最稳）
hermes mcp add omniflow \
  --command "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe" \
  --args "-m" "omniflow"
```

或**手动编辑** `~/.hermes/config.yaml`：
```yaml
mcp:
  servers:
    omniflow:
      command: "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe"
      args: ["-m", "omniflow"]
```

### 1.4 验证配置

启动客户端后，**用 `mcp__omniflow__get_screen_size()` 测试连接**——能返回 `{"width": 1920, "height": 1080}` 就 OK。

---

## 2. Prompt 最佳实践

### 2.1 引导 AI 正确选 Tool

**❌ 差的 Prompt**：
> "帮我操作电脑"

AI 不知道从哪个 Tool 开始。

**✅ 好的 Prompt**：
> "在屏幕右下角（坐标 1800, 1000）点击一个按钮，按钮是蓝色圆角矩形，背景是白色"

AI 知道用 `screenshot` 看屏幕 + `find_image` 找按钮 + `mouse_click` 点击。

### 2.2 让 AI 主动看 `recovery_suggestions`

**❌ 差的 Prompt**：
> "找'确定'按钮"

如果按钮没找到，AI 会**反复重试**同一个 Tool，浪费时间。

**✅ 好的 Prompt**：
> "找'确定'按钮。如果找不到，先按 `recovery_suggestions` 调整 similarity 阈值；如果还找不到，截图给我看"

AI 会**主动**看 `recovery_suggestions` 字段，按建议调整策略。

### 2.3 明确边界

**❌ 危险的 Prompt**：
> "把游戏血量改 0"

可能让 AI 去做**内存修改**（违法风险）。

**✅ 安全的 Prompt**：
> "用截图 + find_image 找血条，当血条 < 30% 时自动按键喝药。**不要**用 `mem_*` 工具"

明确告诉 AI 走 GUI 自动化路径，**不**走内存修改。

### 2.4 让 AI 复用已注册的 Tool 而不是发明新的

如果用户 prompt 模糊，AI 可能会**建议**用户安装新工具。**引导 AI 优先用现有 Tool**：

> "用 OmniFlow 现有的工具完成这个任务。**不要**建议安装新软件"

### 2.5 让 AI 用组合 Tool 而非原子 Tool

**❌ 差的 Prompt**：
> "找'确定'按钮，然后移动鼠标点击"

AI 会用 `find_image` + `mouse_move` + `mouse_click` 三步。

**✅ 好的 Prompt**：
> "点击'确定'按钮"

AI 看到 `click_image` 组合 Tool 会优先用（一步完成）。

---

## 3. 典型任务流程（AI 应该如何编排 Tools）

### 3.1 任务：自动点击某个按钮

```
✅ 推荐流程：
1. click_image(image_path="templates/btn.png", similarity=0.9)
2. 如果 clicked=False, 调 wait_and_click 重试（更长 timeout）
3. 如果还失败，按 recovery_suggestions 调整 similarity 或截图给用户看

❌ 不要这样做：
1. find_image → 拿坐标 → mouse_move → mouse_click（4 步，不如 click_image 1 步）
```

### 3.2 任务：等某个界面出现

```
✅ 推荐：
1. wait_and_click(image_path="templates/loaded.png", timeout=30, poll_interval=1)
   (image 出现就点；timeout 后报"界面未出现")

或用 workflow 节点（更稳）：
1. wait_for_window(class_name="MainForm", timeout=30)
```

### 3.3 任务：登录桌面 app

```
✅ 推荐：
1. window_find(title="Login Window") 拿 hwnd
2. window_activate(hwnd=...) 切到前台
3. key_type(text="username", interval=0.05)  # 中间 IME
4. key_press(key="tab")
5. key_type(text="password", interval=0.05)
6. key_press(key="enter")
7. 验证：等几秒 → window_find(title="Main") 看是否进入主界面
```

### 3.4 任务：游戏自动打怪循环

```
✅ 推荐（workflow 引擎）：
1. 用 workflow_save 存一个工作流：
   - 找怪图标（find_image）
   - 找到就点击（mouse_click）
   - 等 1s
   - 循环
2. 用 hermes cron 调度：每 60s 跑一次

或单 session 内：
1. bind_window(display_mode="dx", mouse_mode="windows", keyboard_mode="windows")
2. 循环（手动 loop_until "用户取消"）:
   - find_image(image_path="monster.png")
   - 找到就 mouse_click
   - 找"拾取"按钮 → click
   - 找"经验条满"按钮 → click
   - sleep(1)
```

### 3.5 任务：清空所有弹窗（保持工作流继续）

```
✅ 推荐（workflow 引擎）：
1. 找"提示"窗口 → 找到就 key_press(enter)
2. 找"错误"窗口 → 找到就 window_close
3. 找已开的子窗口 → 找到就 close
4. 这三步**幂等**（找不到就跳过），可作为 workflow 的开头段

或作为"清理 subflow"复用：
- workflow 内嵌 subflow 引用
- 每个任务开始前先跑清理
```

### 3.6 任务：从截图中提取文字

```
✅ 推荐：
1. screenshot(区域) 截屏
2. ocr(区域) 识别文字
3. 让 LLM 解析文字内容（regex / LLM）

⚠️ 注意：omni ocr 不返回每个词的坐标。要坐标用 find_image 找文字截图模板
```

---

## 4. 调试技巧

### 4.1 Tool 调用失败时

1. **看 `error_code`** —— 标识问题类别（E1001 = 窗口找不到，E2001 = 图片找不到，等等）
2. **看 `recovery_suggestions`** —— 列出"下一步该做什么"的具体建议
3. **如果建议不明确**，**调 `screenshot()` 看现状**——> 90% 的"找不到窗口/按钮"问题用截图一眼看清

### 4.2 任务卡住时

**问 AI 自己**：
> "你的最后 5 个 Tool 调用是什么？返回的 `error_code` 是什么？"

让 AI 把调用历史汇报出来，**自己**识别问题。

**启用 verbose 日志**：
```bash
hermes chat --verbose
# 或在 server.py 启动时设置：
LOG_LEVEL=DEBUG
```

### 4.3 验证 workflow 是否合理

用 `validate_workflow` 工具（P3 计划，未实现；目前用 Python 解析 JSON 后 dry-run）：

```python
# 解析 JSON 后看：
# 1. 所有 step id 唯一？
# 2. outputs schema 里的字段名跟下游 {var} 引用一致？
# 3. condition 表达式合法？
```

### 4.4 测试工具

`tests/test_workflow_v2.py` 包含 8 个 workflow 引擎单元测试 + 集成测试。**改 workflow 引擎前必跑**。

`tests/test_p0_wrap.py` 验证 `_wrap_result` 包装逻辑（统一返回格式）。

`tests/test_p1_composite.py` 验证 3 个组合 Tool 的错误路径。

---

## 5. 性能与最佳实践

### 5.1 高频调用优化

- `screenshot` 是同步阻塞（50-200ms），**别**在 60fps 实时循环里用
- 高频截图（>5/秒）用 `mss` 库替代
- 模板图加载有缓存——`find_image` 多次用同一图比不同图快

### 5.2 长任务调度

**单 session 内**：适合 < 5 分钟的快速任务。

**跨 session**（`hermes cron`）：适合定时任务（每小时清一次弹窗、每 10 分钟保存一次数据）。

**workflow 引擎**：适合"清理 + 主任务"这种复合流程，存为 workflow 复用。

### 5.3 安全护栏

1. **写操作前先确认**——`mem_write` / `key_type` / `mouse_click` 都是**有副作用**的
2. **后台操作前先 `bind_window`**——避免键鼠被其他窗口抢
3. **截图前先 `mouse_move(0, 0)`** 把光标藏到角落——避免截图带光标
4. **错误信息有 `recovery_suggestions`**——遇到错误**先看这里**，**别**瞎试

---

## 6. 文档交叉引用

- 完整 43 tool 描述 + 使用场景 + 错误码：`docs/MCP_TOOLS_REFERENCE.md`
- 按场景组织的使用示例：`OmniFlow 使用示例.md`
- v2 引擎工作流示例：`examples/workflows/infinite_fish_auto_sell.json`
- 错误码完整列表：`src/omniflow/tools/errors.py`
- 技能（AI 自身学习用）：`~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/SKILL.md`

---

## 7. 常见问题（FAQ）

**Q: AI 调了 Tool 但一直失败，怎么办？**
A: 让 AI 截图给你看现状。90% 的"找不到 X"问题截图能直接看出原因（窗口隐藏、按钮被遮挡、坐标错位等）。

**Q: Tool 找不到合适的工作流引擎节点怎么办？**
A: workflow v2 引擎支持的节点：tool_call / condition / if / loop / delay / subflow / wait_for_window。**不**支持 `wait_for_window_close`（等窗口消失）等罕见节点。绕路：用 `loop_until` + `window_get_info` 轮询窗口存在性。

**Q: 怎么让 AI 学会 OmniFlow 的使用模式？**
A: 加载 `~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/` 下的 skill。该 skill 已包含 6 大场景、5 个模式、失败恢复、设计原则。

**Q: AI 误用了 `mem_write`，怎么办？**
A: 立即撤销！`mem_write` 写错地址可能让目标进程崩溃。**预防** > **治疗**：永远不要让 AI 自动用 `mem_write`——明确要求"用截图 + find_image，不修改内存"。

**Q: 工作流引擎运行慢怎么办？**
A: workflow v2 引擎是单线程顺序执行（v1 也类似），没有并行化。如果一个 workflow 有 100 个 step，每个 100ms，共 10s。优化：合并 step、减少 `wait_for_window` 轮询间隔、用 `hermes cron` 拆分大任务为多个小任务。

**Q: 不同 LLM 的 OmniFlow 使用习惯？**
A:
- **Claude Opus / Sonnet**：最擅长组合 Tool，对错误码 + 恢复建议敏感度高
- **GPT-4 / GPT-4o**：跟 Claude 类似
- **本地小模型（如 llama3 7B）**：可能在多步编排上失败，**建议**用 `click_image` 这种组合 Tool 减少编排复杂度
