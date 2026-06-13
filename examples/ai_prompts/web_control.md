# AI Prompt：浏览器控制

> ⚠️ **优先用 `browser` MCP / `web_extract`，不用 OmniFlow！**
> 浏览器控制有专门的工具（headless / 远程控制），速度快 10 倍以上。
> OmniFlow 驱动桌面浏览器只用于**没 headless 替代**的极端场景。

---

## 🌐 何时用 OmniFlow 控制浏览器

✅ **用 OmniFlow**：
- 桌面浏览器内的 flash / silverlight / 老 ActiveX 控件（headless 跑不了）
- 必须用真鼠标轨迹通过的人机识别（rare）
- 浏览器内嵌的 Windows 控件（"另存为"对话框等）

❌ **不要用 OmniFlow**（用 browser MCP / web_extract）：
- 普通网页爬取 → `web_extract`
- 网页自动化测试 → `browser` MCP (Playwright)
- 表单填写 → `browser` MCP
- 截图 → `browser` MCP
- JavaScript 渲染 → `browser` MCP

---

## 📋 通用模板

```
你是浏览器控制助手。**优先用 browser MCP / web_extract**——只有当目标
不可 headless 时才用 OmniFlow。

**用户任务**：
{{user_task}}
```

---

## 🎯 典型场景

### 场景 1：网页爬取（**不要用 OmniFlow**）

```
✅ 正确：用 web_extract
- web_extract(urls=["https://example.com/page1", "https://example.com/page2"])
- LLM 解析返回的 markdown

❌ 错误：用 OmniFlow 驱动 Chrome
- screenshot → ocr → 解析（慢 100 倍，容易出错）
```

### 场景 2：表单填写（**不要用 OmniFlow**）

```
✅ 正确：用 browser MCP
- browser_navigate(url)
- browser_fill(selector="#username", value="alice")
- browser_click(selector="#submit")
- browser_screenshot()

❌ 错误：用 OmniFlow 找输入框
- find_image("username_field.png") 找输入框（脆弱）
- mouse_click → key_type（容易错位）
```

### 场景 3：Chrome 内 Flash 控件（**用 OmniFlow**）

```
任务：控制 Chrome 里的 Flash 视频播放器。

1. window_find(class_name="Chrome_WidgetWin_1", title="Flash Video")
2. bind_window(hwnd, display_mode="gdi")
3. mouse_click(play_button_x, play_button_y)  # 找按钮图
4. 找进度条 → 拖到末尾 → 下一集
```

### 场景 4：浏览器内嵌"另存为"对话框

```
任务：网页下载文件，触发"另存为"对话框，指定保存路径。

1. browser_click(下载链接)  # 触发系统对话框
2. wait_for_window(class_name="#32770", title="另存为", timeout=5)
3. key_type(filepath, interval=0.05)
4. key_press(enter)
5. wait_for_window(class_name="#32770", title="下载完成", timeout=30)  # 等待完成
6. key_press(enter)
```

---

## 🛡️ 安全 / 限制

- **不要**用 OmniFlow 做大量网页爬取（headless 工具更快）
- **不要**用 OmniFlow 模拟真人点击（网站反作弊可能检测到 SendInput 模式）
- **不要**绕过验证码（除非用户明确说"我手动填了验证码，继续"）
- **优先**用 browser MCP 的 `browser_evaluate(js)` 跑 JS 提取数据（比 OCR 快 100 倍）

---

## 💡 调试

| 现象 | 原因 | 解决 |
|---|---|---|
| OmniFlow 点击 Chrome 没反应 | 用了前台模式但 Chrome 不在前台 | `bind_window` 后台模式 |
| 截图看不清文字 | DPI 缩放 / 高分屏 | `get_screen_size` 拿真实像素，按像素截 |
| 浏览器窗口类名变了 | Chrome 版本更新 | `window_enum` 重新看类名 |
| 网页元素位置变了 | 网页响应式布局 | 改用 browser MCP（DOM selector）|
