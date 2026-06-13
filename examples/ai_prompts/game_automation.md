# AI Prompt：游戏自动化

> 让 AI 通过 OmniFlow 自动化游戏的参考 Prompt 模板。
> ⚠️ **先看游戏 ToS**——禁止内存作弊、禁止严重破坏游戏经济。

---

## 🎮 通用模板

```
你是游戏自动化助手。请用 OmniFlow 工具（mcp__omniflow__*）完成用户任务。

**操作原则**：
1. 优先用图色识别（find_image / ocr），不要用 mem_read/write（容易触发反作弊）
2. 后台操作前先调 detect_bind_mode(hwnd) 找最佳 mode，再用 bind_window
3. 长时间操作前先调 screenshot 看清楚当前画面
4. 错误时看 recovery_suggestions 字段，按建议调整

**禁止**：
- 不得用 mem_read / mem_write 修改游戏内存（违反 ToS）
- 不得绕过反作弊机制
- 不得执行破坏游戏经济的批量操作（如自动交易、自动 PK）

**用户任务**：
{{user_task}}
```

---

## 🎯 典型场景

### 场景 1：挂机打怪（合规）

```
任务：用 OmniFlow 自动循环打怪，每 30 秒一次。
- bind_window 后台模式（gdi，兼容性最好）
- find_image 找怪物图标（templates/monster.png）
- 找到就 mouse_click 攻击
- 等 1s
- 找"拾取"按钮（templates/loot.png）→ 点击
- 循环
- 每 5 分钟保存一次（hotkey ctrl+s）
```

### 场景 2：检测 HP 自动喝药

```
任务：监控血量条，低于 30% 自动喝药。
- find_color 在 HP 条区域（x=200, y=850, w=300, h=10）检测红色
- 如果 HP < 30%（红色像素 < 50%）→ 按键 1（吃红药）
- 如果 HP < 10% → 按键 2（吃大药）+ 退出战斗（按 esc）
- 循环监控
```

### 场景 3：自动登录

```
任务：游戏启动后自动登录。
1. wait_for_window(class_name="LoginForm", timeout=30)
2. key_type("username", interval=0.05) → key_press("tab") → key_type("password", interval=0.05)
3. key_press("enter")
4. wait_for_window(class_name="GameMain", timeout=10) 等主界面
5. 报告"登录成功"
```

---

## ⚠️ 反作弊避坑

| 行为 | 风险 | 替代 |
|---|---|---|
| `mem_read` 读金币/血量 | **高**（特征码扫描）| `find_color` / `screenshot` 像素判断 |
| `mem_write` 改 HP = 0 | **极高**（秒杀挂）| **禁止** |
| 极快点击（<50ms 间隔）| 中（频率检测）| `interval=0.1` 以上 |
| 长时间挂机（>24h） | 低 | 每小时主动移动一次 |
| 跨区传送 | 中 | 模拟正常走路路径 |
| 重复相同坐标点击 | 低 | find_image 比坐标更"人类" |

---

## 📚 错误码速查（游戏相关）

- `E1001` WINDOW_NOT_FOUND → 游戏没启动 / 切到后台了
- `E2001` IMAGE_NOT_FOUND → 改主题了 / 角色换了皮肤 → 重新截图
- `E5001` MEM_READ_FAILED → 反作弊拦截 → **改用图色**！
- `E4001` INPUT_SEND_FAILED → 没 bind_window → 重新 bind
