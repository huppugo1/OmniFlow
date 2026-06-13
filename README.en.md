# OmniFlow

> Windows Automation Toolkit based on MCP (Model Context Protocol)

[English](README.en.md) | **中文** | [日本語](README.ja.md) | [Deutsch](README.de.md)

OmniFlow encapsulates Windows desktop automation capabilities (window operations, image/color recognition, OCR, keyboard/mouse simulation, background binding, memory operations, etc.) as a standard **MCP Server**. Any AI client supporting the MCP protocol (such as Claude Desktop, VS Code, CodeBuddy, Cursor, Windsurf, Continue, Cline, Cody, Crayfish, Hermes, Trae, Kiro, etc.) can directly call Windows automation capabilities.

---

## ✨ Features

### 🎯 Use Cases

OmniFlow turns Windows desktop applications into "AI-callable tools". Common use cases:

- **🎨 Image Processing Automation** — Drive Photoshop/AI for batch image processing (resizing, color grading, filters, batch export)
- **📸 Screenshot Pipeline** — Screen capture → OCR text extraction / PIL secondary processing / annotation back to screen
- **✏️ Drawing Automation** — Use mspaint to draw diagrams, add annotations, flowcharts
- **🎮 Game Automation** — Background AFK, auto-battle, dungeon recording and playback
- **📝 Office Automation** — WPS/Office document auto-fill, report generation, batch formatting
- **🎬 Video Control** — Player auto-pause/resume, subtitle recognition, scheduled recording

### 🖥️ Window Operations
- Window finding and enumeration (by title, class name, PID, etc.)
- Get window status (position, size, visibility, minimized state, etc.)
- Window topmost / cancel topmost / show / hide
- Window binding and unbinding (prepare for background operations)

### 🎯 Image & Color Recognition
- **Find Image**: Search for image position by similarity in specified screen area, supports batch search
- **Find Color**: Single point color search, multi-point color search, area color search, supports color tolerance
- **Compare Color**: Compare color at specified coordinate
- **Screenshot**: Capture specified area and save / return image data

### 📝 OCR (Optical Character Recognition)
- **Find Text**: Search for text coordinates on screen based on preset dictionary
- **Recognize Text**: Recognize text content in specified area and return
- Supports standard characters, multi-color characters, color-shifted characters
- Supports dictionary-free OCR recognition

### ⌨️🖱️ Keyboard & Mouse Simulation
- **Foreground Input**: Simulate keyboard keys, key combinations, string input; mouse move / click / scroll
- **Background Input**: Send background messages to bound windows without stealing focus
- Supports key state control (press / release)

### 🧠 Background Binding
- Multiple image/color binding modes: `gdi`, `dx`, `dx2`, `opengl`, etc.
- Multiple keyboard/mouse binding modes: `windows`, `normal`, etc.
- Suitable for game background AFK, multi-window concurrent automation

### 🧬 Memory Operations
- Read / Write process memory
- Memory search and pattern scanning
- Get process module base address

### 📁 File & System
- File read/write operations
- System information retrieval (CPU usage, memory, screen resolution, etc.)
- Process enumeration and management

### 🔧 Thread Safety
- Supports multi-threaded concurrent calls
- Each thread has independent window binding, no interference

### 🔄 Workflow
- Visual / script-based automation task orchestration
- Supports control structures like conditionals, loops, delay waiting, sub-flows
- Task chain execution, output of previous step as input for next step
- Supports workflow saving, loading and reuse

### 🧩 Plugin System
- Plugin hot-loading to extend OmniFlow capabilities
- Supports custom Tools, custom workflow nodes
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
│          Windows System Layer           │
│     GDI / DX / Win32 API               │
└────────────────────────────────────────┘
```

---

## 📥 Installation

### Prerequisites
- Windows OS
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

# 3. Install dependencies (Important: must use `pip install -e .` to make omniflow package importable via `python -m omniflow`)

# Method 1: requirements.txt + editable install (Recommended)
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
      "cwd": "<local OmniFlow repo path>"
    }
  }
}
```

> Notes:
> - `command` points to python.exe in venv (e.g., `D:/OmniFlow/.venv/Scripts/python.exe`)
> - `cwd` points to OmniFlow repository root directory
> - Some MCP clients **support** the `cwd` field (e.g., Hermes); for those that don't, use `env.PYTHONPATH` instead

### Example: Let AI Find an Image and Click It

> Through natural language description in AI client, OmniFlow automatically calls corresponding MCP Tools:

1. Capture screen → `screenshot`
2. Find image in screenshot → `find_image`
3. Move mouse and click → `mouse_click`

AI clients automatically orchestrate these MCP Tool calls.

---

## 📖 MCP Tools Reference

### Window Tools

| Tool | Description |
|------|-------------|
| `window_find` | Find window by title / class name |
| `window_enum` | Enumerate all top-level windows |
| `window_get_info` | Get detailed window information |
| `window_set_top` | Set window topmost |
| `window_show` | Show / hide window |
| `window_activate` | Activate window to foreground |
| `window_close` | Close window (sends WM_CLOSE message, equivalent to clicking X) |

### Binding Tools

| Tool | Description |
|------|-------------|
| `bind_window` | Bind window for background operation, keyboard/mouse control is user-transparent (specify image/color and input modes) |
| `unbind_window` | Unbind window, restore foreground operation |

### Image Tools

| Tool | Description |
|------|-------------|
| `screenshot` | Capture specified area, return Base64 image |
| `find_image` | Find image in specified area, return coordinates |
| `find_color` | Find specified color, return coordinates |
| `compare_color` | Compare color at specified coordinate |
| `get_color` | Get color value at specified coordinate |

### Text Tools

| Tool | Description |
|------|-------------|
| `ocr` | Recognize text in specified area |
| `find_text` | Find text position on screen |
| `set_ocr_dict` | Set OCR dictionary file path |

### Input Tools

| Tool | Description |
|------|-------------|
| `key_press` | Press and release keyboard key |
| `key_down` | Hold keyboard key down |
| `key_up` | Release keyboard key |
| `key_type` | Type string |
| `hotkey` | Send key combination, e.g., Ctrl+C |
| `mouse_move` | Move mouse |
| `mouse_click` | Mouse click (left / right / middle) |
| `mouse_scroll` | Mouse scroll |
| `mouse_get_pos` | Get current mouse position |

### Memory Tools

| Tool | Description |
|------|-------------|
| `mem_read` | Read process memory |
| `mem_write` | Write process memory |
| `get_module_base` | Get module base address |

### System Tools

| Tool | Description |
|------|-------------|
| `get_system_info` | Get CPU, memory and other system information |
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
├── README.md                # Project documentation (Chinese)
├── README.en.md             # Project documentation (English)
├── README.ja.md             # Project documentation (Japanese)
├── README.de.md             # Project documentation (German)
├── OmniFlow 使用示例.md      # Usage examples (by scenario: PS / screenshot / drawing)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata
├── scripts/                 # Helper scripts
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
│           ├── window.py     # Window Tools (includes window_close)
│           ├── binding.py    # Binding Tools
│           ├── image.py      # Image/Color Recognition Tools
│           ├── ocr.py        # OCR Tools
│           ├── input.py      # Keyboard/Mouse Simulation Tools
│           ├── memory.py     # Memory Operation Tools
│           ├── system.py     # System Tools (includes run_program)
│           ├── workflow.py   # Workflow Tools (v2 engine: IF / WAIT_FOR_WINDOW / variable system)
│           └── plugin.py     # Plugin System Tools
├── examples/
│   ├── open_photoshop.py    # Photoshop automation example
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # Complete v2 engine workflow example (self-contained)
└── tests/
    ├── __init__.py
    ├── test_tools.py        # Basic tool tests
    └── test_workflow_v2.py  # Workflow v2 engine regression tests (8 cases)
```

> Note: OmniFlow engine v2 improvements (variable system / IF node / WAIT_FOR_WINDOW / safe condition / true MCP calls) can be found in `docs/workflows/translation-notes.md` and the OmniFlow 0.2.0 entry in `known-integrations.md`.

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

MIT License

---

## ⚠️ Disclaimer

This tool is for legal purposes only (such as automation testing, office automation, etc.). Do not use it for scenarios that violate game terms of service, infringe on others' rights, or engage in any illegal activities. Users are responsible for their own actions.