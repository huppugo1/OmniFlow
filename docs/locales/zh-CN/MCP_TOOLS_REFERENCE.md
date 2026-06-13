# OmniFlow MCP Tools 参考

> 完整 43 个 MCP Tool 的使用场景、参数、返回、错误码、常见组合。

---

## 1. 统一返回格式

所有 Tool 调用返回 JSON，**统一格式**：

```json
{
  "success": true,
  "data": { ... },                  // 原 tool 返回（保留字段）
  "message": "ok",                  // 人类可读
  "error_code": null,               // 错误码（成功时为 null）
  "recovery_suggestions": []       // 错误时填充恢复建议
}
```

**成功路径**：success=true, data 保留原 dict 结构（向后兼容 workflow dispatcher 按字段提取）。
**失败路径**：success=false, message + error_code + recovery_suggestions 三件套给 AI 完整上下文。

**唯一例外**：`screenshot` 工具额外返回 `ImageContent`（base64 PNG），外层 TextContent 用统一格式描述尺寸。

---

## 2. 错误码体系

OmniFlow 定义 **31 个错误码**（E0000-E8002），按模块分段：

| 段 | 模块 | 数量 | 示例 |
|---|---|---|---|
| E0xxx | 通用 | 5 | E0000 UNKNOWN / E0001 INVALID_ARG |
| E1xxx | 窗口 | 4 | E1001 WINDOW_NOT_FOUND |
| E2xxx | 图像 | 4 | E2001 IMAGE_NOT_FOUND |
| E3xxx | OCR | 3 | E3001 OCR_ENGINE_ERROR |
| E4xxx | 键鼠 | 3 | E4001 INPUT_SEND_FAILED |
| E5xxx | 内存 | 4 | E5003 PROCESS_NOT_FOUND |
| E6xxx | 系统 | 3 | E6002 PROGRAM_LAUNCH_FAILED |
| E7xxx | 工作流 | 3 | E7001 WORKFLOW_NOT_FOUND |
| E8xxx | 插件 | 2 | E8001 PLUGIN_NOT_FOUND |

每个错误码都**预置**恢复建议（`RECOVERY_SUGGESTIONS`），在 tool 失败时自动注入到 `recovery_suggestions` 字段。LLM 看到错误码后**立即**知道下一步该做什么。

详细列表和恢复建议在 `src/omniflow/tools/errors.py`。

---

## 3. 工具速查（按功能分组）

### 3.1 窗口类（7 个）

#### `window_find`
- **用途**：按 class_name / title / pid 找窗口
- **参数**：`title` (str) / `class_name` (str) / `pid` (int)，至少一个
- **返回**：`WindowInfo` dict（hwnd, title, class_name, pid, rect, ...）或 null
- **错误码**：`E1001` (WINDOW_NOT_FOUND) / `E1003` (INVALID_HWND)
- **常见组合**：`window_find` → `window_activate` → `bind_window`（后台操作链起点）
- **注意**：title 经常带空格或特殊字符（"游戏名 - 启动器"），用 class_name 更稳

#### `window_enum`
- **用途**：列出所有可见顶层窗口
- **返回**：`[WindowInfo, ...]`
- **错误码**：无（枚举不会失败）
- **常见组合**：先 `window_enum` → 用户挑一个 → `window_find` 锁死
- **AI 提示**：当用户说"列出所有打开的窗口"时优先调这个

#### `window_get_info`
- **用途**：拿窗口的实时信息（位置、是否最小化、parent_hwnd）
- **参数**：`hwnd` (int, 必填)
- **返回**：`WindowInfo`
- **错误码**：`E1001` / `E1003`
- **常见组合**：`window_get_info` → 计算坐标偏移 → 别的工具相对定位

#### `window_set_top`
- **用途**：置顶 / 取消置顶
- **参数**：`hwnd` / `on_top` (bool, 默认 True)
- **返回**：`{"status": "ok"}`
- **典型用法**：调试时让目标窗口永远在最前
- **注意**：置顶窗口的关闭按钮有时被系统任务栏遮挡

#### `window_show`
- **用途**：显示 / 隐藏窗口
- **参数**：`hwnd` / `show` (bool, True=显示 False=隐藏)
- **错误码**：`E1003`
- **vs window_close**：`show=False` 是隐藏（可恢复），`window_close` 是发 WM_CLOSE（真关）

#### `window_activate`
- **用途**：把窗口带到前台（前台化）
- **参数**：`hwnd`
- **错误码**：`E1003`
- **常见组合**：`window_activate` 后才能 `key_type` / `mouse_click`（前台操作）
- **AI 注意**：前台操作会被其他窗口抢焦点，长任务要 bind_window

#### `window_close` ⭐新
- **用途**：发 WM_CLOSE 消息关闭窗口（等同于点 X）
- **参数**：`hwnd`
- **错误码**：`E1003` / `E1004` (WINDOW_CLOSE_FAILED)
- **vs window_show(show=False)**：close 是"真关"（程序收到 OnClose 事件可以保存确认），hide 是"藏起来"
- **典型用法**：关闭已开的子窗口（"前面背包窗口没有关闭"场景）

### 3.2 绑定类（2 个）

#### `bind_window`
- **用途**：把窗口绑定为后台模式（不发前台消息）
- **参数**：`hwnd` (必填) / `display_mode` (gdi/dx/dx2/opengl，默认 gdi) / `mouse_mode` (normal/windows) / `keyboard_mode` (normal/windows)
- **返回**：`{"status": "ok", "bound": bool}`
- **错误码**：`E1002` (WINDOW_BIND_FAILED)
- **4 种 display_mode 选型**（详见 README "绑定模式" 章节）：
  - `gdi`：GDI API 截图，兼容性最好，**默认首选**（普通桌面软件、WPS、画图等）
  - `dx`：DirectX Hook，支持最小化，**游戏**（DirectX 引擎）
  - `dx2`：dx 增强，兼容性更好，dx 失败时尝试
  - `opengl`：OpenGL Hook，支持 OpenGL 游戏
- **4 种 mouse/keyboard_mode 选型**：
  - `normal`：前台模式（窗口必须在前台）
  - `windows`：Windows 消息后台（推荐，几乎所有程序都支持）

#### `unbind_window`
- **用途**：解绑
- **参数**：`hwnd`
- **错误码**：`E1003`
- **典型用法**：切换工作窗口前先 unbind 旧的

### 3.3 图色类（5 个）

#### `screenshot`
- **用途**：截屏（全屏或区域），返回 base64 PNG
- **参数**：`left`/`top`/`right`/`bottom`（区域，省略=全屏）
- **返回**：ImageContent（base64 PNG）+ 统一格式 TextContent（width/height）
- **错误码**：`E2003` (SCREENSHOT_FAILED) / `E2004` (INVALID_REGION)
- **注意**：
  - DPI 缩放下 `get_screen_size` 拿物理像素，不要用 `window_get_info.rect`（那是逻辑像素）
  - 多屏默认截主显示器
  - 截图是同步阻塞（50-200ms），高频场景用 mss 库

#### `find_image`
- **用途**：在屏幕找模板图，返回坐标
- **参数**：`image_path` (必填) / `similarity` (0-1, 默认 0.9) / `left`/`top`/`right`/`bottom`（区域）
- **返回**：`{found, x?, y?, similarity?}`
- **错误码**：`E2001` (IMAGE_NOT_FOUND) / `E2002` (TEMPLATE_LOAD_FAILED)
- **AI 选 similarity 指南**：
  - 0.95+：精确匹配（图标唯一）
  - 0.85-0.95：常规 UI 按钮
  - 0.7-0.85：带 BUFF 特效的游戏、有动画的按钮
- **常见组合**：`screenshot` → `find_image` → `mouse_click`（"找图点击"标准三件套）

#### `find_color`
- **用途**：在区域找颜色（带容差）
- **参数**：`color` (hex "FF0000") / `tolerance` (0-255) / 区域
- **错误码**：`E2001`（没找到）/ `E2004`
- **vs compare_color**：find_color 是"在区域找"，compare_color 是"检查某点"
- **典型用法**：检测 HP 条颜色（满血 vs 残血）→ 触发自动喝药

#### `compare_color`
- **用途**：检查某点像素颜色是否匹配期望
- **参数**：`x`/`y` / `color` (hex) / `tolerance`
- **返回**：`{match: bool}`
- **错误码**：`E0001` (INVALID_ARG)
- **典型用法**：检测状态指示灯（绿灯=在线、红灯=掉线）

#### `get_color`
- **用途**：拿某点像素颜色值
- **参数**：`x`/`y`
- **返回**：`{hex, r, g, b}`
- **常见用法**：调试（"那个按钮是什么颜色"）

### 3.4 OCR 类（3 个）

#### `ocr`
- **用途**：识别区域文字
- **参数**：`left`/`top`/`right`/`bottom`（区域）
- **返回**：`{text: str}`
- **错误码**：`E3001` (OCR_ENGINE_ERROR) / `E3003` (OCR_NOT_INSTALLED)
- **引擎回退链**：Tesseract（需要 pytesseract+训练包）→ EasyOCR（首次下载模型）→ Windows.Media.Ocr（仅英文）
- **注意**：返回的是**一段长文本**，不返回每个词的 bbox。要坐标用 find_image 找文字的图像模板

#### `find_text`
- **用途**：检查区域是否包含指定文字
- **参数**：`text` (必填) / 区域
- **返回**：`{found: bool, text}`（**不返回坐标**）
- **错误码**：`E3002` (TEXT_NOT_FOUND)
- **典型用法**：判断某状态（"是否在登录界面" → 找"登录"文字）

#### `set_ocr_dict`
- **用途**：设置自定义 OCR 字库
- **参数**：`dict_path`（.txt 字符库路径）
- **返回**：`{status, dict_path}`
- **典型用法**：限定识别字符集（只识别数字、英文）→ 提升准确率

### 3.5 键鼠类（9 个）

#### `key_press` / `key_down` / `key_up`
- **用途**：单键操作（press=按下并释放，down=按住，up=释放）
- **参数**：`key`（合法 key 名）
- **错误码**：`E4001` (INPUT_SEND_FAILED) / `E4002` (INVALID_KEY)
- **合法 key 名**：字母数字 / `enter` / `tab` / `esc` / `f1`-`f12` / `ctrl` / `alt` / `shift` / `win` / `space` / `backspace` / 方向键

#### `key_type`
- **用途**：输入字符串
- **参数**：`text` (必填) / `interval` (字间秒数, 默认 0)
- **错误码**：`E4001`
- **AI 提示**：中文输入必须 `interval=0.05`（IME 来不及）；英文可以 `interval=0`

#### `hotkey`
- **用途**：组合键
- **参数**：`keys` (array, 必填)，如 `["ctrl", "s"]`
- **错误码**：`E4001` / `E4002`
- **典型用法**：`hotkey(ctrl+s)` 保存，`hotkey(ctrl+c)` 复制

#### `mouse_move` / `mouse_click` / `mouse_scroll` / `mouse_get_pos`
- **用途**：鼠标操作
- **参数**：`x` / `y` / `duration`（移动耗时）/ `button`（left/right/middle）/ `clicks`（连击数）
- **错误码**：`E4001` / `E4003`（后台操作需要先 bind）
- **AI 注意**：坐标在多屏 / DPI 缩放下可能错位。优先用 find_image 拿坐标，**不**硬编码

### 3.6 内存类（3 个）

#### `mem_read`
- **用途**：读进程内存
- **参数**：`pid` / `address` (10 进制整数) / `size` (字节数, 默认 4)
- **返回**：`{data_hex, size}`
- **错误码**：`E5001` (MEM_READ_FAILED) / `E5003` (PROCESS_NOT_FOUND) / `E5004` (INVALID_ADDRESS)
- **⚠️ 读其他进程内存需要 admin 权限**。读自己进程不需要

#### `mem_write`
- **用途**：写进程内存
- **参数**：`pid` / `address` / `data_hex`（hex 字符串）
- **错误码**：`E5002` (MEM_WRITE_FAILED)
- **⚠️ 写内存可能让目标进程崩溃**——AI 应在用户明确授权下使用

#### `get_module_base`
- **用途**：拿 DLL/EXE 模块基址
- **参数**：`pid` / `module_name`（如 `"kernel32.dll"`）
- **返回**：`{base: int}`（hex 地址的 10 进制表示）
- **典型用法**：基址 + 偏移 = 字段地址（`game.exe+0x1234 = HP 地址`）

### 3.7 系统类（4 个）

#### `get_system_info`
- **用途**：CPU / 内存 / 屏幕 / OS
- **返回**：`{cpu_percent, memory_total_gb, memory_used_gb, screen_width, screen_height, os_version}`
- **错误码**：`E6001`（psutil 缺失 → `pip install psutil`）
- **依赖**：`psutil`

#### `get_screen_size`
- **用途**：物理分辨率
- **返回**：`{width, height}`
- **典型用法**：DPI 缩放下拿真实像素，配合 screenshot 区域参数

#### `enum_process`
- **用途**：枚举有可见窗口的进程
- **限制**：只列有窗口的进程（tray-only 应用漏掉）
- **返回**：`[{pid, name, title, hwnd?}, ...]`
- **错误码**：`E5003`（某进程名拿不到）

#### `run_program` ⭐新
- **用途**：启动外部程序
- **参数**：`program_path`（必填） / `args`（list, 可选） / `cwd`（可选）
- **返回**：`{status, pid?, path}`
- **错误码**：`E6002` (PROGRAM_LAUNCH_FAILED) / `E6003` (PROGRAM_NOT_FOUND)
- **两种模式**：
  - `args=None`：用 `ShellExecute`，自动按 PATH 搜索、识别 .lnk 快捷方式
  - `args=[...]`：用 `subprocess.Popen`，需要传完整命令行参数
- **典型用法**：
  - `run_program("notepad")` —— 启动 notepad
  - `run_program("D:/soft/QQ/QQ.exe", ["-auto"], "D:/soft/QQ")` —— 带参数启动 QQ

### 3.8 工作流类（6 个）

#### `workflow_save`
- **用途**：保存工作流
- **参数**：`name` / `steps`（list of step dicts）
- **返回**：`{id, name, status: "saved"}`
- **错误码**：`E7003` (WORKFLOW_SAVE_FAILED)
- **存储位置**：`~/.omniflow/workflows/{id}.json`（id 是 md5(name)[:12]）

#### `workflow_list`
- **用途**：列出所有工作流
- **返回**：`{workflows: [{id, name, description, step_count}, ...], count}`

#### `workflow_run`
- **用途**：执行工作流（**v2 引擎**——真调 MCP 工具，变量系统、IF/WAIT_FOR_WINDOW 节点、改进 LOOP）
- **参数**：`workflow_id`
- **返回**：`{status, results, context}`
- **错误码**：`E7001` (WORKFLOW_NOT_FOUND) / `E7002` (WORKFLOW_VALIDATION_FAILED) / `E7003`

#### `workflow_pause` / `workflow_resume` / `workflow_delete`
- 标准 CRUD

### 3.9 插件类（5 个）

#### `plugin_list`
- **用途**：列出已安装插件
- **返回**：`[{id, name, enabled, version}, ...]`

#### `plugin_install` / `plugin_uninstall` / `plugin_enable` / `plugin_disable`
- 标准 CRUD
- **错误码**：`E8001` / `E8002`

---

## 4. 典型多 Tool 编排模式

| 任务 | 编排 |
|---|---|
| **找图点击** | `screenshot` → `find_image` → `mouse_move` + `mouse_click` |
| **登录桌面 app** | `window_find` → `window_activate` → `key_type` → `hotkey(enter)` |
| **OCR 提取文字** | `screenshot(区域)` → `ocr(区域)` → LLM 解析 |
| **游戏挂机循环** | `bind_window(dx)` → 循环 `find_image` + `mouse_click` + `key_press` |
| **清空弹窗** | `window_find(每类弹窗)` → 找到就 `key_press(enter)` 或 `window_close` |
| **自动截图保存** | `screenshot` → base64 → PIL 处理 → 保存 |

详见 `examples/workflows/infinite_fish_auto_sell.json`（v2 引擎完整示例）和 `OmniFlow 使用示例.md`（按场景分类的代码示例）。

---

## 5. 设计原则（给 AI 看）

1. **优先用图色**（find_image + screenshot），避免 `mem_read/write`（权限要求 + 崩溃风险）
2. **不要硬编码坐标**——坐标在不同 DPI / 窗口大小下错位；用 find_image 拿坐标
3. **错误后看 recovery_suggestions**——它告诉你下一步该做什么
4. **后台操作前先 bind_window**——避免键鼠被其他窗口抢
5. **多步操作前先 window_get_info** 确认窗口状态

---

## 6. 文档交叉引用

- 完整 API 描述 + 输入 schema：`server.py` 的 `TOOLS` 列表
- 按场景组织的使用示例：`OmniFlow 使用示例.md`
- v2 引擎工作流示例：`examples/workflows/infinite_fish_auto_sell.json`
- 错误码完整列表 + 恢复建议：`src/omniflow/tools/errors.py`
