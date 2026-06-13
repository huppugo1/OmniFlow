# OmniFlow AI 統合ガイド

> AI クライアント（Claude Desktop / Cursor / Windsurf / Hermes / Claude Code）が OmniFlow を正しく使用するための実践ガイド。

---

## 1. MCP クライアント設定

OmniFlow は **stdio プロトコル**を通じて MCP クライアントと通信します。設定の本質は「クライアントに OmniFlow サーバーの起動方法を伝える」ことです。

### 1.1 汎用設定テンプレート

```json
{
  "mcpServers": {
    "omniflow": {
      "command": "<venv-python>",
      "args": ["-m", "omniflow"],
      "cwd": "<ローカルの OmniFlow リポジトリパス>"
    }
  }
}
```

| フィールド | 説明 |
|---|---|
| `command` | venv 内の `python.exe` の絶対パス（システムの `python` は**使用しない** — omniflow パッケージが見つからない） |
| `args` | `["-m", "omniflow"]`（モジュールとして実行、事前に `pip install -e .` が**必須**） |
| `cwd` | OmniFlow リポジトリのルートディレクトリ（一部クライアントがサポート、例：Hermes） |

### 1.2 各クライアントの設定ファイル場所

| クライアント | 設定ファイル場所 |
|---|---|
| **Hermes** | `~/.hermes/config.yaml` の `mcp.servers.omniflow` セクション（`hermes mcp add omniflow ...` コマンドで管理） |
| **Claude Desktop** | Windows: `%APPDATA%\Claude\claude_desktop_config.json`<br>macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Cursor** | Settings → MCP → Add new global MCP server |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **VS Code + Continue** | `.continue/config.json` の `experimental.mcpServers` セクション |
| **Cline** | VS Code 設定 → Cline → MCP Servers |

### 1.3 Hermes 推奨設定

```bash
# hermes mcp add で登録（最も安定）
hermes mcp add omniflow \
  --command "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe" \
  --args "-m" "omniflow"
```

または**手動編集** `~/.hermes/config.yaml`：
```yaml
mcp:
  servers:
    omniflow:
      command: "F:/woker/OmniFlow/.venv-omniflow/Scripts/python.exe"
      args: ["-m", "omniflow"]
```

### 1.4 設定の検証

クライアント起動後、**`mcp__omniflow__get_screen_size()` で接続テスト** — `{"width": 1920, "height": 1080}` が返れば OK。

---

## 2. Prompt ベストプラクティス

### 2.1 AI に正しい Tool を選ばせる

**❌ 悪い Prompt**：
> "PC を操作して"

AI はどの Tool から始めるべきかわかりません。

**✅ 良い Prompt**：
> "画面右下（座標 1800, 1000）のボタンをクリックしてください。ボタンは白背景に青い角丸長方形です"

AI は `screenshot` で画面確認 + `find_image` でボタン検索 + `mouse_click` でクリックと理解します。

### 2.2 AI に `recovery_suggestions` を積極的に確認させる

**❌ 悪い Prompt**：
> "「確定」ボタンを探して"

ボタンが見つからない場合、AI は**同じ Tool を繰り返し試行**し、時間を浪費します。

**✅ 良い Prompt**：
> "「確定」ボタンを探してください。見つからない場合は、まず `recovery_suggestions` に従って similarity 閾値を調整；それでも見つからない場合はスクリーンショットを撮って見せて"

AI は `recovery_suggestions` フィールドを**積極的に**確認し、提案に従って戦略を調整します。

### 2.3 明確な境界を定義する

**❌ 危険な Prompt**：
> "ゲームの HP を 0 に変更して"

AI が**メモリ改変**を行う可能性があります（法的リスク）。

**✅ 安全な Prompt**：
> "スクリーンショット + find_image で HP バーを探し、HP < 30% の時に自動でキーを押してポーションを飲む。**`mem_*` ツールは使用しない**"

AI に GUI 自動化のパスを明示的に指定し、**メモリ改変は行わない**ようにします。

### 2.4 AI に既存の Tool を再利用させ、新しい Tool を発明させない

ユーザーの prompt が曖昧な場合、AI は新しいツールのインストールを**提案**する可能性があります。**AI に既存の Tool を優先使用するよう導きます**：

> "OmniFlow の既存ツールでこのタスクを完了してください。**新しいソフトウェアのインストールを提案しないで**"

### 2.5 AI に複合 Tool を使用させ、単体 Tool を使用させない

**❌ 悪い Prompt**：
> "「確定」ボタンを探して、マウスを移動してクリックして"

AI は `find_image` + `mouse_move` + `mouse_click` の 3 ステップを使用します。

**✅ 良い Prompt**：
> "「確定」ボタンをクリックして"

AI は `click_image` 複合 Tool を認識し、優先的に使用します（1 ステップ完了）。

---

## 3. 典型的なタスクフロー（AI が Tool をオーケストレーションする方法）

### 3.1 タスク：ボタンの自動クリック

```
✅ 推奨フロー：
1. click_image(image_path="templates/btn.png", similarity=0.9)
2. clicked=False の場合、wait_and_click で再試行（より長い timeout）
3. それでも失敗の場合、recovery_suggestions に従って similarity を調整、またはユーザーにスクリーンショットを見せる

❌ こうしないで：
1. find_image → 座標取得 → mouse_move → mouse_click（4 ステップ、click_image の 1 ステップに劣る）
```

### 3.2 タスク：特定のインターフェースの出現を待つ

```
✅ 推奨：
1. wait_and_click(image_path="templates/loaded.png", timeout=30, poll_interval=1)
   （画像が出現したらクリック；timeout 後は「インターフェースが出現しませんでした」と報告）

またはワークフローノード（より安定）：
1. wait_for_window(class_name="MainForm", timeout=30)
```

### 3.3 タスク：デスクトップアプリへのログイン

```
✅ 推奨：
1. window_find(title="Login Window") で hwnd を取得
2. window_activate(hwnd=...) でフォアグラウンドに切り替え
3. key_type(text="username", interval=0.05)  # IME 対応
4. key_press(key="tab")
5. key_type(text="password", interval=0.05)
6. key_press(key="enter")
7. 検証：数秒待つ → window_find(title="Main") でメイン画面に入ったか確認
```

### 3.4 タスク：ゲームの自動戦闘ループ

```
✅ 推奨（ワークフローエンジン）：
1. workflow_save でワークフローを保存：
   - モンスターアイコンの検索（find_image）
   - 発見時のクリック（mouse_click）
   - 1 秒待機
   - ループ
2. hermes cron でスケジューリング：60 秒ごとに実行

またはシングルセッション内：
1. bind_window(display_mode="dx", mouse_mode="windows", keyboard_mode="windows")
2. ループ（手動 loop_until "ユーザーがキャンセル"）：
   - find_image(image_path="monster.png")
   - 発見時にクリック
   - 「拾取」ボタンを探す → クリック
   - 「経験値バー満タン」ボタンを探す → クリック
   - sleep(1)
```

### 3.5 タスク：すべてのポップアップをクリア（ワークフローを継続）

```
✅ 推奨（ワークフローエンジン）：
1. 「確認」ウィンドウを探す → 発見時に key_press(enter)
2. 「エラー」ウィンドウを探す → 発見時に window_close
3. 開いている子ウィンドウを探す → 発見時に close
4. これら 3 ステップは**冪等**（見つからなければスキップ）、ワークフローの冒頭セグメントとして使用可能

または再利用可能な「クリーンアップサブフロー」として：
- ワークフロー内でサブフローをネスト参照
- 各タスク開始前にクリーンアップを実行
```

### 3.6 タスク：スクリーンショットからテキストを抽出

```
✅ 推奨：
1. screenshot(領域) でキャプチャ
2. ocr(領域) でテキスト認識
3. LLM にテキストコンテンツを解析させる（regex / LLM）

⚠️ 注意：omni ocr は各単語の座標を返しません。座標が必要な場合は find_image でテキストスクリーンショットテンプレートを探す
```

---

## 4. デバッグのヒント

### 4.1 Tool 呼び出しが失敗した場合

1. **`error_code` を確認** — 問題カテゴリを特定（E1001 = ウィンドウが見つからない、E2001 = 画像が見つからない など）
2. **`recovery_suggestions` を確認** — 「次に何をすべきか」の具体的な提案をリスト
3. **提案が不明確な場合**、**`screenshot()` で現状を確認** —> 「ウィンドウ/ボタンが見つからない」問題の 90% はスクリーンショットで一目瞭然

### 4.2 タスクが停止した場合

**AI 自身に尋ねる**：
> "あなたの最後の 5 つの Tool 呼び出しは何ですか？返された `error_code` は何ですか？"

AI に呼び出し履歴を報告させ、**自己診断**させます。

**詳細ログを有効化**：
```bash
hermes chat --verbose
# または server.py 起動時：
LOG_LEVEL=DEBUG
```

### 4.3 ワークフローが妥当か検証

`validate_workflow` ツールを使用（P3 計画、未実装；現状は JSON を Python で解析して dry-run）：

```python
# JSON 解析後の確認：
# 1. すべての step id は一意？
# 2. outputs schema のフィールド名は下流の {var} 参照と一致？
# 3. condition 式は有効？
```

### 4.4 テストツール

`tests/test_workflow_v2.py` は 8 つのワークフローエンジンユニットテスト + 統合テストを含みます。**ワークフローエンジンを変更する前に必ず実行**。

`tests/test_p0_wrap.py` は `_wrap_result` のラッピングロジックを検証（統一された返却フォーマット）。

`tests/test_p1_composite.py` は 3 つの複合 Tool のエラーパスを検証。

---

## 5. パフォーマンスとベストプラクティス

### 5.1 高頻度呼び出しの最適化

- `screenshot` は同期ブロッキング（50-200ms）、**60fps のリアルタイムループ内では使用しない**
- 高頻度スクリーンショット（>5/秒）は `mss` ライブラリを使用
- テンプレート画像の読み込みはキャッシュされる — `find_image` は同じ画像を複数回使用した方が異なる画像より高速

### 5.2 長時間タスクのスケジューリング

**シングルセッション内**：5 分未満の短時間タスクに適しています。

**クロスセッション**（`hermes cron`）：定期タスクに適しています（1 時間ごとにポップアップをクリア、10 分ごとにデータを保存）。

**ワークフローエンジン**：「クリーンアップ + メインタスク」のような複合フローに適しており、ワークフローとして保存して再利用可能。

### 5.3 安全ガードレール

1. **書き込み操作前に確認** — `mem_write` / `key_type` / `mouse_click` はすべて**副作用があります**
2. **バックグラウンド操作前に `bind_window`** — キーボード/マウスが他のウィンドウに奪われるのを防ぐ
3. **スクリーンショット前に `mouse_move(0, 0)`** でカーソルを隅に隠す — スクリーンショットにカーソルが入らないように
4. **エラーメッセージには `recovery_suggestions` があります** — エラー発生時に**まずここを確認**、**盲目的に試行しない**

---

## 6. ドキュメント相互参照

- 完全な 43 ツールの説明 + シナリオ + エラーコード：`docs/MCP_TOOLS_REFERENCE.md`
- シナリオ別の使用例：`OmniFlow 使用示例.md`
- v2 エンジンワークフロー例：`examples/workflows/infinite_fish_auto_sell.json`
- 完全なエラーコードリスト：`src/omniflow/tools/errors.py`
- スキル（AI 自身の学習用）：`~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/SKILL.md`

---

## 7. よくある質問（FAQ）

**Q: AI が Tool を呼び出したが失敗し続ける、どうすれば？**
A: AI に現状のスクリーンショットを撮って見せるよう依頼してください。「X が見つからない」問題の 90% はスクリーンショットで直接原因がわかります（ウィンドウが隠れている、ボタンが遮られている、座標がずれている など）。

**Q: Tool が適切なワークフローエンジンノードを見つけられない？**
A: ワークフロー v2 エンジンがサポートするノード：tool_call / condition / if / loop / delay / subflow / wait_for_window。**`wait_for_window_close`**（ウィンドウの消失を待つ）などの珍しいノードは**サポートしていません**。回避策：`loop_until` + `window_get_info` でウィンドウの存在性をポーリング。

**Q: AI に OmniFlow の使用パターンを学習させるには？**
A: `~/.hermes/skills/autonomous-ai-agents/omniflow-windows-automation/` 下のスキルを読み込んでください。このスキルには 6 大シナリオ、5 つのパターン、失敗回復、設計原則が含まれています。

**Q: AI が誤って `mem_write` を使用した、どうすれば？**
A: 即座に取り消してください！`mem_write` の誤ったアドレスへの書き込みは対象プロセスをクラッシュさせる可能性があります。**予防** > **治療**：AI に `mem_write` を自動使用させない — 明示的に「スクリーンショット + find_image を使用し、メモリを変更しない」と要求してください。

**Q: ワークフローエンジンが遅い？**
A: ワークフロー v2 エンジンはシングルスレッド順次実行です（v1 も同様）、並列化されていません。ワークフローが 100 ステップあり、各 100ms かかる場合、合計 10 秒です。最適化：ステップを統合、`wait_for_window` のポーリング間隔を短縮、`hermes cron` で大きなタスクを複数の小さなタスクに分割。

**Q: 異なる LLM の OmniFlow 使用習慣は？**
A:
- **Claude Opus / Sonnet**：複合 Tool が最も得意、エラーコード + 回復提案への感度が高い
- **GPT-4 / GPT-4o**：Claude と同様
- **ローカル小モデル（例：llama3 7B）**：多段オーケストレーションで失敗する可能性があります。`click_image` などの複合 Tool を使用してオーケストレーションの複雑さを減らすことを**推奨**
