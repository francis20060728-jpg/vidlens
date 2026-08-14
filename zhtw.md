# VidLens

[English](README.md) | [简体中文](zhcn.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

讓純文字 AI 智慧體擁有「看」圖片和影片的能力。

VidLens 將視覺檔案路由到外部視覺模型，回傳純文字。任何智慧體 -- Codex、Claude Code、Cursor、Cline -- 無需原生影像支援即可檢查、驗證和回應視覺內容。

> **如果目前模型/提供商明確是多模態，請使用原生視覺。** 純文字或能力未知時，VidLens 使用外部視覺並只回傳文字。

## 工作原理

```
圖片/影片 -> base64 編碼 -> 視覺 API -> 純文字結果
```

## 一鍵部署（告訴你的 AI 智慧體）

告訴你的智慧體：

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

智慧體會克隆倉庫、執行 --init，並幫你填寫 config.yaml。

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

### MCP 工具

| 工具 | 描述 | 主要參數 |
|------|------|------|
| `look` | 用視覺模型分析單個圖片或影片檔案。影片自動採樣為帶標註的聯繫表。 | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | 查找目錄中的圖片和影片檔案。遞迴搜尋，按檔名關鍵詞過濾。回傳按圖片優先排序的絕對路徑。 | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | 按關鍵詞搜尋目錄，然後一次呼叫分析最佳匹配。list_media + look 的便捷組合。 | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

範例：`look(media_path="chart.png", prompt="這張圖顯示了什麼？")`


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

規則會先確認實際模型/提供商能力。明確多模態的模型使用原生視覺，並可將路徑載入原生輸入；純文字或能力未知時由 VidLens 回傳純文字。原生影像請求被拒絕後不會重試。

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
| `response_tokens` | `1200` | 最大回應 token |
| `verification_tokens` | `350` | PASS/FAIL 驗證用較短預算 |
| `http_timeout` | `45` | 單次請求逾時 |
| `total_timeout` | `60` | 總逾時 |
| `reasoning_effort` | `""` | 可選推理強度 |
| `max_image_side` | `1600` | 圖片最大邊長 |
| `image_jpeg_quality` | `90` | JPEG 品質 |
| `is_reasoning_model` | `false` | 推理模型設 true |

## 故障排除

| 問題 | 修復 |
|---------|---------|
| `NEEDS CONFIG` | 執行 `--init`，填 config.yaml，然後 `--status` |
| 影片失敗 | 安裝 ffmpeg 或 `pip install opencv-python numpy` |

## 回饋

有問題或建議？發電子郵件到 **francis20060728@gmail.com**，我會盡快處理。
## 文件

- [安裝指南](docs/SETUP.md)
- [進階功能](docs/ADVANCED.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [更新日誌](CHANGELOG.md)

## 授權

MIT。詳見 [LICENSE](LICENSE)。
