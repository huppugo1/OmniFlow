# OmniFlow MCP Tools リファレンス

> 完全な 43 個の MCP Tool の使用シナリオ、パラメータ、返却値、エラーコード、一般的な組み合わせ。

---

## 1. 統一返却フォーマット

すべての Tool 呼び出しは JSON で **統一フォーマット** を返却します：

```json
{
  "success": true,
  "data": { ... },                  // 元の tool 返却（フィールド保持）
  "message": "ok",                  // 人間が読める形式
  "error_code": null,               // エラーコード（成功時は null）
  "recovery_suggestions": []       // エラー時に回復提案を埋め込む
}
```

**成功パス**：success=true、data は元の dict 構造を保持（ワークフローディスパッチャーのフィールド抽出との後方互換性）。
**失敗パス**：success=false、message + error_code + recovery_suggestions の三つ組で AI に完全なコンテキストを提供。

**唯一の例外**：`screenshot` ツールは追加で `ImageContent`（base64 PNG）を返却し、外側の TextContent は統一フォーマットでサイズを記述。

---

## 2. エラーコード体系

OmniFlow は **31 個のエラーコード**（E0000-E8002）を定義し、モジュールごとにセグメント化：

| セグメント | モジュール | 数 | 例 |
|---|---|---|---|
| E0xxx | 汎用 | 5 | E0000 UNKNOWN / E0001 INVALID_ARG |
| E1xxx | ウィンドウ | 4 | E1001 WINDOW_NOT_FOUND |
| E2xxx | 画像 | 4 | E2001 IMAGE_NOT_FOUND |
| E3xxx | OCR | 3 | E3001 OCR_ENGINE_ERROR |
| E4xxx | 入力 | 3 | E4001 INPUT_SEND_FAILED |
| E5xxx | メモリ | 4 | E5003 PROCESS_NOT_FOUND |
| E6xxx | システム | 3 | E6002 PROGRAM_LAUNCH_FAILED |
| E7xxx | ワークフロー | 3 | E7001 WORKFLOW_NOT_FOUND |
| E8xxx | プラグイン | 2 | E8001 PLUGIN_NOT_FOUND |

各エラーコードには**事前設定された**回復提案（`RECOVERY_SUGGESTIONS`）があり、tool 失敗時に自動的に `recovery_suggestions` フィールドに注入されます。LLM はエラーコードを見て**即座に**次に何をすべきかを知ります。

詳細リストと回復提案は `src/omniflow/tools/errors.py` にあります。

---

## 3. ツールクイックリファレンス（機能別グループ）

### 3.1 ウィンドウ系（7 個）

#### `window_find`
- **用途**：class_name / title / pid でウィンドウを検索
- **パラメータ**：`title` (str) / `class_name` (str) / `pid` (int)、少なくとも 1 つ必須
- **返却**：`WindowInfo` dict（hwnd, title, class_name, pid, rect, ...）または null
- **エラーコード**：`E1001` (WINDOW_NOT_FOUND) / `E1003` (INVALID_HWND)
- **一般的な組み合わせ**：`window_find` → `window_activate` → `bind_window`（バックグラウンド操作チェーンの起点）
- **注意**：title は頻繁にスペースや特殊文字を含む（"ゲーム名 - ランチャー"）、class_name の方が安定

#### `window_enum`
- **用途**：すべての可視トップレベルウィンドウを一覧表示
- **返却**：`[WindowInfo, ...]`
- **エラーコード**：なし（列挙は失敗しない）
- **一般的な組み合わせ**：まず `window_enum` → ユーザーが選択 → `window_find` で固定
- **AI ヒント**：ユーザーが「開いているウィンドウをすべて一覧表示」と言った場合に優先的に使用

#### `window_get_info`
- **用途**：ウィンドウのリアルタイム情報を取得（位置、最小化状態、parent_hwnd）
- **パラメータ**：`hwnd` (int, 必須)
- **返却**：`WindowInfo`
- **エラーコード**：`E1001` / `E1003`
- **一般的な組み合わせ**：`window_get_info` → 座標オフセット計算 → 他のツールで相対位置決め

#### `window_set_top`
- **用途**：最前面化 / 最前面解除
- **パラメータ**：`hwnd` / `on_top` (bool, デフォルト True)
- **返却**：`{"status": "ok"}`
- **典型的な使用法**：デバッグ時に対象ウィンドウを常に前面に保持
- **注意**：最前面ウィンドウの閉じるボタンがシステムタスクバーに遮られることがある

#### `window_show`
- **用途**：表示 / 非表示
- **パラメータ**：`hwnd` / `show` (bool, True=表示 False=非表示)
- **エラーコード**：`E1003`
- **vs window_close**：`show=False` は非表示（復元可能）、`window_close` は WM_CLOSE を送信（実際に閉じる）

#### `window_activate`
- **用途**：ウィンドウをフォアグラウンドに持ってくる
- **パラメータ**：`hwnd`
- **エラーコード**：`E1003`
- **一般的な組み合わせ**：`window_activate` 後に `key_type` / `mouse_click`（フォアグラウンド操作）
- **AI 注意**：フォアグラウンド操作は他のウィンドウにフォーカスを奪われる可能性がある、長時間タスクには bind_window が必要

#### `window_close` ⭐新機能
- **用途**：WM_CLOSE メッセージを送信してウィンドウを閉じる（X をクリックするのと同等）
- **パラメータ**：`hwnd`
- **エラーコード**：`E1003` / `E1004` (WINDOW_CLOSE_FAILED)
- **vs window_show(show=False)**：close は「実際に閉じる」（プログラムは OnClose イベントを受信し保存確認が可能）、hide は「隠す」
- **典型的な使用法**：開いている子ウィンドウを閉じる（「前のバックパックウィンドウが閉じていない」シナリオ）

### 3.2 バインド系（2 個）

#### `bind_window`
- **用途**：ウィンドウをバックグラウンドモードにバインド（フォアグラウンドメッセージを送信しない）
- **パラメータ**：`hwnd` (必須) / `display_mode` (gdi/dx/dx2/opengl, デフォルト gdi) / `mouse_mode` (normal/windows) / `keyboard_mode` (normal/windows)
- **返却**：`{"status": "ok", "bound": bool}`
- **エラーコード**：`E1002` (WINDOW_BIND_FAILED)
- **4 種類の display_mode オプション**（README の「バインドモード」章を参照）：
  - `gdi`：GDI API スクリーンショット、最も互換性が高い、**デフォルトの第一選択**（一般的なデスクトップソフトウェア、WPS、ペイントなど）
  - `dx`：DirectX Hook、最小化をサポート、**ゲーム**（DirectX エンジン）
  - `dx2`：dx 強化、より互換性が高い、dx 失敗時に試行
  - `opengl`：OpenGL Hook、OpenGL ゲームをサポート
- **4 種類の mouse/keyboard_mode オプション**：
  - `normal`：フォアグラウンドモード（ウィンドウが最前面に必要）
  - `windows`：Windows メッセージバックグラウンド（推奨、ほぼすべてのプログラムがサポート）

#### `unbind_window`
- **用途**：アンバインド
- **パラメータ**：`hwnd`
- **エラーコード**：`E1003`
- **典型的な使用法**：作業ウィンドウを切り替える前に古いものをアンバインド

### 3.3 画像/色系（5 個）

#### `screenshot`
- **用途**：スクリーンショット（フルスクリーンまたは領域）、base64 PNG を返却
- **パラメータ**：`left`/`top`/`right`/`bottom`（領域、省略=フルスクリーン）
- **返却**：ImageContent（base64 PNG）+ 統一フォーマット TextContent（width/height）
- **エラーコード**：`E2003` (SCREENSHOT_FAILED) / `E2004` (INVALID_REGION)
- **注意**：
  - DPI スケーリング下では物理ピクセルに `get_screen_size` を使用、`window_get_info.rect` は論理ピクセルなので使用しない
  - マルチスクリーンはデフォルトでメインモニタ
  - スクリーンショットは同期ブロッキング（50-200ms）、高頻度シナリオでは mss ライブラリを使用

#### `find_image`
- **用途**：画面でテンプレート画像を探し、座標を返却
- **パラメータ**：`image_path` (必須) / `similarity` (0-1, デフォルト 0.9) / `left`/`top`/`right`/`bottom`（領域）
- **返却**：`{found, x?, y?, similarity?}`
- **エラーコード**：`E2001` (IMAGE_NOT_FOUND) / `E2002` (TEMPLATE_LOAD_FAILED)
- **AI similarity 選択ガイド**：
  - 0.95+：正確一致（ユニークなアイコン）
  - 0.85-0.95：通常の UI ボタン
  - 0.7-0.85：BUFF エフェクトのあるゲーム、アニメーション付きボタン
- **一般的な組み合わせ**：`screenshot` → `find_image` → `mouse_click`（「画像検索クリック」標準トリオ）

#### `find_color`
- **用途**：領域内で色を探す（許容範囲付き）
- **パラメータ**：`color` (hex "FF0000") / `tolerance` (0-255) / 領域
- **エラーコード**：`E2001`（見つからない）/ `E2004`
- **vs compare_color**：find_color は「領域内で探す」、compare_color は「特定の点を確認」
- **典型的な使用法**：HP バーの色を検出（満タン vs 残りわずか）→ 自動ポーション飲みをトリガー

#### `compare_color`
- **用途**：特定の点のピクセル色が期待と一致するか確認
- **パラメータ**：`x`/`y` / `color` (hex) / `tolerance`
- **返却**：`{match: bool}`
- **エラーコード**：`E0001` (INVALID_ARG)
- **典型的な使用法**：状態インジケータライトを検出（緑=オンライン、赤=オフライン）

#### `get_color`
- **用途**：特定の点のピクセル色値を取得
- **パラメータ**：`x`/`y`
- **返却**：`{hex, r, g, b}`
- **一般的な使用法**：デバッグ（「そのボタンは何色か」）

### 3.4 OCR 系（3 個）

#### `ocr`
- **用途**：領域内のテキストを認識
- **パラメータ**：`left`/`top`/`right`/`bottom`（領域）
- **返却**：`{text: str}`
- **エラーコード**：`E3001` (OCR_ENGINE_ERROR) / `E3003` (OCR_NOT_INSTALLED)
- **エンジンフォールバックチェーン**：Tesseract（pytesseract+トレーニングパッケージが必要）→ EasyOCR（初回使用時にモデルをダウンロード）→ Windows.Media.Ocr（英語のみ）
- **注意**：**長いテキスト**を返却し、各単語の bbox は返さない。座標が必要な場合は find_image でテキスト画像テンプレートを探す

#### `find_text`
- **用途**：領域に指定されたテキストが含まれているか確認
- **パラメータ**：`text` (必須) / 領域
- **返却**：`{found: bool, text}`（**座標は返さない**）
- **エラーコード**：`E3002` (TEXT_NOT_FOUND)
- **典型的な使用法**：状態を判断（"ログイン画面か" → "ログイン" テキストを探す）

#### `set_ocr_dict`
- **用途**：カスタム OCR フォントライブラリを設定
- **パラメータ**：`dict_path`（.txt 文字ライブラリのパス）
- **返却**：`{status, dict_path}`
- **典型的な使用法**：認識文字セットを限定（数字、英語のみ）→ 精度向上

### 3.5 キーボード/マウス系（9 個）

#### `key_press` / `key_down` / `key_up`
- **用途**：単一キー操作（press=押して離す、down=長押し、up=解放）
- **パラメータ**：`key`（有効なキー名）
- **エラーコード**：`E4001` (INPUT_SEND_FAILED) / `E4002` (INVALID_KEY)
- **有効なキー名**：英数字 / `enter` / `tab` / `esc` / `f1`-`f12` / `ctrl` / `alt` / `shift` / `win` / `space` / `backspace` / 方向キー

#### `key_type`
- **用途**：文字列を入力
- **パラメータ**：`text` (必須) / `interval` (文字間秒数, デフォルト 0)
- **エラーコード**：`E4001`
- **AI ヒント**：日本語/中国語入力には `interval=0.05` が必須（IME が間に合わない）；英語は `interval=0` で可

#### `hotkey`
- **用途**：コンビネーションキー
- **パラメータ**：`keys` (配列, 必須)、例：`["ctrl", "s"]`
- **エラーコード**：`E4001` / `E4002`
- **典型的な使用法**：`hotkey(ctrl+s)` で保存、`hotkey(ctrl+c)` でコピー

#### `mouse_move` / `mouse_click` / `mouse_scroll` / `mouse_get_pos`
- **用途**：マウス操作
- **パラメータ**：`x` / `y` / `duration`（移動時間）/ `button`（left/right/middle）/ `clicks`（連続クリック数）
- **エラーコード**：`E4001` / `E4003`（バックグラウンド操作には事前にバインドが必要）
- **AI 注意**：マルチスクリーン / DPI スケーリング下で座標がずれる可能性がある。座標には find_image を優先的に使用し、**ハードコードしない**

### 3.6 メモリ系（3 個）

#### `mem_read`
- **用途**：プロセスメモリを読み取る
- **パラメータ**：`pid` / `address` (10 進数整数) / `size` (バイト数, デフォルト 4)
- **返却**：`{data_hex, size}`
- **エラーコード**：`E5001` (MEM_READ_FAILED) / `E5003` (PROCESS_NOT_FOUND) / `E5004` (INVALID_ADDRESS)
- **⚠️ 他のプロセスのメモリ読み取りには管理者権限が必要**。自分自身のプロセスの読み取りには不要

#### `mem_write`
- **用途**：プロセスメモリに書き込む
- **パラメータ**：`pid` / `address` / `data_hex`（hex 文字列）
- **エラーコード**：`E5002` (MEM_WRITE_FAILED)
- **⚠️ メモリ書き込みは対象プロセスをクラッシュさせる可能性があります** — AI はユーザーの明示的な承認の下で使用すべき

#### `get_module_base`
- **用途**：DLL/EXE モジュールのベースアドレスを取得
- **パラメータ**：`pid` / `module_name`（例：`"kernel32.dll"`）
- **返却**：`{base: int}`（hex アドレスの 10 進数表現）
- **典型的な使用法**：ベースアドレス + オフセット = フィールドアドレス（`game.exe+0x1234 = HP アドレス`）

### 3.7 システム系（4 個）

#### `get_system_info`
- **用途**：CPU / メモリ / 画面 / OS
- **返却**：`{cpu_percent, memory_total_gb, memory_used_gb, screen_width, screen_height, os_version}`
- **エラーコード**：`E6001`（psutil 不足 → `pip install psutil`）
- **依存関係**：`psutil`

#### `get_screen_size`
- **用途**：物理解像度
- **返却**：`{width, height}`
- **典型的な使用法**：DPI スケーリング下で実際のピクセルを取得、スクリーンショット領域パラメータと組み合わせて使用

#### `enum_process`
- **用途**：可視ウィンドウを持つプロセスを列挙
- **制限**：ウィンドウを持つプロセスのみを一覧表示（tray-only アプリケーションは除外）
- **返却**：`[{pid, name, title, hwnd?}, ...]`
- **エラーコード**：`E5003`（一部のプロセス名を取得できない）

#### `run_program` ⭐新機能
- **用途**：外部プログラムを起動
- **パラメータ**：`program_path` (必須) / `args` (リスト, オプション) / `cwd` (オプション)
- **返却**：`{status, pid?, path}`
- **エラーコード**：`E6002` (PROGRAM_LAUNCH_FAILED) / `E6003` (PROGRAM_NOT_FOUND)
- **2 つのモード**：
  - `args=None`：`ShellExecute` を使用、PATH による自動検索、.lnk ショートカットの認識
  - `args=[...]`：`subprocess.Popen` を使用、フルコマンドラインパラメータが必要
- **典型的な使用法**：
  - `run_program("notepad")` —— メモ帳を起動
  - `run_program("D:/soft/QQ/QQ.exe", ["-auto"], "D:/soft/QQ")` —— パラメータ付きで QQ を起動

### 3.8 ワークフロー系（6 個）

#### `workflow_save`
- **用途**：ワークフローを保存
- **パラメータ**：`name` / `steps`（step dict のリスト）
- **返却**：`{id, name, status: "saved"}`
- **エラーコード**：`E7003` (WORKFLOW_SAVE_FAILED)
- **保存場所**：`~/.omniflow/workflows/{id}.json`（id は md5(name)[:12]）

#### `workflow_list`
- **用途**：すべてのワークフローを一覧表示
- **返却**：`{workflows: [{id, name, description, step_count}, ...], count}`

#### `workflow_run`
- **用途**：ワークフローを実行（**v2 エンジン** — 実際の MCP ツール呼び出し、変数システム、IF/WAIT_FOR_WINDOW ノード、改善された LOOP）
- **パラメータ**：`workflow_id`
- **返却**：`{status, results, context}`
- **エラーコード**：`E7001` (WORKFLOW_NOT_FOUND) / `E7002` (WORKFLOW_VALIDATION_FAILED) / `E7003`

#### `workflow_pause` / `workflow_resume` / `workflow_delete`
- 標準 CRUD

### 3.9 プラグイン系（5 個）

#### `plugin_list`
- **用途**：インストール済みプラグインを一覧表示
- **返却**：`[{id, name, enabled, version}, ...]`

#### `plugin_install` / `plugin_uninstall` / `plugin_enable` / `plugin_disable`
- 標準 CRUD
- **エラーコード**：`E8001` / `E8002`

---

## 4. 典型的なマルチツールオーケストレーションパターン

| タスク | オーケストレーション |
|---|---|
| **画像検索クリック** | `screenshot` → `find_image` → `mouse_move` + `mouse_click` |
| **デスクトップアプリにログイン** | `window_find` → `window_activate` → `key_type` → `hotkey(enter)` |
| **OCR テキスト抽出** | `screenshot(領域)` → `ocr(領域)` → LLM 解析 |
| **ゲームバックグラウンドループ** | `bind_window(dx)` → ループ `find_image` + `mouse_click` + `key_press` |
| **ポップアップをクリア** | `window_find(各ポップアップタイプ)` → 発見時に `key_press(enter)` または `window_close` |
| **自動スクリーンショット保存** | `screenshot` → base64 → PIL 処理 → 保存 |

`examples/workflows/infinite_fish_auto_sell.json`（v2 エンジン完全例）と `OmniFlow 使用示例.md`（シナリオ別コード例）を参照。

---

## 5. 設計原則（AI 向け）

1. **画像/色を優先的に使用**（find_image + screenshot）、`mem_read/write` は避ける（権限要件 + クラッシュリスク）
2. **座標をハードコードしない** — 異なる DPI / ウィンドウサイズ下で座標がずれる；find_image で座標を取得
3. **エラー後に recovery_suggestions を確認** — 次に何をすべきかを教えてくれる
4. **バックグラウンド操作前に bind_window** — キーボード/マウスが他のウィンドウに奪われるのを防ぐ
5. **多段操作前に window_get_info** でウィンドウ状態を確認

---

## 6. ドキュメント相互参照

- 完全な API 説明 + 入力スキーマ：`server.py` の `TOOLS` リスト
- シナリオ別の使用例：`OmniFlow 使用示例.md`
- v2 エンジンワークフロー例：`examples/workflows/infinite_fish_auto_sell.json`
- 完全なエラーコードリスト + 回復提案：`src/omniflow/tools/errors.py`
