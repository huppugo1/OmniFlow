# OmniFlow AI Integration Guide

> Practical guide for AI clients (Claude Desktop / Cursor / Windsurf / Hermes / Claude Code) to correctly use OmniFlow.

---

## 1. MCP Client Configuration

OmniFlow communicates with MCP clients via the **stdio protocol**. Configuration essentially "tells the client how to start the OmniFlow server".

### 1.1 Universal Configuration Template

```json
{
  "mcpServers": {
    "omniflow": {
      "command": "<venv-python>",
      "args": ["-m", "omniflow"],
      "cwd": "<local OmniFlow repository path>"
    }
  }
}
```

| Field | Description |
|---|---|
| `command` | Absolute path to `python.exe` in venv (**do not** use system `python` — it won't find the omniflow package) |
| `args` | `["-m", "omniflow"]` (run as module, **must** run `pip install -e .` first) |
| `cwd` | OmniFlow repository root directory (some clients support it, e.g., Hermes) |

### 1.2 Configuration File Locations by Client

| Client | Configuration File Location |
|---|---|
| **Hermes** | `~/.hermes/config.yaml` under `mcp.servers.omniflow` section (managed via `hermes mcp add omniflow ...` command) |
| **Claude Desktop** | Windows: `%APPDATA%\Claude\claude_desktop_config.json`<br>macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Cursor** | Settings → MCP → Add new global MCP server |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **VS Code + Continue** | `.continue/config.json` under `experimental.mcpServers` section |
| **Cline** | VS Code Settings → Cline → MCP Servers |

### 1.3 Hermes Recommended Configuration

```bash
# Register with hermes mcp add (most stable)
hermes mcp add omniflow \
  --command "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe" \
  --args "-m" "omniflow"
```

Or **manually edit** `~/.hermes/config.yaml`:
```yaml
mcp:
  servers:
    omniflow:
      command: "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe"
      args: ["-m", "omniflow"]
```

### 1.4 Verify Configuration

After starting the client, **test connection with `mcp__omniflow__get_screen_size()`** — returning `{"width": 1920, "height": 1080}` means it's working.

---

## 2. Prompt Best Practices

### 2.1 Guide AI to Choose the Right Tool

**❌ Bad Prompt**:
> "Help me operate the computer"

AI doesn't know which Tool to start with.

**✅ Good Prompt**:
> "Click a button at the bottom-right of the screen (coordinates 1800, 1000). The button is a blue rounded rectangle with a white background"

AI knows to use `screenshot` to view screen + `find_image` to find the button + `mouse_click` to click.

### 2.2 Let AI Actively Check `recovery_suggestions`

**❌ Bad Prompt**:
> "Find the 'OK' button"

If the button is not found, AI will **repeatedly retry** the same Tool, wasting time.

**✅ Good Prompt**:
> "Find the 'OK' button. If not found, first adjust the similarity threshold according to `recovery_suggestions`; if still not found, take a screenshot and show me"

AI will **actively** look at the `recovery_suggestions` field and adjust strategy according to suggestions.

### 2.3 Define Clear Boundaries

**❌ Dangerous Prompt**:
> "Change the game HP to 0"

May cause AI to perform **memory modification** (legal risk).

**✅ Safe Prompt**:
> "Use screenshot + find_image to find the HP bar, automatically press key to drink potion when HP < 30%. **Do not** use `mem_*` tools"

Clearly tell AI to use the GUI automation path, **not** memory modification.

### 2.4 Let AI Reuse Registered Tools Instead of Inventing New Ones

If the user prompt is vague, AI may **suggest** installing new tools. **Guide AI to prioritize existing Tools**:

> "Use OmniFlow's existing tools to complete this task. **Do not** suggest installing new software"

### 2.5 Let AI Use Composite Tools Instead of Atomic Tools

**❌ Bad Prompt**:
> "Find the 'OK' button, then move the mouse and click"

AI will use `find_image` + `mouse_move` + `mouse_click` in three steps.

**✅ Good Prompt**:
> "Click the 'OK' button"

AI will see the `click_image` composite Tool and prioritize it (one step completion).

---

## 3. Typical Task Flows (How AI Should Orchestrate Tools)

### 3.1 Task: Automatically Click a Button

```
✅ Recommended Flow:
1. click_image(image_path="templates/btn.png", similarity=0.9)
2. If clicked=False, call wait_and_click to retry (longer timeout)
3. If still fails, adjust similarity according to recovery_suggestions or take a screenshot to show the user

❌ Don't do this:
1. find_image → get coordinates → mouse_move → mouse_click (4 steps, not as good as click_image 1 step)
```

### 3.2 Task: Wait for an Interface to Appear

```
✅ Recommended:
1. wait_and_click(image_path="templates/loaded.png", timeout=30, poll_interval=1)
   (click when image appears; report "interface did not appear" after timeout)

Or use workflow node (more stable):
1. wait_for_window(class_name="MainForm", timeout=30)
```

### 3.3 Task: Log in to Desktop App

```
✅ Recommended:
1. window_find(title="Login Window") to get hwnd
2. window_activate(hwnd=...) to bring to foreground
3. key_type(text="username", interval=0.05)  # for IME
4. key_press(key="tab")
5. key_type(text="password", interval=0.05)
6. key_press(key="enter")
7. Verify: wait a few seconds → window_find(title="Main") to check if entered main interface
```

### 3.4 Task: Game Auto-Combat Loop

```
✅ Recommended (workflow engine):
1. Use workflow_save to save a workflow:
   - Find monster icon (find_image)
   - Click if found (mouse_click)
   - Wait 1s
   - Loop
2. Use hermes cron scheduling: run every 60s

Or within single session:
1. bind_window(display_mode="dx", mouse_mode="windows", keyboard_mode="windows")
2. Loop (manual loop_until "user cancels"):
   - find_image(image_path="monster.png")
   - Click if found
   - Find "pick up" button → click
   - Find "exp bar full" button → click
   - sleep(1)
```

### 3.5 Task: Clear All Pop-ups (Keep Workflow Running)

```
✅ Recommended (workflow engine):
1. Find "prompt" window → press key_press(enter) if found
2. Find "error" window → window_close if found
3. Find opened child windows → close if found
4. These three steps are **idempotent** (skip if not found), can be used as the opening segment of a workflow

Or as a reusable "cleanup subflow":
- Workflow with nested subflow reference
- Run cleanup before each task starts
```

### 3.6 Task: Extract Text from Screenshot

```
✅ Recommended:
1. screenshot(area) to capture
2. ocr(area) to recognize text
3. Let LLM parse text content (regex / LLM)

⚠️ Note: omni ocr does not return coordinates for each word. Use find_image to find text screenshot templates for coordinates.
```

---

## 4. Debugging Tips

### 4.1 When Tool Call Fails

1. **Check `error_code`** — identifies problem category (E1001 = window not found, E2001 = image not found, etc.)
2. **Check `recovery_suggestions`** — lists specific suggestions for "what to do next"
3. **If suggestions are unclear**, **call `screenshot()` to see current state** —> 90% of "window/button not found" issues are obvious from a screenshot

### 4.2 When Task is Stuck

**Ask AI itself**:
> "What are your last 5 Tool calls? What `error_code` did they return?"

Let AI report its call history and **self-identify** the problem.

**Enable verbose logging**:
```bash
hermes chat --verbose
# Or when starting server.py:
LOG_LEVEL=DEBUG
```

### 4.3 Validate Whether Workflow is Reasonable

Use `validate_workflow` tool (P3 plan, not yet implemented; currently parse JSON with Python then dry-run):

```python
# After parsing JSON, check:
# 1. Are all step ids unique?
# 2. Do field names in outputs schema match downstream {var} references?
# 3. Are condition expressions valid?
```

### 4.4 Testing Tools

`tests/test_workflow_v2.py` contains 8 workflow engine unit tests + integration tests. **Must run before modifying workflow engine**.

`tests/test_p0_wrap.py` verifies `_wrap_result` wrapping logic (unified return format).

`tests/test_p1_composite.py` verifies error paths of 3 composite Tools.

---

## 5. Performance and Best Practices

### 5.1 High-frequency Call Optimization

- `screenshot` is synchronous blocking (50-200ms), **do not** use in 60fps real-time loops
- For high-frequency screenshots (>5/sec), use `mss` library instead
- Template image loading is cached — `find_image` using the same image multiple times is faster than different images

### 5.2 Long Task Scheduling

**Single session**: Suitable for quick tasks < 5 minutes.

**Cross session** (`hermes cron`): Suitable for scheduled tasks (clear pop-ups every hour, save data every 10 minutes).

**Workflow engine**: Suitable for composite flows like "cleanup + main task", save as workflow for reuse.

### 5.3 Safety Guardrails

1. **Confirm before write operations** — `mem_write` / `key_type` / `mouse_click` all have **side effects**
2. **Bind window first for background operations** — prevent keyboard/mouse from being grabbed by other windows
3. **Move cursor to corner before screenshot** — `mouse_move(0, 0)` to hide cursor and avoid cursor in screenshot
4. **Error messages have `recovery_suggestions`** — when encountering errors, **check here first**, **don't** try blindly

---

## 6. Documentation Cross-references

- Complete 43 tool descriptions + scenarios + error codes: `docs/MCP_TOOLS_REFERENCE.md`
- Scenario-organized usage examples: `OmniFlow 使用示例.md`
- v2 engine workflow example: `examples/workflows/infinite_fish_auto_sell.json`
- Complete error code list: `src/omniflow/tools/errors.py`
- Skills (for AI self-learning): `~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/SKILL.md`

---

## 7. Frequently Asked Questions (FAQ)

**Q: AI called a Tool but keeps failing, what to do?**
A: Let AI take a screenshot to show you the current state. 90% of "X not found" issues are directly visible from a screenshot (window hidden, button obscured, coordinate offset, etc.).

**Q: Tool can't find a suitable workflow engine node?**
A: Workflow v2 engine supports nodes: tool_call / condition / if / loop / delay / subflow / wait_for_window. **Does not** support `wait_for_window_close` (wait for window to disappear) and other rare nodes. Workaround: use `loop_until` + `window_get_info` to poll window existence.

**Q: How to make AI learn OmniFlow usage patterns?**
A: Load the skill under `~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/`. This skill already contains 6 major scenarios, 5 patterns, failure recovery, and design principles.

**Q: AI mistakenly used `mem_write`, what to do?**
A: Undo immediately! `mem_write` writing to wrong address may crash the target process. **Prevention** > **Treatment**: never let AI automatically use `mem_write` — explicitly require "use screenshot + find_image, do not modify memory".

**Q: Workflow engine runs slowly?**
A: Workflow v2 engine is single-threaded sequential execution (v1 is similar), no parallelization. If a workflow has 100 steps, each 100ms, total 10s. Optimization: merge steps, reduce `wait_for_window` polling interval, use `hermes cron` to split large tasks into multiple small tasks.

**Q: Different LLM OmniFlow usage habits?**
A:
- **Claude Opus / Sonnet**: Best at composite Tools, highly sensitive to error codes + recovery suggestions
- **GPT-4 / GPT-4o**: Similar to Claude
- **Local small models (e.g., llama3 7B)**: May fail at multi-step orchestration, **suggest** using `click_image` and other composite Tools to reduce orchestration complexity
