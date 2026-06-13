# OmniFlow

> Windows Automation All-in-One Tool based on MCP (Model Context Protocol)

**[English](README.md)** | [中文](../zh-CN/README.md) | [日本語](../ja/README.md) | [Deutsch](../de/README.md)

OmniFlow encapsulates Windows desktop automation capabilities (window operations, image/color recognition, text recognition, keyboard/mouse simulation, background binding, memory operations, etc.) into a standard **MCP Server**, enabling any AI client that supports the MCP protocol (such as Claude Desktop, VS Code, CodeBuddy, Cursor, Windsurf, Continue, Cline, Cody, Crayfish, Hermes, Trae, Kiro, etc.) to directly invoke Windows automation capabilities.

---

## ✨ Features

### 🎯 Application Scenarios

OmniFlow turns Windows desktop applications into "tools callable by AI". Common use cases:

- **🎨 Image Processing Automation** — Drive Photoshop / AI and other professional software for batch image processing (scaling, color adjustment, filters, batch export)
- **📸 Screenshot Pipeline** — Screen capture → OCR text extraction / PIL secondary processing / annotation back to screen
- **✏️ Drawing Automation** — Use mspaint to draw diagrams, add annotations, create flowcharts
- **🎮 Game Assistance** — Background挂机, auto-combat, dungeon automation
- **📝 Office Automation** — WPS / Office document auto-fill, report generation, batch format adjustment
- **🎬 Video Control** — Player auto pause/resume, subtitle recognition, scheduled recording

### 🖥️ Window Operations
- Window finding and enumeration (by title, class name, PID, etc.)
- Window state retrieval (position, size, visibility, minimized state, etc.)
- Window topmost / cancel topmost / show / hide
- Window bind and unbind (preparation for background operations)

### 🎯 Image/Color Recognition
- **Find Image**: Find image positions in specified screen areas by similarity, supports batch multi-image search
- **Find Color**: Single-point, multi-point, and area color search, supports color tolerance
- **Compare Color**: Compare colors at specified coordinates
- **Screenshot**: Capture specified areas and save / return image data

### 📝 Text Recognition (OCR)
- **Find Text**: Find text coordinates on screen based on preset font library
- **Recognize Text**: Recognize and return text content in specified areas
- Supports standard fonts, multi-color fonts, and偏色 fonts
- Supports OCR without font library

### ⌨️🖱️ Keyboard/Mouse Simulation
- **Foreground Input**: Simulate keyboard keys, combinations, and string input; mouse move / click / scroll
- **Background Input**: Send background messages to bound windows without grabbing focus
- Supports key state control (hold / release)

### 🧠 Background Binding
- Multiple image binding modes: `gdi`, `dx`, `dx2`, `opengl`, etc.
- Multiple keyboard/mouse binding modes: `windows`, `normal`, etc.
- Suitable for game background挂机 and multi-window concurrent automation

#### 4 display_mode Options

| Mode | Principle | Pros | Cons | When AI Should Choose |
|------|-----------|------|------|----------------------|
| `gdi` | GDI API screenshot | Stable, good compatibility | Window cannot be minimized | **Default first choice**, ordinary desktop software (WPS / Paint / PS) |
| `dx` | DirectX Hook | Can be minimized, high performance | Some games don't support | When user explicitly says **DirectX engine** game |
| `dx2` | DirectX enhanced | Better compatibility | Slightly higher resource usage | Try when `dx` mode fails |
| `opengl` | OpenGL Hook | Supports OpenGL games | Slightly unstable | When user explicitly says **OpenGL engine** game |

**Keyboard/Mouse Mode**: `normal` (foreground, window must be topmost) / `windows` (Windows message background, **recommended**)

**Auto Mode Selection (Future)**: Plan to add `detect_bind_mode(hwnd)` tool to automatically try `gdi → dx → dx2 → opengl` and return recommendation.

### 🧬 Memory Operations
- Read / write process memory
- Memory search and signature scanning
- Get process module base address

### 📁 File and System
- File read/write operations
- System info retrieval (CPU usage, memory, screen resolution, etc.)
- Process enumeration and management

### 🔧 Multi-threading Safety
- Supports multi-threaded concurrent calls
- Per-thread independent window binding, no interference

### 🔄 Workflow
- Visual / scripted automation task flow orchestration
- Supports conditionals, loops, delays, sub-flows, and other control structures
- Task chain execution with previous step output as next step input
- Supports workflow save, load, and reuse

### 🧩 Plugin System
- Plugin hot-loading to extend OmniFlow capabilities
- Supports custom Tools and custom workflow nodes
- Community plugin ecosystem for sharing and reusing automation capabilities

---

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│           AI Client (MCP Host)          │
│  Claude Desktop / CodeBuddy / VS Code   │
│  Cursor / Windsurf / Continue / Cline   │
│  Crayfish / Hermes / Trae / Kiro ...     │
└──────────────┬─────────────────────────┘
               │  MCP Protocol (stdio)
┌──────────────▼─────────────────────────┐
│           OmniFlow MCP Server           │
│  ┌───────────────────────────────────┐  │
│  │         MCP Tools Layer           │  │
│  │  window / image / text / input    │  │
│  │  / binding / memory / system ...  │  │
│  └──────────────┬────────────────────┘  │
│  ┌──────────────▼────────────────────┐  │
│  │        Automation Engine          │  │
│  │     Win32 API / COM / ctypes      │  │
│  └──────────────┬────────────────────┘  │
└─────────────────┼───────────────────────┘
┌─────────────────▼───────────────────────┐
│          Windows System底层             │
│     GDI / DX / Win32 API               │
└─────────────────────────────────────────┘
```

---

## 📥 Installation

### Prerequisites
- Windows operating system
- Python 3.10+

### Installation Steps

```bash
# 1. Clone repository
git clone <this-repo-url>
cd OmniFlow

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac (some features not supported)

# 3. Install dependencies (key: must use `pip install -e .` so omniflow package can be imported by `python -m omniflow`)

# Method 1: Use requirements.txt + editable install (recommended)
pip install -r requirements.txt
pip install -e .

# Method 2: One-liner
pip install -r requirements.txt && pip install -e .
```

---

## 🚀 Quick Start

### Configure MCP Client

Add OmniFlow to your MCP client configuration file:

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

> Notes:
> - `command` points to `python.exe` in venv (e.g., `D:/OmniFlow/.venv/Scripts/python.exe`)
> - `cwd` points to OmniFlow repository root directory
> - Some MCP clients **support** the `cwd` field (e.g., Hermes); for those that don't, use `env.PYTHONPATH` instead

### Example: Let AI automatically find an image and click

> Through natural language description in AI client, OmniFlow will automatically call the corresponding MCP Tool:

1. Capture screen → `screenshot`
2. Find image in screenshot → `find_image`
3. Move mouse and click → `mouse_click`

AI client will automatically orchestrate these MCP Tool calls.

---

## 📖 MCP Tools Reference

### Window Tools

| Tool | Description |
|------|-------------|
| `window_find` | Find window by title / class name |
| `window_enum` | Enumerate all top-level windows |
| `window_get_info` | Get window detailed information |
| `window_set_top` | Set window topmost |
| `window_show` | Show / hide window |
| `window_activate` | Activate window to foreground |
| `window_close` | Close window (send WM_CLOSE message, equivalent to clicking X) |

### Binding Tools

| Tool | Description |
|------|-------------|
| `bind_window` | Background bind window, control keyboard/mouse without user awareness (specify image / keyboard/mouse mode) |
| `unbind_window` | Unbind window, restore foreground operation |

### Image/Color Tools

| Tool | Description |
|------|-------------|
| `screenshot` | Capture specified area, return Base64 image |
| `find_image` | Find image in specified area, return coordinates |
| `find_color` | Find specified color, return coordinates |
| `compare_color` | Compare color at specified coordinates |
| `get_color` | Get color value at specified coordinates |

### Text Tools

| Tool | Description |
|------|-------------|
| `ocr` | Recognize text in specified area |
| `find_text` | Find text position on screen |
| `set_ocr_dict` | Set OCR font library file path |

### Keyboard/Mouse Tools

| Tool | Description |
|------|-------------|
| `key_press` | Press keyboard key |
| `key_down` | Hold keyboard key |
| `key_up` | Release keyboard key |
| `key_type` | Input string |
| `hotkey` | Send combination keys, e.g., Ctrl+C |
| `mouse_move` | Move mouse |
| `mouse_click` | Mouse click (left / right / middle) |
| `mouse_scroll` | Mouse scroll |
| `mouse_get_pos` | Get current mouse position |

### Memory Tools

| Tool | Description |
|------|-------------|
| `mem_read` | Read process memory |
| `mem_write` | Write process memory |
| `get_module_base` | Get process module base address |

### System Tools

| Tool | Description |
|------|-------------|
| `get_system_info` | Get CPU, memory, and other system information |
| `get_screen_size` | Get screen resolution |
| `enum_process` | Enumerate running processes |
| `run_program` | Launch external program (supports PATH search and .lnk shortcuts) |

### Workflow Tools

| Tool | Description |
|------|-------------|
| `workflow_run` | Execute specified workflow |
| `workflow_list` | List all saved workflows |
| `workflow_save` | Save current orchestrated workflow |
| `workflow_delete` | Delete workflow |
| `workflow_pause` | Pause workflow execution |
| `workflow_resume` | Resume workflow execution |

### Composite Tools (3) ⭐AI-friendly

| Tool | Description |
|------|-------------|
| `click_image` | Find image and click (combines find_image + mouse_move + mouse_click) |
| `wait_and_click` | Poll until image appears, then click |
| `ocr_and_click` | OCR find text, then click area center |

### Plugin Tools

| Tool | Description |
|------|-------------|
| `plugin_list` | List installed plugins |
| `plugin_install` | Install plugin |
| `plugin_uninstall` | Uninstall plugin |
| `plugin_enable` | Enable plugin |
| `plugin_disable` | Disable plugin |

---

## 📁 Project Structure

```
OmniFlow/
├── .gitignore               # Git ignore configuration
├── README.md                # Project documentation
├── OmniFlow 使用示例.md      # Usage examples (organized by scenario: PS / Screenshot / Drawing)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata
├── scripts/                 # Helper scripts
├── docs/
│   ├── AI_INTEGRATION_GUIDE.md   # AI integration guide (configuration / Prompt / debugging)
│   ├── MCP_TOOLS_REFERENCE.md    # 43 tools complete reference (with error codes)
│   └── OPTIMIZATION_PLAN.md      # Optimization plan
├── src/
│   └── omniflow/
│       ├── __init__.py
│       ├── __main__.py       # Entry point (python -m omniflow)
│       ├── server.py         # MCP Server main logic
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── com.py        # COM / Win32 API wrapper
│       │   └── types.py      # Type definitions
│       └── tools/
│           ├── __init__.py
│           ├── window.py     # Window related Tools (includes window_close)
│           ├── binding.py    # Binding related Tools
│           ├── image.py      # Image/color recognition Tools
│           ├── ocr.py        # Text recognition Tools
│           ├── input.py      # Keyboard/mouse simulation Tools
│           ├── memory.py     # Memory operation Tools
│           ├── system.py     # System related Tools (includes run_program)
│           ├── workflow.py   # Workflow Tools (v2 engine: IF / WAIT_FOR_WINDOW / variable system)
│           └── plugin.py     # Plugin system Tools
├── examples/
│   ├── open_photoshop.py    # Photoshop automation example
│   ├── ai_prompts/          # AI Prompt examples (4 scenarios)
│   │   ├── game_automation.md
│   │   ├── office_automation.md
│   │   ├── image_processing.md
│   │   └── web_control.md
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # v2 engine complete workflow example (self-contained)
└── tests/
    ├── __init__.py
    ├── test_tools.py        # Tool basic tests
    └── test_workflow_v2.py  # workflow v2 engine regression tests (8 cases)
```

> Note: OmniFlow engine v2 improvements (variable system / IF node / WAIT_FOR_WINDOW / safe condition / real MCP calls) see `docs/workflows/translation-notes.md` and `known-integrations.md` for OmniFlow 0.2.0 entries.

---

## 🛠️ Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
ruff format src/
ruff check src/
```

---

## 📄 License

**MIT License**

OmniFlow uses the MIT License, a very permissive open source license:

- ✅ Allows free use, copying, modification, and distribution of code
- ✅ Can be used for commercial projects
- ✅ Can release derivative works as closed source
- ⚠️ Only need to retain original copyright notice and license text

For specific terms, please see the LICENSE file in the project.

---

## ⚠️ Disclaimer

This tool is for legal purposes only (such as automated testing, office automation, etc.). Do not use it for scenarios that violate game terms of service, infringe on others' rights, or engage in any illegal activities. Users bear their own responsibility.
