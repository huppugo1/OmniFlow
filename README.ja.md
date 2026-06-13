# OmniFlow

> MCP (Model Context Protocol) プロトコルに基づく Windows オートメーションツールキット

[English](README.en.md) | [中文](README.md) | **日本語** | [Deutsch](README.de.md)

OmniFlow は、Windows デスクトップオートメーション機能（ウィンドウ操作、画像/カラー認識、OCR、キーボード/マウスシミュレーション、バックグラウンドバインディング、メモリ操作など）を標準的な **MCP Server** としてカプセル化します。MCP プロトコルをサポートする任意の AI クライアント（Claude Desktop、VS Code、CodeBuddy、Cursor、Windsurf、Continue、Cline、Cody、Crayfish、Hermes、Trae、Kiro など）が、Windows オートメーション機能を直接呼び出すことができます。

---

## ✨ 機能

### 🎯 使用例

OmniFlow は Windows デスクトップアプリケーションを「AI から呼び出し可能なツール」に変えます。一般的な使用例：

- **🎨 画像処理オートメーション** — Photoshop/AI を駆使してバッチ画像処理（リサイズ、カラーグレーディング、フィルター、バッチエクスポート）
- **📸 スクリーンショットパイプライン** — 画面キャプチャ → OCR テキスト抽出 / PIL 二次処理 / アノテーションの画面への書き戻し
- **✏️ 描画オートメーション** — mspaint で図面、注釈、フローチャートを描く
- **🎮 ゲームオートメーション** — バックグラウンドでの放置、オートバトル、ダンジョンの記録と再生
- **📝 オフィスオートメーション** — WPS/Office ドキュメントの自動入力、レポート生成、バッチフォーマット変更
- **🎬 ビデオコントロール** — プレーヤーの自動一時停止/再開、字幕認識、スケジュール録画

### 🖥️ ウィンドウ操作
- ウィンドウの検索と列挙（タイトル、クラス名、PID など）
- ウィンドウステータスの取得（位置、サイズ、可視性、最小化状態など）
- ウィンドウの最前面表示 / 最前面解除 / 表示 / 非表示
- ウィンドウのバインドとアンバインド（バックグラウンド操作の準備）

### 🎯 画像・カラー認識
- **画像検索**: 指定した画面領域内で類似度に基づいて画像位置を検索、バッチ検索をサポート
- **カラー検索**: 単一点カラー検索、多点カラー検索、領域カラー検索、カラー許容範囲をサポート
- **カラー比較**: 指定した座標のカラーを比較
- **スクリーンショット**: 指定領域をキャプチャして保存 / 画像データを返す

### 📝 OCR（光学文字認識）
- **テキスト検索**: プリセット辞書に基づいて画面上のテキスト座標を検索
- **テキスト認識**: 指定領域内のテキスト内容を認識して返す
- 標準文字、マルチカラー文字、色ずれ文字をサポート
- 辞書なし OCR 認識をサポート

### ⌨️🖱️ キーボード・マウスシミュレーション
- **フォアグラウンド入力**: キーボードキー、キーコンビネーション、文字列入力のシミュレーション；マウスの移動 / クリック / スクロール
- **バックグラウンド入力**: バインドされたウィンドウにバックグラウンドメッセージを送信、フォーカスを奪わない
- キーステータス制御（押下 / 解放）をサポート

### 🧠 バックグラウンドバインディング
- 複数の画像/カラーバインドモード: `gdi`、`dx`、`dx2`、`opengl` など
- 複数のキーボード/マウスバインドモード: `windows`、`normal` など
- ゲームのバックグラウンド放置、マルチウィンドウ同時オートメーションに適している

### 🧬 メモリ操作
- プロセスメモリの読み取り / 書き込み
- メモリ検索とパターンスキャン
- プロセスモジュールのベースアドレスの取得

### 📁 ファイル・システム
- ファイルの読み書き操作
- システム情報の取得（CPU使用率、メモリ、画面解像度など）
- プロセスの列挙と管理

### 🔧 スレッドセーフ
- マルチスレッド同時呼び出しをサポート
- 各スレッドは独立したウィンドウバインディングを持ち、相互干渉しない

### 🔄 ワークフロー
- 視覚的 / スクリプトベースのオートメーションタスクオーケストレーション
- 条件分岐、ループ、遅延待機、サブフローなどの制御構造をサポート
- タスクチェーン実行、前ステップの出力を次ステップの入力として使用
- ワークフローの保存、読み込み、再利用をサポート

### 🧩 プラグインシステム
- プラグインのホットローディングによる OmniFlow 機能の拡張
- カスタムツール、カスタムワークフローノードをサポート
- コミュニティプラグインエコシステムによるオートメーション機能の共有と再利用

---

## 🏗️ アーキテクチャ

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

## 📥 インストール

### 前提条件
- Windows OS
- Python 3.10+

### インストール手順

```bash
# 1. リポジトリをクローン
git clone <this-repo-url>
cd OmniFlow

# 2. 仮想環境を作成
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac (一部の機能はサポートされていません)

# 3. 依存関係をインストール（重要：`pip install -e .` を使用して、`python -m omniflow` 経由で omniflow パッケージをインポート可能にする必要があります）

# 方法1: requirements.txt + editable install（推奨）
pip install -r requirements.txt
pip install -e .

# 方法2: ワンライナー
pip install -r requirements.txt && pip install -e .
```

---

## 🚀 クイックスタート

### MCP クライアントの設定

OmniFlow を MCP クライアントの設定ファイルに追加します：

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

> 注:
> - `command` は venv 内の python.exe を指します（例: `D:/OmniFlow/.venv/Scripts/python.exe`）
> - `cwd` は OmniFlow リポジトリのルートディレクトリを指します
> - 一部の MCP クライアントは `cwd` フィールドを**サポート**しています（例: Hermes）；サポートしていない場合は `env.PYTHONPATH` を代わりに使用してください

### 例：AI に画像を見つけさせてクリックさせる

> AI クライアントで自然言語で記述することで、OmniFlow は対応する MCP Tool を自動的に呼び出します：

1. 画面をキャプチャ → `screenshot`
2. スクリーンショット内で画像を検索 → `find_image`
3. マウスを移動してクリック → `mouse_click`

AI クライアントはこれらの MCP Tool 呼び出しを自動的にオーケストレーションします。

---

## 📖 MCP Tools リファレンス

### ウィンドウツール

| Tool | 説明 |
|------|------|
| `window_find` | タイトル / クラス名でウィンドウを検索 |
| `window_enum` | すべてのトップレベルウィンドウを列挙 |
| `window_get_info` | ウィンドウの詳細情報を取得 |
| `window_set_top` | ウィンドウを最前面に表示 |
| `window_show` | ウィンドウを表示 / 非表示 |
| `window_activate` | ウィンドウをフォアグラウンドにアクティブ化 |
| `window_close` | ウィンドウを閉じる（WM_CLOSE メッセージを送信、X をクリックするのと同じ） |

### バインディングツール

| Tool | 説明 |
|------|------|
| `bind_window` | バックグラウンド操作のためにウィンドウをバインド、キーボード/マウス制御はユーザーに対して透過的（画像/カラーおよび入力モードを指定） |
| `unbind_window` | ウィンドウのバインドを解除、フォアグラウンド操作に戻す |

### 画像ツール

| Tool | 説明 |
|------|------|
| `screenshot` | 指定領域をキャプチャ、Base64 画像を返す |
| `find_image` | 指定領域内で画像を検索、座標を返す |
| `find_color` | 指定した色を検索、座標を返す |
| `compare_color` | 指定した座標の色を比較 |
| `get_color` | 指定した座標の色値を取得 |

### テキストツール

| Tool | 説明 |
|------|------|
| `ocr` | 指定領域内のテキストを認識 |
| `find_text` | 画面上のテキスト位置を検索 |
| `set_ocr_dict` | OCR 辞書ファイルパスを設定 |

### 入力ツール

| Tool | 説明 |
|------|------|
| `key_press` | キーボードキーを押して離す |
| `key_down` | キーボードキーを押し続ける |
| `key_up` | キーボードキーを離す |
| `key_type` | 文字列を入力 |
| `hotkey` | キーコンビネーションを送信、例: Ctrl+C |
| `mouse_move` | マウスを移動 |
| `mouse_click` | マウスクリック（左 / 右 / 中ボタン） |
| `mouse_scroll` | マウススクロール |
| `mouse_get_pos` | 現在のマウス位置を取得 |

### メモリツール

| Tool | 説明 |
|------|------|
| `mem_read` | プロセスメモリを読み取る |
| `mem_write` | プロセスメモリに書き込む |
| `get_module_base` | モジュールのベースアドレスを取得 |

### システムツール

| Tool | 説明 |
|------|------|
| `get_system_info` | CPU、メモリなどのシステム情報を取得 |
| `get_screen_size` | 画面解像度を取得 |
| `enum_process` | 実行中のプロセスを列挙 |
| `run_program` | 外部プログラムを起動（PATH 検索および .lnk ショートカットをサポート） |

### ワークフローツール

| Tool | 説明 |
|------|------|
| `workflow_run` | 指定したワークフローを実行 |
| `workflow_list` | 保存されているすべてのワークフローをリスト表示 |
| `workflow_save` | 現在オーケストレーションされているワークフローを保存 |
| `workflow_delete` | ワークフローを削除 |
| `workflow_pause` | ワークフローの実行を一時停止 |
| `workflow_resume` | ワークフローの実行を再開 |

### プラグインツール

| Tool | 説明 |
|------|------|
| `plugin_list` | インストールされているプラグインをリスト表示 |
| `plugin_install` | プラグインをインストール |
| `plugin_uninstall` | プラグインをアンインストール |
| `plugin_enable` | プラグインを有効化 |
| `plugin_disable` | プラグインを無効化 |

---

## 📁 プロジェクト構造

```
OmniFlow/
├── .gitignore               # Git ignore 設定
├── README.md                # プロジェクトドキュメント（中国語）
├── README.en.md             # プロジェクトドキュメント（英語）
├── README.ja.md             # プロジェクトドキュメント（日本語）
├── README.de.md             # プロジェクトドキュメント（ドイツ語）
├── OmniFlow 使用示例.md      # 使用例（シナリオ別：PS / スクリーンショット / 描画）
├── requirements.txt         # Python 依存関係
├── pyproject.toml          # プロジェクトメタデータ
├── scripts/                 # ヘルパースクリプト
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
│           ├── window.py     # ウィンドウツール（window_close を含む）
│           ├── binding.py    # バインディングツール
│           ├── image.py      # 画像/カラー認識ツール
│           ├── ocr.py        # OCR ツール
│           ├── input.py      # キーボード/マウスシミュレーションツール
│           ├── memory.py     # メモリ操作ツール
│           ├── system.py     # システムツール（run_program を含む）
│           ├── workflow.py   # ワークフローツール（v2 エンジン: IF / WAIT_FOR_WINDOW / 変数システム）
│           └── plugin.py     # プラグインシステムツール
├── examples/
│   ├── open_photoshop.py    # Photoshop オートメーション例
│   └── workflows/
│       └── infinite_fish_auto_sell.json   # v2 エンジンの完全なワークフロー例（自己完結型）
└── tests/
    ├── __init__.py
    ├── test_tools.py        # 基本ツールテスト
    └── test_workflow_v2.py  # ワークフロー v2 エンジンリグレッションテスト（8 ケース）
```

> 注: OmniFlow エンジン v2 の改善点（変数システム / IF ノード / WAIT_FOR_WINDOW / 安全な条件 / 真の MCP 呼び出し）は `docs/workflows/translation-notes.md` および `known-integrations.md` の OmniFlow 0.2.0 のエントリーを参照してください。

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

MIT License

---

## ⚠️ 免責事項

このツールは合法的な目的（自動化テスト、オフィスオートメーションなど）にのみ使用してください。ゲームの利用規約違反、他人の権利侵害、または違法行為に関与するシナリオに使用しないでください。使用者は自分の行為に対して責任を負う必要があります。