# AI Prompt：图像处理自动化

> 用 OmniFlow 驱动 PS / AI / mspaint 做图片处理流水线。

---

## 🎨 通用模板

```
你是图像处理助手。请用 OmniFlow 工具完成用户的图片处理任务。

**操作原则**：
1. PS/AI 操作前先 window_activate 切到前台
2. 复杂操作优先用 PS 自带批处理（File → Scripts → Image Processor），
   OmniFlow 只做"调度者"，不循环单图操作
3. mspaint 只用于"画给人看的中间产物"（箭头、标注），
   真正的图像生成应该用 PIL
4. 模板图从当前主题截，不要硬编码坐标

**用户任务**：
{{user_task}}
```

---

## 🖼️ 典型场景

### 场景 1：批量缩放 + 加水印

```
任务：把 50 张 4K 图片缩放到 1920x1080 + 加"© 2026 My Brand"水印。

**推荐方案**（不要用 OmniFlow 循环）：
1. 在 PS 录制一个 Action：
   - File → Automate → Batch
   - 录制 Image Size → 1920x1080
   - 录制文字水印
2. 用 OmniFlow 调：
   - run_program(Photoshop.exe)
   - wait_for_window(class_name="Photoshop", timeout=30)
   - hotkey(ctrl+alt+i) → key_type("1920") → key_press("tab") → key_type("1080") → key_press(enter)
   - hotkey(ctrl+shift+alt+s) 触发 Export
   - 选目标文件夹

❌ 不要：50 次循环 find_image + click_image
✅ 正确：让 PS 自己批处理
```

### 场景 2：截图 → 标注 → 回写

```
任务：截全屏，标红框 + 文字"重点"，保存为 PNG。

用 PIL 在内存里处理（不要 OmniFlow 驱动 mspaint）：
1. screenshot() 拿 base64
2. PIL.Image.open(BytesIO(b64decode(b64)))
3. ImageDraw.Draw(img).rectangle((x, y, x+w, y+h), outline="red", width=3)
4. ImageDraw.Draw(img).text((x, y+h+10), "重点", fill="red")
5. PIL 保存为 annotated.png
```

### 场景 3：mspaint 画流程图

```
任务：在 mspaint 画一个流程图：圆角矩形 + 箭头 + 文字。

1. run_program("mspaint")
2. wait_for_window(class_name="MSPaintApp", timeout=5)
3. hotkey("r") 选矩形工具
4. mouse_drag(x1, y1, x2, y2) 画矩形
5. hotkey("t") 选文字工具
6. mouse_drag 创建文字框
7. key_type("步骤 1", interval=0.05)
8. mouse_click(画布外) 退出文字编辑
9. 重复画其他元素
10. hotkey(ctrl+s) 保存
```

### 场景 4：OCR 提取截图中的文字

```
任务：把 5 张截图里的文字提取出来汇总成表格。

1. 对每张图：
   a. screenshot 或读图 → base64
   b. OCR（识别整图或指定区域）
   c. LLM 解析
2. 合并为表格
3. 保存为 CSV
```

---

## ⚠️ 性能 / 精度

| 需求 | 工具 |
|---|---|
| 1 张图处理 | OmniFlow 截屏 + PIL |
| 10-100 张批量 | PS Action + Image Processor |
| 1000+ 张 | PS Action + Image Processor Pro（GPU）|
| 实时识别（>5fps）| mss 库 + OpenCV |
| 高精度 OCR | Tesseract + chi_sim 训练包 |

---

## 🐛 常见坑

- **PS 各版本 UI 差异大**：模板图必须从**当前 PS 版本**截，跨版本不通用
- **录制 Action 是"原子操作"**：不污染 Ctrl+Z 历史；OmniFlow 触发的"播放 Action"完全可重放
- **mspaint 不支持矢量输出**：要 SVG/PDF 就别用 mspaint
- **截图带光标**：先 `mouse_move(0, 0)` 把光标藏到角落，再截图
