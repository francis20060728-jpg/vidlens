# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [zhtw](zhtw.md) | [ko](ko.md) | [fr](fr.md) | [es](es.md) | [de](de.md) | [pt](pt.md)

テキスト専用 AI エージェントに画像と動画を見る能力を与えます。

VidLens は視覚ファイルを外部のビジョンモデルにルーティングし、プレーンテキストを返します。

**画像分析はゼロ依存。** Python 3 標準ライブラリのみ必要。

**モデルがネイティブで視覚をサポートする場合は VidLens を使わないでください。** テキスト専用モデル専用です。

## クイックスタート：MCP サーバー（推奨）

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
python vidlens/server.py
```

## クイックスタート：CLI（MCP 非対応のフォールバック）

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "画像に何がありますか？"
```

## 自動使用ルール

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
```

## ライセンス

MIT。[LICENSE](LICENSE) を参照してください。
