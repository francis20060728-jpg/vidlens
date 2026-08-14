# VidLens

[English](README.md) | [简体中文](zhcn.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

讓純文字 AI 智慧體擁有「看」圖片和影片的能力。

VidLens 將視覺檔案路由到外部視覺模型，回傳純文字。任何智慧體 -- Codex、Claude Code、Cursor、Cline -- 無需原生影像支援即可檢查、驗證和回應視覺內容。

> **如果你的模型本身支援視覺，請不要使用 VidLens。** 它只用於無法看圖的純文字模型。

## 工作原理

```
圖片/影片 -> base64 編碼 -> 視覺 API -> 純文字結果
```

## 前置條件

- 已安裝 [Python 3](https://python.org)（3.7+）
- 一個 OpenAI 相容的視覺 API 金鑰
- （選用）[ffmpeg](https://ffmpeg.org) 用於影片支援

## 快速開始：MCP 伺服器（推薦）

MCP 是使用 VidLens 最快的方式——無程序啟動、無沙箱延遲。

```bash
# 1. 安裝
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. 設定
python scripts/vidlens.py --init
# 編輯 config.yaml: api_url, api_key, model_name
# 3. 啟動 MCP 伺服器
python vidlens/server.py
```

在 MCP 用戶端（Claude Desktop、Cursor、Cline）中註冊：

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

三個工具：`look`、`list_media`、`find_and_look`。

## 快速開始：CLI（不支援 MCP 的備選）

結果直接列印到 stdout，無需讀取單獨的檔案。

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
# 編輯 config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "圖片裡有什麼？"
```

## 自動使用規則（Codex）

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

規則會先檢查原生視覺：如果模型能看圖就跳過 VidLens。MCP 工具優先於 CLI。

## 功能

- **圖片零依賴**（僅 Python 標準庫）
- **MCP 伺服器模式**
- **多提供商故障轉移**（最多 9 個備用）
- **推理模型支援**
- **本地 OCR 回退**
- **影片支援**（ffmpeg 或 opencv）
- **自訂 prompt 範本**
- **多提供商**：任何 OpenAI 相容的視覺 API

## 設定

| 鍵 | 預設值 | 用途 |
|-----|-----|-----|
| `api_url` | `""` | 視覺 API 位址 |
| `api_key` | `""` | API 金鑰 |
| `model_name` | `""` | 模型名稱 |
| `response_tokens` | `4000` | 最大回應 token |
| `http_timeout` | `120` | 逾時秒數 |
| `is_reasoning_model` | `false` | 推理模型設 true |

## 故障排除

| 問題 | 修復 |
|---------|---------|
| `NEEDS CONFIG` | 執行 `--init`，填 config.yaml，然後 `--status` |
| 影片失敗 | 安裝 ffmpeg 或 `pip install opencv-python numpy` |

## 文件

- [安裝指南](docs/SETUP.md)
- [進階功能](docs/ADVANCED.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [更新日誌](CHANGELOG.md)

## 授權

MIT。詳見 [LICENSE](LICENSE)。
