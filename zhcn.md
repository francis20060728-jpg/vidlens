# VidLens

[English](README.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

让纯文本 AI 智能体拥有「看」图片和视频的能力。

VidLens 将视觉文件路由到外部视觉模型，返回纯文本。任何智能体 -- Codex、Claude Code、Cursor、Cline -- 无需原生图像支持即可检查、验证和响应视觉内容。

> **如果当前模型/提供商明确是多模态，请使用原生视觉。** 纯文本或能力未知时，VidLens 使用外部视觉并只返回文本。

## 工作原理

```
图片/视频 -> base64 编码 -> 视觉 API -> 纯文本结果
```

## 一键部署（告诉你的 AI 智能体）

告诉你的智能体：

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

智能体会克隆仓库、运行 --init，并帮你填写 config.yaml。

## 前置条件

- 已安装 [Python 3](https://python.org)（3.7+）
- 一个 OpenAI 兼容的视觉 API 密钥（gpt-4o、qwen-vl-max、gemini 等）
- （可选）[ffmpeg](https://ffmpeg.org) 用于视频支持

## 快速开始：MCP 服务器（推荐）

MCP 是使用 VidLens 最快的方式——无进程启动、无沙箱延迟。

```bash
# 1. 安装
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. 配置
python scripts/vidlens.py --init
# 编辑 config.yaml: api_url, api_key, model_name
# 3. 启动 MCP 服务器
python vidlens/server.py
```

在 MCP 客户端（Claude Desktop、Cursor、Cline）中注册：

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

| 工具 | 描述 | 主要参数 |
|------|------|------|
| `look` | 用视觉模型分析单个图片或视频文件。视频自动采样为带标注的联系表。 | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | 查找目录中的图片和视频文件。递归搜索，按文件名关键词过滤。返回按图片优先排序的绝对路径。 | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | 按关键词搜索目录，然后一次调用分析最佳匹配。list_media + look 的便捷组合。 | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

示例：`look(media_path="chart.png", prompt="这张图显示了什么？")`


## 快速开始：CLI（不支持 MCP 的 agent 的备选）

结果直接打印到 stdout，无需读取单独的文件。

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
# 编辑 config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "图片里有什么？"
```

## 自动使用规则（Codex）

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

规则会先确认实际模型/提供商能力。明确多模态的模型使用原生视觉，并可将路径加载到原生输入；纯文本或能力未知时由 VidLens 返回纯文本。原生图像请求被拒绝后不会重试。

## 功能

- **图片零依赖**（仅 Python 标准库）
- **MCP 服务器模式**（Claude Desktop、Cursor、Cline）
- **多提供商故障转移**（最多 9 个备用）
- **推理模型支持**（自动检测思考型模型）
- **本地 OCR 回退**（Windows OCR / Tesseract）
- **视频支持**（ffmpeg 或 opencv 联系表回退）
- **自定义 prompt 模板**（放 .txt 到 prompts/）
- **多提供商**：任何 OpenAI 兼容的视觉 API

## 配置

| 键 | 默认值 | 用途 |
|-----|-----|-----|
| `api_url` | `""` | 视觉 API 地址 |
| `api_key` | `""` | API 密钥 |
| `model_name` | `""` | 模型名称 |
| `response_tokens` | `1200` | 最大响应 token |
| `verification_tokens` | `350` | PASS/FAIL 验证用更短预算 |
| `http_timeout` | `45` | 单次请求超时 |
| `total_timeout` | `60` | 总超时 |
| `reasoning_effort` | `""` | 可选推理强度 |
| `max_image_side` | `1600` | 图片最大边长 |
| `image_jpeg_quality` | `90` | JPEG 质量 |
| `sampling_temp` | `0.1` | 温度（0.1 精确，0.7 创意） |
| `is_reasoning_model` | `false` | 推理模型设 true |
| `fallback_N_url` | `""` | 备用提供商 N 地址 |

## 故障排除

| 问题 | 修复 |
|---------|---------|
| `NEEDS CONFIG` | 运行 `--init`，填 config.yaml，然后 `--status` |
| `python: not found` | 用启动器（`vidlens.cmd` / `vidlens.sh`） |
| 视频失败 | 安装 ffmpeg 或 `pip install opencv-python numpy` |
| 首次运行慢 | 沙箱在审批网络——只发生一次 |

## 反馈

有问题或建议？发邮件到 **francis20060728@gmail.com**，我会尽快处理。
## 文档

- [安装指南](docs/SETUP.md)
- [高级功能](docs/ADVANCED.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [测试与边界](docs/TESTING.md)
- [更新日志](CHANGELOG.md)
- [版本发布](https://github.com/francis20060728-jpg/vidlens/releases)
- [开发指南](DEV_GUIDE.md)

## 许可证

MIT。详见 [LICENSE](LICENSE)。
