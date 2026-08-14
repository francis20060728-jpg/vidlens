# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

テキスト専用 AI エージェントに画像と動画を見る能力を与えます。

VidLens は視覚ファイルを外部のビジョンモデルにルーティングし、プレーンテキストを返します。Codex、Claude Code、Cursor、Cline など、ネイティブ画像サポートなしで視覚コンテンツを検査、検証、応答できます。

> **モデルがネイティブで視覚をサポートする場合は VidLens を使わないでください。** テキスト専用モデル専用です。

## 仕組み

```
画像/動画 -> base64 エンコード -> ビジョン API -> プレーンテキスト結果
```

## ワンクリック・デプロイ（AIエージェントに指示）

エージェントに伝えます：

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

エージェントがリポジトリをクローンし、--initを実行して、config.yamlの入力を支援します。

## 前提条件

- [Python 3](https://python.org)（3.7+）
- OpenAI 互換ビジョン API キー
- （任意）動画用 [ffmpeg](https://ffmpeg.org)

## クイックスタート：MCP サーバー（推奨）

MCP は VidLens を使う最速の方法です。

```bash
# 1. インストール
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. 設定
python scripts/vidlens.py --init
# config.yaml を編集
# 3. MCP サーバー起動
python vidlens/server.py
```

MCP クライアント（Claude Desktop、Cursor、Cline）に登録：

```json
{
  "mcpServers": {
    "vidlens": {
      "command": "python",
      "args": ["/abs/path/to/vidlens/vidlens/server.py"]
    }
  }
}
```

### MCP ツール

| ツール | 説明 | 主な引数 |
|------|------|------|
| `look` | ビジョンモデルで単一の画像または動画ファイルを分析。動画は自動的にラベル付きコンタクトシートにサンプリングされます。 | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | ディレクトリ内の画僻・動画ファイルを検索。再帰的に検索し、ファイル名キーワードでフィルタリング。画像優先でソートされた絶対パスを返します。 | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | キーワードでディレクトリを検索し、最適な一致を1回の呼び出しで分析。list_media + lookの便利な組み合わせ。 | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

例：`look(media_path="chart.png", prompt="この画像は何を示していますか？")`


## クイックスタート：CLI（MCP 非対応フォールバック）

結果は stdout に直接出力されます。

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "画像に何がありますか？"
```

## 自動使用ルール（Codex）

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

ネイティブ視覚を先にチェック：モデルが画像を見られるなら VidLens をスキップ。

## 機能

- **画像はゼロ依存**（Python 標準ライブラリのみ）
- **MCP サーバーモード**
- **プロバイダーフェイルオーバー**（最大9つ）
- **推論モデルサポート**
- **ローカル OCR フォールバック**
- **動画サポート**（ffmpeg / opencv）
- **カスタムプロンプトテンプレート**
- **マルチプロバイダー**

## 設定

| キー | デフォルト | 目的 |
|-----|-----|-----|
| `api_url` | `""` | ビジョン API URL |
| `api_key` | `""` | API キー |
| `model_name` | `""` | モデル名 |
| `response_tokens` | `4000` | 最大トークン |
| `is_reasoning_model` | `false` | 推論モデルは true |

## トラブルシューティング

| 問題 | 解決策 |
|---------|---------|
| `NEEDS CONFIG` | `--init` 実行後 config.yaml を編集 |
| 動画失敗 | ffmpeg または `pip install opencv-python numpy` |

## フィードバック

ご質問やご提案は **francis20060728@gmail.com** までメールでお知らせください。早急に対応いたします。
## ドキュメント

- [セットアップ](docs/SETUP.md)
- [詳細機能](docs/ADVANCED.md)
- [トラブルシューティング](docs/TROUBLESHOOTING.md)
- [変更履歴](CHANGELOG.md)

## ライセンス

MIT。[LICENSE](LICENSE) を参照してください。
