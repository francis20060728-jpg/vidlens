# VidLens

[English](en.md) | [en](en.md) | [zhtw](zhtw.md) | [ja](ja.md) | [ko](ko.md) | [fr](fr.md) | [es](es.md) | [de](de.md) | [pt](pt.md)

让纯文本 AI 智能体拥有「看」图片和视频的能力。

VidLens 将视觉文件路由到外部视觉模型，返回纯文本。任何智能体无需原生图像支持即可检查和响应视觉内容。

**图片分析零依赖。** 只需 Python 3 标准库。视频可用 ffmpeg，opencv 为可选回退。

**如果你的模型本身支持视觉，请不要使用 VidLens。** 它只用于无法看图的纯文本模型。

## 前置条件

- 已安装 [Python 3](https://python.org)（3.7+）
- 一个 OpenAI 兼容的视觉 API 密钥
- （可选）[ffmpeg](https://ffmpeg.org) 用于视频支持

## 快速开始：MCP 服务器（推荐）

MCP 是使用 VidLens 最快的方式——无进程启动、无沙箱延迟。

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init     # 创建 config.yaml
# 编辑 config.yaml: api_url, api_key, model_name
python vidlens/server.py             # 启动 MCP 服务器
```

在 MCP 客户端（Claude Desktop、Cursor、Cline）中注册：

```json
{
  "mcpServers": {
    "vidlens": {
      "command": "python",
      "args": ["/绝对路径/vidlens/vidlens/server.py"]
    }
  }
}
```

三个工具：`look`、`list_media`、`find_and_look`。

## 快速开始：CLI（不支持 MCP 的 agent 的备选）

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init     # 创建 config.yaml
# 编辑 config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status   # 验证
python scripts/vidlens.py photo.png "图片里有什么？"
```

## 自动使用规则（Codex / Claude Code）

```bash
python scripts/vidlens.py --install-agents   # 自动检测 agent 配置
python scripts/vidlens.py --remove-agents    # 从全部移除
```

规则会先检查原生视觉：如果模型能看图就跳过 VidLens。只有纯文本模型才触发。

## 配置

| 键 | 默认值 | 用途 |
|----|--------|------|
| `api_url` | "" | 视觉 API 地址 |
| `api_key` | "" | API 密钥 |
| `model_name` | "" | 模型名称 |
| `response_tokens` | 4000 | 最大响应 token |
| `is_reasoning_model` | false | 推理模型设 true |

任何 OpenAI 兼容的视觉 API 均可。

## 许可证

MIT。详见 [LICENSE](LICENSE)。
