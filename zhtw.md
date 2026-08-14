# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [ja](ja.md) | [ko](ko.md) | [fr](fr.md) | [es](es.md) | [de](de.md) | [pt](pt.md)

讓純文字 AI 智慧體擁有「看」圖片和影片的能力。

VidLens 將視覺檔案路由到外部視覺模型，回傳純文字。任何智慧體無需原生影像支援即可檢查和回應視覺內容。

**圖片分析零依賴。** 只需 Python 3 標準庫。影片可用 ffmpeg，opencv 為可選回退。

**如果你的模型本身支援視覺，請不要使用 VidLens。** 它只用於無法看圖的純文字模型。

## 快速開始：MCP 伺服器（推薦）

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
# 編輯 config.yaml: api_url, api_key, model_name
python vidlens/server.py
```

## 快速開始：CLI（不支援 MCP 的備選）

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "圖片裡有什麼？"
```

## 自動使用規則

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
```

## 授權

MIT。詳見 [LICENSE](LICENSE)。
