# OmniFlow

> 基于 MCP (Model Context Protocol) 协议的 Windows 自动化全能工具

[English](docs/locales/en/README.md) | **中文** | [日本語](docs/locales/ja/README.md) | [Deutsch](docs/locales/de/README.md)

OmniFlow 将 Windows 桌面自动化能力（窗口操作、图色识别、文字识别、键鼠模拟、后台绑定、内存操作等）封装为标准的 **MCP Server**，使得任何支持 MCP 协议的 AI 客户端（如 Claude Desktop、VS Code、CodeBuddy、Cursor、Windsurf、Continue、Cline、Cody、Crayfish、Hermes、Trae、Kiro 等）都能直接调用 Windows 自动化能力。

---

## ✨ 功能特性

### 🎯 应用场景

OmniFlow 把 Windows 桌面应用变成"可被 AI 调用的工具"，常见落地场景：

- **🎨 图像处理自动化** — 驱动 Photoshop / AI 等专业软件做批量图片处理（缩放、调色、滤镜、批量导出）
- **📸 截图流水线** — 屏幕截图 → OCR 提取文字 / PIL 二次处理 / 标注回写屏幕
- **✏️ 绘图自动化** — 用 mspaint 画示意图、加注解、画流程图
- **🎮 游戏辅助** — 后台挂机、自动战斗、副本流程
- **📝 办公自动化** — WPS / Office 文档自动填写、报表生成、批量格式调整
- **🎬 视频控制** — 播放器自动暂停/续播、字幕识别、定时录制

### 🖥️ 窗口操作
- 窗口查找与枚举（按标题、类名、PID 等）
- 窗口状态获取（位置、大小、是否可见、是否最小化等）
- 窗口置顶 / 取消置顶 / 显示 / 隐藏
- 窗口绑定与解绑（为后台操作做准备）

### 🎯 图色识别
- **找图**：在屏幕指定区域按相似度查找图片位置，支持多图批量查找
- **找色**：单点找色、多点找色、区域找色，支持颜色容差
- **比色**：比较指定坐标点颜色
- **截图**：指定区域截图并保存 / 返回图片数据

### 📝 文字识别 (OCR)
- **找字**：基于预置字库在屏幕查找文字坐标
- **识字**：识别指定区域内的文字内容并返回
- 支持标准字、多色字、偏色字
- 支持免字库 OCR 识别

### ⌨️🖱️ 键鼠模拟
- **前台键鼠**：模拟键盘按键、组合键、字符串输入；鼠标移动 / 点击 / 滚轮
- **后台键鼠**：对已绑定窗口发送后台消息，不抢占焦点
- 支持按键状态控制（按住 / 释放）

### 🧠 后台绑定
- 多种图色绑定模式：`gdi`、`dx`、`dx2`、`opengl` 等
- 多种键鼠绑定模式：`windows`、`normal` 等
- 适用于游戏后台挂机、多窗口并发自动化

#### 4 种 display_mode 选型

| 模式 | 原理 | 优点 | 缺点 | AI 应该何时选择 |
|------|------|------|------|------------------|
| `gdi` | GDI API 截图 | 稳定、兼容性好 | 窗口不能最小化 | **默认首选**，普通桌面软件（WPS / 画图 / PS） |
| `dx` | DirectX Hook | 可最小化、性能高 | 某些游戏不支持 | 用户明确说是 **DirectX 引擎**的游戏 |
| `dx2` | DirectX 增强 | 兼容性更好 | 资源占用稍高 | `dx` 模式失败时尝试 |
| `opengl` | OpenGL Hook | 支持 OpenGL 游戏 | 稍不稳定 | 用户明确说是 **OpenGL 引擎**的游戏 |

**键鼠模式**：`normal`（前台，窗口必须在最前）/ `windows`（Windows 消息后台，**推荐**）

**自动模式选择（未来）**：计划加 `detect_bind_mode(hwnd)` tool，自动尝试 `gdi → dx → dx2 → opengl` 并返回推荐。

### 🧬 内存操作
- 读取 / 写入进程内存
- 内存搜索与特征码定位
- 获取进程模块基址

### 📁 文件与系统
- 文件读写操作
- 系统信息获取（CPU 使用率、内存、屏幕分辨率等）
- 进程枚举与管理

### 🔧 多线程安全
- 支持多线程并发调用
- 每线程独立窗口绑定，互不干扰

### 🔄 工作流
- 可视化 / 脚本化编排自动化任务流程
- 支持条件判断、循环、延迟等待、子流程等控制结构
- 任务链串联执行，前一步输出作为后一步输入
- 支持工作流的保存、加载与复用

### 🧩 插件系统
- 插件热加载，扩展 OmniFlow 能力边界
- 支持自定义 Tool、自定义工作流节点
- 社区插件生态，共享与复用自动化能力

---

## 🏗️ 架构

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
│          Windows 系统底层               │
│     GDI / DX / Win32 API               │
└─────────────────────────────────────────┘
```

---

## 📥 安装

### 前置条件
- Windows 操作系统
- Python 3.10+

### 安装步骤

```bash
# 1. 克隆仓库
git clone <this-repo-url>
cd OmniFlow

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac (部分功能不支持)

# 3. 安装依赖（关键：必须 `pip install -e .`，让 omniflow 包可被 `python -m omniflow` 导入）

# 方式一：使用 requirements.txt + editable install（推荐）
pip install -r requirements.txt
pip install -e .

# 方式二：一行搞定
pip install -r requirements.txt && pip install -e .
```

---

## 🚀 快速开始

### 配置 MCP 客户端

在 MCP 客户端配置文件中添加 OmniFlow：

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

> 说明：
> - `command` 指向 venv 里的 `python.exe`（如 `D:/OmniFlow/.venv/Scripts/python.exe`）
> - `cwd` 指向 OmniFlow 仓库根目录
> - 部分 MCP 客户端**支持** `cwd` 字段（如 Hermes）；不支持的可用 `env.PYTHONPATH` 代替

### 示例：让 AI 自动找个图并点击

> 通过 AI 客户端自然语言描述，OmniFlow 会自动调用对应 MCP Tool：

1. 截取屏幕 → `screenshot`
2. 在截图中找图片 → `find_image`
3. 移动鼠标点击 → `mouse_click`

AI 客户端会自动编排这些 MCP Tool 调用。

---

## 📖 MCP Tools 参考

### 窗口类

| Tool | 说明 |
|------|------|
| `window_find` | 按标题 / 类名查找窗口 |
| `window_enum` | 枚举所有顶层窗口 |
| `window_get_info` | 获取窗口详细信息 |
| `window_set_top` | 窗口置顶 |
| `window_show` | 显示 / 隐藏窗口 |
| `window_activate` | 激活窗口到前台 |
| `window_close` | 关闭窗口（发送 WM_CLOSE 消息，等同于点 X） |

### 绑定类

| Tool | 说明 |
|------|------|
| `bind_window` | 后台绑定窗口，控制键鼠时用户无感知（指定图色 / 键鼠模式） |
| `unbind_window` | 解绑窗口，恢复前台操作 |

### 图色类

| Tool | 说明 |
|------|------|
| `screenshot` | 截图指定区域，返回 Base64 图片 |
| `find_image` | 在指定区域查找图片，返回坐标 |
| `find_color` | 查找指定颜色，返回坐标 |
| `compare_color` | 比较指定坐标颜色 |
| `get_color` | 获取指定坐标颜色值 |

### 文字类

| Tool | 说明 |
|------|------|
| `ocr` | 识别指定区域内的文字 |
| `find_text` | 在屏幕上查找文字位置 |
| `set_ocr_dict` | 设置 OCR 字库文件路径 |

### 键鼠类

| Tool | 说明 |
|------|------|
| `key_press` | 按下键盘按键 |
| `key_down` | 按住键盘按键 |
| `key_up` | 释放键盘按键 |
| `key_type` | 输入字符串 |
| `hotkey` | 发送组合键，如 Ctrl+C |
| `mouse_move` | 移动鼠标 |
| `mouse_click` | 鼠标点击（左 / 右 / 中键） |
| `mouse_scroll` | 鼠标滚轮 |
| `mouse_get_pos` | 获取当前鼠标位置 |

### 内存类

| Tool | 说明 |
|------|------|
| `mem_read` | 读取进程内存 |
| `mem_write` | 写入进程内存 |
| `get_module_base` | 获取进程模块基址 |

### 系统类

| Tool | 说明 |
|------|------|
| `get_system_info` | 获取 CPU、内存等系统信息 |
| `get_screen_size` | 获取屏幕分辨率 |
| `enum_process` | 枚举运行中的进程 |
| `run_program` | 启动外部程序（支持 PATH 搜索和 .lnk 快捷方式） |

### 工作流类

| Tool | 说明 |
|------|------|
| `workflow_run` | 执行指定工作流 |
| `workflow_list` | 列出所有已保存的工作流 |
| `workflow_save` | 保存当前编排的工作流 |
| `workflow_delete` | 删除工作流 |
| `workflow_pause` | 暂停工作流执行 |
| `workflow_resume` | 恢复工作流执行 |

### 组合类（3 个）⭐AI 友好

| Tool | 说明 |
|------|------|
| `click_image` | 找图并点击（合并 find_image + mouse_move + mouse_click） |
| `wait_and_click` | 轮询等图片出现后点击 |
| `ocr_and_click` | OCR 找文字后点击区域中心 |

### 插件类

| Tool | 说明 |
|------|------|
| `plugin_list` | 列出已安装的插件 |
| `plugin_install` | 安装插件 |
| `plugin_uninstall` | 卸载插件 |
| `plugin_enable` | 启用插件 |
| `plugin_disable` | 禁用插件 |

---

## 📁 项目结构

```
OmniFlow/
├── .gitignore               # Git 忽略配置
├── README.md                # 项目说明
├── OmniFlow 使用示例.md      # 使用示例（按场景组织：PS / 截图 / 画图）
├── requirements.txt         # Python 依赖
├── pyproject.toml          # 项目元数据
├── scripts/                 # 辅助脚本
├── docs/
│   ├── AI_INTEGRATION_GUIDE.md   # AI 集成指南（配置 / Prompt / 调试）
│   ├── MCP_TOOLS_REFERENCE.md    # 43 tool 完整参考（含错误码）
│   └── OPTIMIZATION_PLAN.md      # 优化方案
├── src/
│   └── omniflow/
│       ├── __init__.py
│       ├── __main__.py       # 入口 (python -m omniflow)
│       ├── server.py         # MCP Server 主逻辑
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── com.py        # COM / Win32 API 封装
│       │   └── types.py      # 类型定义
│       └── tools/
│           ├── __init__.py
│           ├── window.py     # 窗口相关 Tools（含 window_close）
│           ├── binding.py    # 绑定相关 Tools
│           ├── image.py      # 图色识别 Tools
│           ├── ocr.py        # 文字识别 Tools
│           ├── input.py      # 键鼠模拟 Tools
│           ├── memory.py     # 内存操作 Tools
│           ├── system.py     # 系统相关 Tools（含 run_program）
│           ├── workflow.py   # 工作流 Tools（v2 引擎：IF / WAIT_FOR_WINDOW / 变量系统）
│           └── plugin.py     # 插件系统 Tools
├── examples/
│   ├── open_photoshop.py    # Photoshop 自动化示例
│   ├── ai_prompts/          # AI Prompt 示例（4 个场景）
│   │   ├── game_automation.md
│   │   ├── office_automation.md
│   │   ├── image_processing.md
│   │   └── web_control.md
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # v2 引擎完整工作流示例（自包含）
└── tests/
    ├── __init__.py
    ├── test_tools.py        # 工具基础测试
    └── test_workflow_v2.py  # workflow v2 引擎回归测试（8 个 case）
```

> 注：OmniFlow 引擎 v2 改进（变量系统 / IF 节点 / WAIT_FOR_WINDOW / 安全 condition / 真调 MCP）见 `docs/workflows/translation-notes.md` 和 `known-integrations.md` 中关于 OmniFlow 0.2.0 的条目。

---

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
ruff format src/
ruff check src/
```

---

## 📄 许可证

**MIT License**

OmniFlow 采用 MIT 许可证，这是一种非常宽松的开源许可证：

- ✅ 允许自由使用、复制、修改、分发代码
- ✅ 可用于商业项目
- ✅ 可闭源发布衍生作品
- ⚠️ 仅需保留原始版权声明和许可证文本

具体条款请参见项目中的 LICENSE 文件。

---

## ⚠️ 免责声明

本工具仅供合法用途（如自动化测试、办公自动化等）。请勿将其用于违反游戏服务条款、侵犯他人权益或从事任何非法活动的场景。使用者需自行承担相应责任。
