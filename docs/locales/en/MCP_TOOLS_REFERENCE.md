# OmniFlow MCP Tools Reference

> Complete 43 MCP Tools usage scenarios, parameters, returns, error codes, and common combinations.

---

## 1. Unified Return Format

All Tool calls return JSON with **unified format**:

```json
{
  "success": true,
  "data": { ... },                  // Original tool return (preserved fields)
  "message": "ok",                  // Human-readable
  "error_code": null,               // Error code (null on success)
  "recovery_suggestions": []       // Filled with recovery suggestions on error
}
```

**Success path**: success=true, data preserves original dict structure (backward compatible with workflow dispatcher field extraction).
**Failure path**: success=false, message + error_code + recovery_suggestions triad gives AI complete context.

**Only exception**: `screenshot` tool additionally returns `ImageContent` (base64 PNG), outer TextContent uses unified format to describe dimensions.

---

## 2. Error Code System

OmniFlow defines **31 error codes** (E0000-E8002), segmented by module:

| Segment | Module | Count | Examples |
|---|---|---|---|
| E0xxx | General | 5 | E0000 UNKNOWN / E0001 INVALID_ARG |
| E1xxx | Window | 4 | E1001 WINDOW_NOT_FOUND |
| E2xxx | Image | 4 | E2001 IMAGE_NOT_FOUND |
| E3xxx | OCR | 3 | E3001 OCR_ENGINE_ERROR |
| E4xxx | Input | 3 | E4001 INPUT_SEND_FAILED |
| E5xxx | Memory | 4 | E5003 PROCESS_NOT_FOUND |
| E6xxx | System | 3 | E6002 PROGRAM_LAUNCH_FAILED |
| E7xxx | Workflow | 3 | E7001 WORKFLOW_NOT_FOUND |
| E8xxx | Plugin | 2 | E8001 PLUGIN_NOT_FOUND |

Each error code has **pre-configured** recovery suggestions (`RECOVERY_SUGGESTIONS`), automatically injected into the `recovery_suggestions` field when a tool fails. LLM sees the error code and **immediately** knows what to do next.

Detailed list and recovery suggestions in `src/omniflow/tools/errors.py`.

---

## 3. Tool Quick Reference (Grouped by Function)

### 3.1 Window Tools (7)

#### `window_find`
- **Purpose**: Find window by class_name / title / pid
- **Parameters**: `title` (str) / `class_name` (str) / `pid` (int), at least one required
- **Returns**: `WindowInfo` dict (hwnd, title, class_name, pid, rect, ...) or null
- **Error codes**: `E1001` (WINDOW_NOT_FOUND) / `E1003` (INVALID_HWND)
- **Common combination**: `window_find` → `window_activate` → `bind_window` (background operation chain starting point)
- **Note**: title often contains spaces or special characters ("Game Name - Launcher"), using class_name is more stable

#### `window_enum`
- **Purpose**: List all visible top-level windows
- **Returns**: `[WindowInfo, ...]`
- **Error codes**: None (enumeration won't fail)
- **Common combination**: First `window_enum` → user picks one → `window_find` to lock
- **AI tip**: Prioritize this when user says "list all open windows"

#### `window_get_info`
- **Purpose**: Get real-time window info (position, minimized state, parent_hwnd)
- **Parameters**: `hwnd` (int, required)
- **Returns**: `WindowInfo`
- **Error codes**: `E1001` / `E1003`
- **Common combination**: `window_get_info` → calculate coordinate offset → other tools for relative positioning

#### `window_set_top`
- **Purpose**: Set / cancel topmost
- **Parameters**: `hwnd` / `on_top` (bool, default True)
- **Returns**: `{"status": "ok"}`
- **Typical usage**: Keep target window always in front during debugging
- **Note**: Close button of topmost window may sometimes be obscured by system taskbar

#### `window_show`
- **Purpose**: Show / hide window
- **Parameters**: `hwnd` / `show` (bool, True=show False=hide)
- **Error codes**: `E1003`
- **vs window_close**: `show=False` is hide (recoverable), `window_close` sends WM_CLOSE (actually closes)

#### `window_activate`
- **Purpose**: Bring window to foreground
- **Parameters**: `hwnd`
- **Error codes**: `E1003`
- **Common combination**: After `window_activate` then `key_type` / `mouse_click` (foreground operation)
- **AI note**: Foreground operations may be grabbed by other windows, long tasks need bind_window

#### `window_close` ⭐New
- **Purpose**: Send WM_CLOSE message to close window (equivalent to clicking X)
- **Parameters**: `hwnd`
- **Error codes**: `E1003` / `E1004` (WINDOW_CLOSE_FAILED)
- **vs window_show(show=False)**: close is "really close" (program receives OnClose event and can save confirmation), hide is "hide it"
- **Typical usage**: Close opened child windows ("previous backpack window not closed" scenario)

### 3.2 Binding Tools (2)

#### `bind_window`
- **Purpose**: Bind window to background mode (no foreground messages)
- **Parameters**: `hwnd` (required) / `display_mode` (gdi/dx/dx2/opengl, default gdi) / `mouse_mode` (normal/windows) / `keyboard_mode` (normal/windows)
- **Returns**: `{"status": "ok", "bound": bool}`
- **Error codes**: `E1002` (WINDOW_BIND_FAILED)
- **4 display_mode options** (see README "Binding Modes" chapter):
  - `gdi`: GDI API screenshot, best compatibility, **default first choice** (ordinary desktop software, WPS, Paint, etc.)
  - `dx`: DirectX Hook, supports minimization, **games** (DirectX engine)
  - `dx2`: dx enhanced, better compatibility, try when dx fails
  - `opengl`: OpenGL Hook, supports OpenGL games
- **4 mouse/keyboard_mode options**:
  - `normal`: Foreground mode (window must be in foreground)
  - `windows`: Windows message background (recommended, almost all programs support)

#### `unbind_window`
- **Purpose**: Unbind
- **Parameters**: `hwnd`
- **Error codes**: `E1003`
- **Typical usage**: Unbind old before switching working windows

### 3.3 Image/Color Tools (5)

#### `screenshot`
- **Purpose**: Screenshot (full screen or area), return base64 PNG
- **Parameters**: `left`/`top`/`right`/`bottom` (area, omit = full screen)
- **Returns**: ImageContent (base64 PNG) + unified format TextContent (width/height)
- **Error codes**: `E2003` (SCREENSHOT_FAILED) / `E2004` (INVALID_REGION)
- **Note**:
  - Under DPI scaling, use `get_screen_size` for physical pixels, don't use `window_get_info.rect` (that's logical pixels)
  - Multi-screen defaults to main monitor
  - Screenshot is synchronous blocking (50-200ms), use mss library for high-frequency scenarios

#### `find_image`
- **Purpose**: Find template image on screen, return coordinates
- **Parameters**: `image_path` (required) / `similarity` (0-1, default 0.9) / `left`/`top`/`right`/`bottom` (area)
- **Returns**: `{found, x?, y?, similarity?}`
- **Error codes**: `E2001` (IMAGE_NOT_FOUND) / `E2002` (TEMPLATE_LOAD_FAILED)
- **AI similarity selection guide**:
  - 0.95+: Exact match (unique icon)
  - 0.85-0.95: Regular UI buttons
  - 0.7-0.85: Games with BUFF effects, animated buttons
- **Common combination**: `screenshot` → `find_image` → `mouse_click` ("find image and click" standard trio)

#### `find_color`
- **Purpose**: Find color in area (with tolerance)
- **Parameters**: `color` (hex "FF0000") / `tolerance` (0-255) / area
- **Error codes**: `E2001` (not found) / `E2004`
- **vs compare_color**: find_color is "search in area", compare_color is "check a point"
- **Typical usage**: Detect HP bar color (full HP vs low HP) → trigger auto potion drinking

#### `compare_color`
- **Purpose**: Check if pixel color at a point matches expectation
- **Parameters**: `x`/`y` / `color` (hex) / `tolerance`
- **Returns**: `{match: bool}`
- **Error codes**: `E0001` (INVALID_ARG)
- **Typical usage**: Detect status indicator light (green = online, red = offline)

#### `get_color`
- **Purpose**: Get pixel color value at a point
- **Parameters**: `x`/`y`
- **Returns**: `{hex, r, g, b}`
- **Common usage**: Debugging ("what color is that button")

### 3.4 OCR Tools (3)

#### `ocr`
- **Purpose**: Recognize text in area
- **Parameters**: `left`/`top`/`right`/`bottom` (area)
- **Returns**: `{text: str}`
- **Error codes**: `E3001` (OCR_ENGINE_ERROR) / `E3003` (OCR_NOT_INSTALLED)
- **Engine fallback chain**: Tesseract (requires pytesseract+training packages) → EasyOCR (downloads model on first use) → Windows.Media.Ocr (English only)
- **Note**: Returns **a long text**, does not return bbox for each word. Use find_image to find text image templates for coordinates

#### `find_text`
- **Purpose**: Check if area contains specified text
- **Parameters**: `text` (required) / area
- **Returns**: `{found: bool, text}` (**does not return coordinates**)
- **Error codes**: `E3002` (TEXT_NOT_FOUND)
- **Typical usage**: Determine a state ("is it on the login screen" → find "Login" text)

#### `set_ocr_dict`
- **Purpose**: Set custom OCR font library
- **Parameters**: `dict_path` (path to .txt character library)
- **Returns**: `{status, dict_path}`
- **Typical usage**: Limit recognized character set (only numbers, English) → improve accuracy

### 3.5 Keyboard/Mouse Tools (9)

#### `key_press` / `key_down` / `key_up`
- **Purpose**: Single key operation (press=press and release, down=hold, up=release)
- **Parameters**: `key` (valid key name)
- **Error codes**: `E4001` (INPUT_SEND_FAILED) / `E4002` (INVALID_KEY)
- **Valid key names**: Alphanumeric / `enter` / `tab` / `esc` / `f1`-`f12` / `ctrl` / `alt` / `shift` / `win` / `space` / `backspace` / arrow keys

#### `key_type`
- **Purpose**: Input string
- **Parameters**: `text` (required) / `interval` (seconds between characters, default 0)
- **Error codes**: `E4001`
- **AI tip**: Chinese input must use `interval=0.05` (IME can't keep up); English can use `interval=0`

#### `hotkey`
- **Purpose**: Combination keys
- **Parameters**: `keys` (array, required), e.g., `["ctrl", "s"]`
- **Error codes**: `E4001` / `E4002`
- **Typical usage**: `hotkey(ctrl+s)` to save, `hotkey(ctrl+c)` to copy

#### `mouse_move` / `mouse_click` / `mouse_scroll` / `mouse_get_pos`
- **Purpose**: Mouse operations
- **Parameters**: `x` / `y` / `duration` (move time) / `button` (left/right/middle) / `clicks` (consecutive clicks)
- **Error codes**: `E4001` / `E4003` (background operation needs bind first)
- **AI note**: Coordinates may offset under multi-screen / DPI scaling. Prioritize using find_image for coordinates, **don't** hardcode

### 3.6 Memory Tools (3)

#### `mem_read`
- **Purpose**: Read process memory
- **Parameters**: `pid` / `address` (decimal integer) / `size` (bytes, default 4)
- **Returns**: `{data_hex, size}`
- **Error codes**: `E5001` (MEM_READ_FAILED) / `E5003` (PROCESS_NOT_FOUND) / `E5004` (INVALID_ADDRESS)
- **⚠️ Reading other process memory requires admin privileges**. Reading own process does not

#### `mem_write`
- **Purpose**: Write process memory
- **Parameters**: `pid` / `address` / `data_hex` (hex string)
- **Error codes**: `E5002` (MEM_WRITE_FAILED)
- **⚠️ Writing memory may crash the target process** — AI should use under explicit user authorization

#### `get_module_base`
- **Purpose**: Get DLL/EXE module base address
- **Parameters**: `pid` / `module_name` (e.g., `"kernel32.dll"`)
- **Returns**: `{base: int}` (decimal representation of hex address)
- **Typical usage**: Base address + offset = field address (`game.exe+0x1234 = HP address`)

### 3.7 System Tools (4)

#### `get_system_info`
- **Purpose**: CPU / memory / screen / OS
- **Returns**: `{cpu_percent, memory_total_gb, memory_used_gb, screen_width, screen_height, os_version}`
- **Error codes**: `E6001` (psutil missing → `pip install psutil`)
- **Dependencies**: `psutil`

#### `get_screen_size`
- **Purpose**: Physical resolution
- **Returns**: `{width, height}`
- **Typical usage**: Get real pixels under DPI scaling, use with screenshot area parameters

#### `enum_process`
- **Purpose**: Enumerate processes with visible windows
- **Limitation**: Only lists processes with windows (tray-only apps missing)
- **Returns**: `[{pid, name, title, hwnd?}, ...]`
- **Error codes**: `E5003` (can't get name for some process)

#### `run_program` ⭐New
- **Purpose**: Launch external program
- **Parameters**: `program_path` (required) / `args` (list, optional) / `cwd` (optional)
- **Returns**: `{status, pid?, path}`
- **Error codes**: `E6002` (PROGRAM_LAUNCH_FAILED) / `E6003` (PROGRAM_NOT_FOUND)
- **Two modes**:
  - `args=None`: Use `ShellExecute`, auto search by PATH, recognize .lnk shortcuts
  - `args=[...]`: Use `subprocess.Popen`, need full command line parameters
- **Typical usage**:
  - `run_program("notepad")` —— launch notepad
  - `run_program("D:/soft/QQ/QQ.exe", ["-auto"], "D:/soft/QQ")` —— launch QQ with parameters

### 3.8 Workflow Tools (6)

#### `workflow_save`
- **Purpose**: Save workflow
- **Parameters**: `name` / `steps` (list of step dicts)
- **Returns**: `{id, name, status: "saved"}`
- **Error codes**: `E7003` (WORKFLOW_SAVE_FAILED)
- **Storage location**: `~/.omniflow/workflows/{id}.json` (id is md5(name)[:12])

#### `workflow_list`
- **Purpose**: List all workflows
- **Returns**: `{workflows: [{id, name, description, step_count}, ...], count}`

#### `workflow_run`
- **Purpose**: Execute workflow (**v2 engine** — real MCP tool calls, variable system, IF/WAIT_FOR_WINDOW nodes, improved LOOP)
- **Parameters**: `workflow_id`
- **Returns**: `{status, results, context}`
- **Error codes**: `E7001` (WORKFLOW_NOT_FOUND) / `E7002` (WORKFLOW_VALIDATION_FAILED) / `E7003`

#### `workflow_pause` / `workflow_resume` / `workflow_delete`
- Standard CRUD

### 3.9 Plugin Tools (5)

#### `plugin_list`
- **Purpose**: List installed plugins
- **Returns**: `[{id, name, enabled, version}, ...]`

#### `plugin_install` / `plugin_uninstall` / `plugin_enable` / `plugin_disable`
- Standard CRUD
- **Error codes**: `E8001` / `E8002`

---

## 4. Typical Multi-Tool Orchestration Patterns

| Task | Orchestration |
|---|---|
| **Find image and click** | `screenshot` → `find_image` → `mouse_move` + `mouse_click` |
| **Log in to desktop app** | `window_find` → `window_activate` → `key_type` → `hotkey(enter)` |
| **OCR extract text** | `screenshot(area)` → `ocr(area)` → LLM parsing |
| **Game background loop** | `bind_window(dx)` → loop `find_image` + `mouse_click` + `key_press` |
| **Clear pop-ups** | `window_find(each pop-up type)` → `key_press(enter)` or `window_close` if found |
| **Auto screenshot save** | `screenshot` → base64 → PIL processing → save |

See `examples/workflows/infinite_fish_auto_sell.json` (v2 engine complete example) and `OmniFlow 使用示例.md` (scenario-classified code examples).

---

## 5. Design Principles (For AI)

1. **Prioritize image/color** (find_image + screenshot), avoid `mem_read/write` (permission requirements + crash risk)
2. **Don't hardcode coordinates** — coordinates offset under different DPI / window sizes; use find_image for coordinates
3. **Check recovery_suggestions after errors** — it tells you what to do next
4. **Bind window first for background operations** — prevent keyboard/mouse from being grabbed by other windows
5. **Check window_get_info before multi-step operations** to confirm window state

---

## 6. Documentation Cross-references

- Complete API description + input schema: `server.py` `TOOLS` list
- Scenario-organized usage examples: `OmniFlow 使用示例.md`
- v2 engine workflow example: `examples/workflows/infinite_fish_auto_sell.json`
- Complete error code list + recovery suggestions: `src/omniflow/tools/errors.py`
