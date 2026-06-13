# AI Prompt：办公自动化

> 用 OmniFlow 自动化 WPS / Office / 浏览器填表等办公任务。

---

## 📝 通用模板

```
你是办公自动化助手。请用 OmniFlow 工具完成用户的任务。

**操作原则**：
1. WPS/Office 操作前先 window_find + window_activate 切到前台
2. 长时间操作前调 screenshot 看清楚当前布局
3. 中文输入必须用 key_type(text, interval=0.05) 给 IME 留时间
4. 重要操作（保存、提交）后调 screenshot 验证
5. 失败时看 recovery_suggestions 调整

**安全原则**：
- 不修改文件 / 邮件内容（除非用户明确授权）
- 不发送任何消息（除非用户明确授权）
- 不删除任何内容（除非用户明确说"删除"）

**用户任务**：
{{user_task}}
```

---

## 📋 典型场景

### 场景 1：自动填表

```
任务：在 WPS 表格中填入 100 行客户数据。
1. window_find(class_name="TkdxMainWnd", title="客户表")  # WPS 表格窗口
2. window_activate(hwnd)
3. click_image(image_path="templates/cell_a1.png")  # 定位第一个单元格
4. 循环 100 次：
   - key_type(row[i].name, interval=0.05)
   - key_press("tab")
   - key_type(row[i].phone, interval=0.05)
   - key_press("tab")
   - key_type(row[i].email, interval=0.05)
   - key_press("enter")
5. hotkey(ctrl+s) 保存
6. 报告"已填 100 行"
```

### 场景 2：批量重命名 PDF

```
任务：把 D:/docs 下所有 PDF 按"日期_标题"格式重命名。
- 不用 OmniFlow（这是文件操作，不是 GUI 自动化）
- 用 Python 脚本：glob + os.rename + pdf 解析
```

### 场景 3：自动发邮件（需明确授权）

```
任务：发邮件给 5 个收件人，内容是同一封。
⚠️ 必须先确认：
1. 邮件草稿已写好
2. 收件人列表已准备好
3. 用户明确说"发送"

操作：
1. window_find(title="Outlook") / window_activate
2. 找"新建邮件"按钮 → click_image
3. 等新窗口出现
4. key_type(recipient) → key_press(";")
5. key_press("tab") 切到主题
6. key_type(subject)
7. key_press("tab") 切到正文
8. key_type(body, interval=0.05)
9. hotkey(ctrl+enter) 发送
10. 重复
```

### 场景 4：定期截图保存

```
任务：每天 9 点截屏整个桌面，保存到 D:/screenshots/日期.png。
- 用 hermes cron 调度（不是 OmniFlow）
- cron job: 0 9 * * * → 跑 python 脚本调 screenshot()
```

---

## 🛡️ 安全护栏

**重要操作前必须确认**：
- ✏️ 修改 / 覆盖文件
- ✉️ 发送消息（邮件 / IM / 社交媒体）
- 💰 涉及支付的任何操作（即使有"已读确认"）
- 🗑️ 删除文件 / 数据库记录
- 🔓 提交代码 / push git

**错误码速查（办公相关）**：
- `E1001` 窗口找不到 → 程序关了 / 切到别的窗口
- `E3001` OCR 失败 → 没装 OCR 引擎 / 中文需要 chi_sim 包
- `E4002` INVALID_KEY → 用了不合法 key 名（参考 MCP_TOOLS_REFERENCE 合法集）

---

## 💡 性能建议

- **大表格**填入：用 `key_type` 慢（每字段 100ms），考虑用 `pyperclip` 复制 + `key_press(ctrl+v)` 粘贴（快 10 倍）
- **多窗口切换**：每次切窗口先 `window_activate` + `screenshot` 验证
- **后台任务**：用 `hermes cron` 调度，不阻塞当前 session
