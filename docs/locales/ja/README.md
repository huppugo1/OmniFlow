# OmniFlow

> MCP (Model Context Protocol) プロトコルベースの Windows 自動化オールインワンツール

**[English](../en/README.md)** | [中文](../zh-CN/README.md) | **日本語** | [Deutsch](../de/README.md)

OmniFlow は Windows デスクトップ自動化機能（ウィンドウ操作、画像/色認識、文字認識、キーボード/マウスシミュレーション、バックグラウンドバインド、メモリ操作など）を標準の **MCP Server** としてカプセル化し、MCP プロトコルをサポートする任意の AI クライアント（Claude Desktop、VS Code、CodeBuddy、Cursor、Windsurf、Continue、Cline、Cody、Crayfish、Hermes、Trae、Kiro など）が Windows 自動化機能を直接呼び出せるようにします。

---

## ✨ 機能特性

### 🎯 応用シナリオ

OmniFlow は Windows デスクトップアプリケーションを「AI が呼び出せるツール」に変換します。一般的なユースケース：

- **🎨 画像処理自動化** — Photoshop / AI などのプロフェッショナルソフトウェアを駆動して一括画像処理（リサイズ、色調整、フィルター、一括エクスポート）
- **📸 スクリーンショットパイプライン** — 画面キャプチャ → OCR テキスト抽出 / PIL 二次処理 / 画面への注記書き戻し
- **✏️ 描画自動化** — mspaint で図を描画、注記追加、フローチャート作成
- **🎮 ゲームアシスタント** — バックグラウンド放置、自動戦闘、ダンジョン自動化
- **📝 オフィス自動化** — WPS / Office 文書の自動入力、レポート生成、一括書式調整
- **🎬 ビデオ制御** — プレーヤーの自動一時停止/再開、字幕認識、タイマー録画

### 🖥️ ウィンドウ操作
- ウィンドウの検索と列挙（タイトル、クラス名、PID など）
- ウィンドウ状態の取得（位置、サイズ、表示状態、最小化状態など）
- ウィンドウの最前面化 / 最前面解除 / 表示 / 非表示
- ウィンドウのバインドとアンバインド（バックグラウンド操作の準備）

### 🎯 画像/色認識
- **画像検索**：画面の指定領域で類似度による画像位置検索、複数画像の一括検索をサポート
- **色検索**：単点、多点、領域での色検索、色の許容範囲をサポート
- **色比較**：指定座標の色を比較
- **スクリーンショット**：指定領域のキャプチャと保存 / 画像データの返却

### 📝 文字認識（OCR）
- **文字検索**：プリセットフォントライブラリに基づいて画面上の文字座標を検索
- **文字認識**：指定領域内のテキストコンテンツを認識して返却
- 標準フォント、多色フォント、偏色フォントをサポート
- フォントライブラリ不要の OCR 認識をサポート

### ⌨️🖱️ キーボード/マウスシミュレーション
- **フォアグラウンド入力**：キーボードキー、コンビネーション、文字列入力のシミュレーション；マウスの移動 / クリック / スクロール
- **バックグラウンド入力**：バインドされたウィンドウにバックグラウンドメッセージを送信し、フォーカスを奪わない
- キー状態制御（長押し / 解放）をサポート

### 🧠 バックグラウンドバインド
- 複数の画像バインドモード：`gdi`、`dx`、`dx2`、`opengl` など
- 複数のキーボード/マウスバインドモード：`windows`、`normal` など
- ゲームのバックグラウンド放置やマルチウィンドウ並列自動化に適用

#### 4 種類の display_mode 選択

| モード | 原理 | 利点 | 欠点 | AI が選択すべきタイミング |
|------|------|------|------|----------------------|
| `gdi` | GDI API スクリーンショット | 安定、互換性が高い | ウィンドウを最小化できない | **デフォルトの第一選択**、一般的なデスクトップソフトウェア（WPS / ペイント / PS） |
| `dx` | DirectX Hook | 最小化可能、高性能 | 一部のゲームで非対応 | ユーザーが **DirectX エンジン** のゲームと明言した場合 |
| `dx2` | DirectX 強化 | 互換性がさらに高い | リソース消費がやや高い | `dx` モードが失敗した場合に試行 |
| `opengl` | OpenGL Hook | OpenGL ゲームをサポート | やや不安定 | ユーザーが **OpenGL エンジン** のゲームと明言した場合 |

**キーボード/マウスモード**：`normal`（フォアグラウンド、ウィンドウが最前面に必要）/ `windows`（Windows メッセージバックグラウンド、**推奨**）

**自動モード選択（将来）**：`detect_bind_mode(hwnd)` ツールを追加し、`gdi → dx → dx2 → opengl` を自動試行して推奨を返す予定。

### 🧬 メモリ操作
- プロセスメモリの読み取り / 書き込み
- メモリ検索とシグネチャスキャン
- プロセスモジュールのベースアドレス取得

### 📁 ファイルとシステム
- ファイルの読み書き操作
- システム情報の取得（CPU 使用率、メモリ、画面解像度など）
- プロセスの列挙と管理

### 🔧 マルチスレッド安全性
- マルチスレッド並列呼び出しをサポート
- スレッドごとに独立したウィンドウバインド、相互干渉なし

### 🔄 ワークフロー
- ビジュアル / スクリプトによる自動化タスクフローのオーケストレーション
- 条件分岐、ループ、遅延、サブフローなどの制御構造をサポート
- タスクチェーンの連続実行、前のステップの出力を次のステップの入力として使用
- ワークフローの保存、読み込み、再利用をサポート

### 🧩 プラグインシステム
- プラグインのホットロードで OmniFlow の能力を拡張
- カスタム Tool、カスタムワークフローノードをサポート
- コミュニティプラグインエコシステムで自動化能力の共有と再利用

---

## 🏗️ アーキテクチャ

```
┌────────────────────────────────────────┐
│           AI クライアント (MCP Host)      │
│  Claude Desktop / CodeBuddy / VS Code   │
│  Cursor / Windsurf / Continue / Cline   │
│  Crayfish / Hermes / Trae / Kiro ...     │
└──────────────┬─────────────────────────┘
               │  MCP プロトコル (stdio)
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
│          Windows システム層             │
│     GDI / DX / Win32 API               │
└─────────────────────────────────────────┘
```

---

## 📥 インストール

### 前提条件
- Windows オペレーティングシステム
- Python 3.10+

### インストール手順

```bash
# 1. リポジトリをクローン
git clone <this-repo-url>
cd OmniFlow

# 2. 仮想環境を作成
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac（一部機能非対応）

# 3. 依存関係をインストール（重要：`pip install -e .` が必須で、omniflow パッケージを `python -m omniflow` でインポート可能にする）

# 方法1：requirements.txt + editable install（推奨）
pip install -r requirements.txt
pip install -e .

# 方法2：ワンライナー
pip install -r requirements.txt && pip install -e .
```

---

## 🚀 クイックスタート

### MCP クライアントの設定

MCP クライアントの設定ファイルに OmniFlow を追加：

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

> 説明：
> - `command` は venv 内の `python.exe` を指します（例：`D:/OmniFlow/.venv/Scripts/python.exe`）
> - `cwd` は OmniFlow リポジトリのルートディレクトリを指します
> - 一部の MCP クライアントは `cwd` フィールドを**サポート**します（例：Hermes）；サポートしていない場合は `env.PYTHONPATH` で代替

### 例：AI に画像を自動検索してクリックさせる

> AI クライアントの自然言語記述を通じて、OmniFlow は自動的に対応する MCP Tool を呼び出します：

1. 画面をキャプチャ → `screenshot`
2. スクリーンショット内で画像を検索 → `find_image`
3. マウスを移動してクリック → `mouse_click`

AI クライアントはこれらの MCP Tool 呼び出しを自動的にオーケストレーションします。

---

## 📖 MCP Tools リファレンス

### ウィンドウ系

| Tool | 説明 |
|------|------|
| `window_find` | タイトル / クラス名でウィンドウを検索 |
| `window_enum` | すべてのトップレベルウィンドウを列挙 |
| `window_get_info` | ウィンドウの詳細情報を取得 |
| `window_set_top` | ウィンドウを最前面化 |
| `window_show` | ウィンドウを表示 / 非表示 |
| `window_activate` | ウィンドウをフォアグラウンドにアクティブ化 |
| `window_close` | ウィンドウを閉じる（WM_CLOSE メッセージを送信、X をクリックするのと同等） |

### バインド系

| Tool | 説明 |
|------|------|
| `bind_window` | ウィンドウをバックグラウンドバインド、キーボード/マウス制御時にユーザーが感知しない（画像 / キーボード/マウスモードを指定） |
| `unbind_window` | ウィンドウをアンバインド、フォアグラウンド操作に戻す |

### 画像/色系

| Tool | 説明 |
|------|------|
| `screenshot` | 指定領域をキャプチャ、Base64 画像を返却 |
| `find_image` | 指定領域で画像を検索、座標を返却 |
| `find_color` | 指定色を検索、座標を返却 |
| `compare_color` | 指定座標の色を比較 |
| `get_color` | 指定座標の色値を取得 |

### 文字系

| Tool | 説明 |
|------|------|
| `ocr` | 指定領域内の文字を認識 |
| `find_text` | 画面上で文字位置を検索 |
| `set_ocr_dict` | OCR フォントライブラリファイルパスを設定 |

### キーボード/マウス系

| Tool | 説明 |
|------|------|
| `key_press` | キーボードキーを押す |
| `key_down` | キーボードキーを長押し |
| `key_up` | キーボードキーを解放 |
| `key_type` | 文字列を入力 |
| `hotkey` | コンビネーションキーを送信、例：Ctrl+C |
| `mouse_move` | マウスを移動 |
| `mouse_click` | マウスクリック（左 / 右 / 中ボタン） |
| `mouse_scroll` | マウススクロール |
| `mouse_get_pos` | 現在のマウス位置を取得 |

### メモリ系

| Tool | 説明 |
|------|------|
| `mem_read` | プロセスメモリを読み取る |
| `mem_write` | プロセスメモリに書き込む |
| `get_module_base` | プロセスモジュールのベースアドレスを取得 |

### システム系

| Tool | 説明 |
|------|------|
| `get_system_info` | CPU、メモリなどのシステム情報を取得 |
| `get_screen_size` | 画面解像度を取得 |
| `enum_process` | 実行中のプロセスを列挙 |
| `run_program` | 外部プログラムを起動（PATH 検索と .lnk ショートカットをサポート） |

### ワークフロー系

| Tool | 説明 |
|------|------|
| `workflow_run` | 指定ワークフローを実行 |
| `workflow_list` | 保存済みのすべてのワークフローを一覧表示 |
| `workflow_save` | 現在のオーケストレーションワークフローを保存 |
| `workflow_delete` | ワークフローを削除 |
| `workflow_pause` | ワークフロー実行を一時停止 |
| `workflow_resume` | ワークフロー実行を再開 |

### コンボ系（3 つ）⭐AI フレンドリー

| Tool | 説明 |
|------|------|
| `click_image` | 画像を検索してクリック（find_image + mouse_move + mouse_click を統合） |
| `wait_and_click` | 画像が出現するまでポーリングしてクリック |
| `ocr_and_click` | OCR で文字を検索して領域中心をクリック |

### プラグイン系

| Tool | 説明 |
|------|------|
| `plugin_list` | インストール済みプラグインを一覧表示 |
| `plugin_install` | プラグインをインストール |
| `plugin_uninstall` | プラグインをアンインストール |
| `plugin_enable` | プラグインを有効化 |
| `plugin_disable` | プラグインを無効化 |

---

## 📁 プロジェクト構造

```
OmniFlow/
├── .gitignore               # Git 無視設定
├── README.md                # プロジェクト説明
├── OmniFlow 使用示例.md      # 使用例（シナリオ別：PS / スクリーンショット / 描画）
├── requirements.txt         # Python 依存関係
├── pyproject.toml          # プロジェクトメタデータ
├── scripts/                 # 補助スクリプト
├── docs/
│   ├── AI_INTEGRATION_GUIDE.md   # AI 統合ガイド（設定 / Prompt / デバッグ）
│   ├── MCP_TOOLS_REFERENCE.md    # 43 tool 完全リファレンス（エラーコード含む）
│   └── OPTIMIZATION_PLAN.md      # 最適化プラン
├── src/
│   └── omniflow/
│       ├── __init__.py
│       ├── __main__.py       # エントリーポイント (python -m omniflow)
│       ├── server.py         # MCP Server メインロジック
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── com.py        # COM / Win32 API ラッパー
│       │   └── types.py      # 型定義
│       └── tools/
│           ├── __init__.py
│           ├── window.py     # ウィンドウ関連 Tools（window_close 含む）
│           ├── binding.py    # バインド関連 Tools
│           ├── image.py      # 画像/色認識 Tools
│           ├── ocr.py        # 文字認識 Tools
│           ├── input.py      # キーボード/マウスシミュレーション Tools
│           ├── memory.py     # メモリ操作 Tools
│           ├── system.py     # システム関連 Tools（run_program 含む）
│           ├── workflow.py   # ワークフロー Tools（v2 エンジン：IF / WAIT_FOR_WINDOW / 変数システム）
│           └── plugin.py     # プラグインシステム Tools
├── examples/
│   ├── open_photoshop.py    # Photoshop 自動化例
│   ├── ai_prompts/          # AI Prompt 例（4 シナリオ）
│   │   ├── game_automation.md
│   │   ├── office_automation.md
│   │   ├── image_processing.md
│   │   └── web_control.md
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # v2 エンジン完全ワークフロー例（自己完結）
└── tests/
    ├── __init__.py
    ├── test_tools.py        # ツール基本テスト
    └── test_workflow_v2.py  # workflow v2 エンジン回帰テスト（8 ケース）
```

> 注：OmniFlow エンジン v2 の改善点（変数システム / IF ノード / WAIT_FOR_WINDOW / 安全な condition / 実際の MCP 呼び出し）については、`docs/workflows/translation-notes.md` と `known-integrations.md` の OmniFlow 0.2.0 エントリを参照。

---

## 🛠️ 開発

```bash
# 開発依存関係をインストール
pip install -e ".[dev]"

# テストを実行
pytest

# コードフォーマット
ruff format src/
ruff check src/
```

---

## 📄 ライセンス

**MIT License**

OmniFlow は MIT ライセンスを採用しています。これは非常に寛容なオープンソースライセンスです：

- ✅ コードの自由な使用、複製、変更、配布を許可
- ✅ 商用プロジェクトでの使用可能
- ✅ 派生作品のクローズドソース公開可能
- ⚠️ 元の著作権表示とライセンステキストの保持のみ必要

具体的な条項については、プロジェクト内の LICENSE ファイルを参照してください。

---

## ⚠️ 免責事項

本ツールは合法的な用途（自動化テスト、オフィス自動化など）のみに使用してください。ゲームのサービス条項違反、他人の権利侵害、または違法行為には使用しないでください。使用者は自己責任で使用してください。
