# VidLens

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文) | [日本語](#日本語) | [한국어](#한국어) | [Français](#français) | [Español](#español) | [Deutsch](#deutsch) | [Português](#português)

---

## English

Give text-only AI agents the ability to see images and videos.

VidLens routes visual files through an external vision model and returns
plain text. Any agent -- Codex, Claude Code, Cursor, Cline -- can inspect,
verify, and respond to visual content without native image support.

**Zero pip dependencies for images.** Only Python 3 stdlib required.
Videos use ffmpeg (system binary) if available; opencv is an optional fallback.

### Quick Start

```bash
# 1. Configure (edit config.yaml next to SKILL.md)
cp config.example.yaml config.yaml
# Fill in: api_url, api_key, model_name

# 2. Install anti-rejection rule (so the agent never says "I can't see")
python scripts/vidlens.py --install-agents
# Restart your agent

# 3. Look at an image
python scripts/vidlens.py photo.png "What's in this image?"
```

The script prints `output_path=<file>`. Read that file for the full description.

### How It Works

```
Image -> base64 encode -> Vision API -> Markdown file -> output_path=
Video -> ffmpeg compress -> base64 encode -> Vision API -> Markdown file
         (or opencv contact sheet if ffmpeg absent)
```

VidLens does NOT replace your main model. It only activates when vision is
needed. The sidebar still shows your text model.

### Anti-Rejection

Text-only agents often refuse images ("this model does not support image
input"). VidLens prevents this:

```bash
# Write a rule into ~/.codex/AGENTS.md (idempotent, won't touch other rules)
python scripts/vidlens.py --install-agents

# Remove it later
python scripts/vidlens.py --remove-agents

# Check status
python scripts/vidlens.py --status
```

### Usage

```bash
# Single image (zero dependencies)
python scripts/vidlens.py screenshot.png "Are the UI elements aligned?"

# Named prompt template
python scripts/vidlens.py result.png --prompt-name verify_output

# Video (needs ffmpeg or opencv)
python scripts/vidlens.py video.mp4 "Describe the motion"

# Multiple images
python scripts/vidlens.py a.png b.png --task "Compare these two designs"

# Save to specific path
python scripts/vidlens.py image.png -o report.md
```

Or use the launcher (auto-finds Python):

```bash
vidlens.cmd image.png "What is this?"     # Windows
./vidlens.sh image.png "What is this?"     # macOS/Linux
```

**Question syntax:** You can pass the question as a trailing positional arg
or via `--task`. Both work:

```bash
python scripts/vidlens.py image.png "What is this?"         # positional
python scripts/vidlens.py image.png --task "What is this?"  # explicit flag
```

### Custom Prompts

Drop `.txt` files in `prompts/` for reusable templates:

```bash
python scripts/vidlens.py output/stage1.mp4 --prompt-name stage1_detection
```

Built-in: `describe`, `verify_output`, `quality_check`, `object_inventory`,
`compare_frames`. See [prompts/CUSTOMIZE.md](prompts/CUSTOMIZE.md).

### Config

| Key | Default | Purpose |
|-----|---------|---------|
| `api_url` | "" | Vision API base URL |
| `api_key` | "" | API key |
| `model_name` | "" | Model name |
| `fallback_N_url` | "" | Fallback provider N URL (N = 1-9) |
| `fallback_N_key` | "" | Fallback provider N API key |
| `fallback_N_model` | "" | Fallback provider N model |
| `response_tokens` | 4000 | Max response tokens |
| `sampling_temp` | 0.1 | Temperature |
| `http_timeout` | 120 | Seconds |

Any OpenAI-compatible vision API works (gpt-4o, qwen-vl-max, gemini, etc.).

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `python: command not found` | Use the launcher (`vidlens.cmd` / `vidlens.sh`) or add Python to PATH |
| `NEEDS CONFIG` | Run `python scripts/vidlens.py --status`, then edit `config.yaml` |
| Video fails | Install ffmpeg (preferred) or `pip install opencv-python numpy` |
| All providers failed | A local OCR fallback kicks in for images; check your API key/URL |
| Chinese path garbled | Fixed since v1.2 -- stdout/stderr forced to UTF-8 on Windows |

### MCP Server Mode

For Claude Desktop, Cursor, Cline:

```bash
pip install mcp opencv-python numpy
python vidlens/server.py
```

Three tools: `look`, `list_media`, `find_and_look`.

### License

MIT. See [LICENSE](LICENSE).

---

## 简体中文

让纯文本 AI 智能体拥有「看」图片和视频的能力。

VidLens 将视觉文件路由到外部视觉模型，返回纯文本。任何智能体 -- Codex、Claude Code、Cursor、Cline -- 无需原生图像支持即可检查、验证和响应视觉内容。

**图片分析零依赖。** 只需 Python 3 标准库。视频可用 ffmpeg（系统二进制），opencv 为可选回退。

### 快速开始

```bash
cp config.example.yaml config.yaml  # 填入 api_url、api_key、model_name
python scripts/vidlens.py --install-agents  # 安装反拒绝规则
python scripts/vidlens.py photo.png "图片里有什么？"
```

脚本会打印 `output_path=<文件>`，读取该文件获取完整描述。

### 工作原理

```
图片 -> base64 编码 -> 视觉 API -> Markdown 文件 -> output_path=
视频 -> ffmpeg 压缩 -> base64 编码 -> 视觉 API -> Markdown 文件
       （无 ffmpeg 时用 opencv 拼接联系表）
```

VidLens 不会替换你的主模型。它只在需要视觉时激活。

### 反拒绝机制

纯文本智能体经常拒绝图片（"此模型不支持图像输入"）。VidLens 防止这种情况：

```bash
python scripts/vidlens.py --install-agents   # 写入 ~/.codex/AGENTS.md
python scripts/vidlens.py --remove-agents    # 移除
python scripts/vidlens.py --status           # 查看状态
```

### 用法

```bash
python scripts/vidlens.py screenshot.png "界面元素对齐了吗？"
python scripts/vidlens.py video.mp4 "描述视频中的运动"
python scripts/vidlens.py a.png b.png --task "比较这两个设计"
python scripts/vidlens.py image.png -o report.md
```

### 配置

| 键 | 默认值 | 用途 |
|----|--------|------|
| `api_url` | "" | 视觉 API 地址 |
| `api_key` | "" | API 密钥 |
| `model_name` | "" | 模型名称 |
| `fallback_N_url` | "" | 备用提供商 N 的地址 (N = 1-9) |
| `fallback_N_key` | "" | 备用提供商 N 的密钥 |
| `fallback_N_model` | "" | 备用提供商 N 的模型 |
| `response_tokens` | 4000 | 最大响应 token |
| `sampling_temp` | 0.1 | 温度 |
| `http_timeout` | 120 | 超时秒数 |

任何 OpenAI 兼容的视觉 API 均可（gpt-4o、qwen-vl-max、gemini 等）。

### 许可证

MIT。详见 [LICENSE](LICENSE)。

---

## 繁體中文

讓純文字 AI 智慧體擁有「看」圖片和影片的能力。

VidLens 將視覺檔案路由到外部視覺模型，回傳純文字。任何智慧體 -- Codex、Claude Code、Cursor、Cline -- 無需原生影像支援即可檢查、驗證和回應視覺內容。

**圖片分析零依賴。** 只需 Python 3 標準庫。影片可用 ffmpeg（系統二進位），opencv 為可選回退。

### 快速開始

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "圖片裡有什麼？"
```

### 工作原理

```
圖片 -> base64 編碼 -> 視覺 API -> Markdown 檔案
影片 -> ffmpeg 壓縮 -> base64 編碼 -> 視覺 API -> Markdown 檔案
```

VidLens 不會替換你的主模型。它只在需要視覺時啟用。

### 用法

```bash
python scripts/vidlens.py screenshot.png "介面元素對齊了嗎？"
python scripts/vidlens.py video.mp4 "描述影片中的運動"
python scripts/vidlens.py a.png b.png --task "比較這兩個設計"
```

### 許可證

MIT。詳見 [LICENSE](LICENSE)。

---

## 日本語

テキスト専用 AI エージェントに画像と動画を見る能力を与えます。

VidLens は視覚ファイルを外部のビジョンモデルにルーティングし、プレーンテキストを返します。Codex、Claude Code、Cursor、Cline など、ネイティブ画像サポートなしで視覚コンテンツを検査、検証、応答できます。

**画像分析はゼロ依存。** Python 3 標準ライブラリのみ必要。動画は ffmpeg（システムバイナリ）を使用、opencv はオプションのフォールバック。

### クイックスタート

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "この画像には何がありますか？"
```

### 仕組み

```
画像 -> base64 エンコード -> ビジョン API -> Markdown ファイル
動画 -> ffmpeg 圧縮 -> base64 エンコード -> ビジョン API -> Markdown ファイル
```

VidLens はメインモデルを置き換えません。必要な時にのみ動作します。

### 使い方

```bash
python scripts/vidlens.py screenshot.png "UI 要素は整列していますか？"
python scripts/vidlens.py video.mp4 "動画の動きを説明してください"
python scripts/vidlens.py a.png b.png --task "この2つのデザインを比較してください"
```

### ライセンス

MIT。[LICENSE](LICENSE) を参照してください。

---

## 한국어

텍스트 전용 AI 에이전트에게 이미지와 비디오를 볼 수 있는 능력을 부여합니다.

VidLens는 시각 파일을 외부 비전 모델로 라우팅하여 일반 텍스트로 반환합니다. Codex, Claude Code, Cursor, Cline 등 네이티브 이미지 지원 없이도 시각 콘텐츠를 검사, 검증, 응답할 수 있습니다.

**이미지 분석은 종속성 제로.** Python 3 표준 라이브러리만 필요. 비디오는 ffmpeg(시스템 바이너리)를 사용하며, opencv는 선택적 폴백입니다.

### 빠른 시작

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "이 이미지에 무엇이 있나요?"
```

### 작동 방식

```
이미지 -> base64 인코딩 -> 비전 API -> Markdown 파일
비디오 -> ffmpeg 압축 -> base64 인코딩 -> 비전 API -> Markdown 파일
```

VidLens는 메인 모델을 교체하지 않습니다. 비전이 필요할 때만 작동합니다.

### 사용법

```bash
python scripts/vidlens.py screenshot.png "UI 요소가 정렬되어 있나요?"
python scripts/vidlens.py video.mp4 "비디오의 움직임을 설명해 주세요"
python scripts/vidlens.py a.png b.png --task "이 두 디자인을 비교해 주세요"
```

### 라이선스

MIT. [LICENSE](LICENSE)를 참조하세요.

---

## Français

Donnez aux agents IA en mode texte uniquement la capacité de voir images et vidéos.

VidLens achemine les fichiers visuels via un modèle de vision externe et renvoie du texte brut. Tout agent -- Codex, Claude Code, Cursor, Cline -- peut inspecter, vérifier et répondre au contenu visuel sans support d'image natif.

**Zéro dépendance pip pour les images.** Seule la bibliothèque standard Python 3 est requise. Les vidéos utilisent ffmpeg (binaire système) ; opencv est un repli optionnel.

### Démarrage rapide

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "Que contient cette image ?"
```

### Fonctionnement

```
Image -> encodage base64 -> API de vision -> fichier Markdown
Vidéo -> compression ffmpeg -> encodage base64 -> API de vision -> fichier Markdown
```

VidLens ne remplace pas votre modèle principal. Il ne s'active que lorsque la vision est nécessaire.

### Utilisation

```bash
python scripts/vidlens.py screenshot.png "Les éléments d'interface sont-ils alignés ?"
python scripts/vidlens.py video.mp4 "Décrivez le mouvement de la vidéo"
python scripts/vidlens.py a.png b.png --task "Comparez ces deux conceptions"
```

### Licence

MIT. Voir [LICENSE](LICENSE).

---

## Español

Da a los agentes de IA de solo texto la capacidad de ver imágenes y videos.

VidLens enruta archivos visuales a través de un modelo de visión externo y devuelve texto sin formato. Cualquier agente -- Codex, Claude Code, Cursor, Cline -- puede inspeccionar, verificar y responder a contenido visual sin soporte nativo de imágenes.

**Cero dependencias pip para imágenes.** Solo se requiere la biblioteca estándar de Python 3. Los videos usan ffmpeg (binario del sistema); opencv es un respaldo opcional.

### Inicio rápido

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "¿Qué hay en esta imagen?"
```

### Cómo funciona

```
Imagen -> codificación base64 -> API de visión -> archivo Markdown
Vídeo -> compresión ffmpeg -> codificación base64 -> API de visión -> archivo Markdown
```

VidLens no reemplaza tu modelo principal. Solo se activa cuando se necesita visión.

### Uso

```bash
python scripts/vidlens.py screenshot.png "¿Están alineados los elementos de la interfaz?"
python scripts/vidlens.py video.mp4 "Describe el movimiento del video"
python scripts/vidlens.py a.png b.png --task "Compara estos dos diseños"
```

### Licencia

MIT. Ver [LICENSE](LICENSE).

---

## Deutsch

Geben Sie KI-Agenten im Nur-Text-Modus die Fähigkeit, Bilder und Videos zu sehen.

VidLens leitet visuelle Dateien über ein externes Vision-Modell und gibt reinen Text zurück. Jeder Agent -- Codex, Claude Code, Cursor, Cline -- kann visuelle Inhalte prüfen, verifizieren und beantworten, ohne native Bildunterstützung.

**Keine pip-Abhängigkeiten für Bilder.** Nur die Python-3-Standardbibliothek wird benötigt. Videos verwenden ffmpeg (Systembinärdatei); opencv ist ein optionaler Fallback.

### Schnellstart

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "Was ist auf diesem Bild?"
```

### Funktionsweise

```
Bild -> base64-Kodierung -> Vision-API -> Markdown-Datei
Video -> ffmpeg-Komprimierung -> base64-Kodierung -> Vision-API -> Markdown-Datei
```

VidLens ersetzt nicht Ihr Hauptmodell. Es wird nur aktiviert, wenn Bilderkennung benötigt wird.

### Verwendung

```bash
python scripts/vidlens.py screenshot.png "Sind die UI-Elemente ausgerichtet?"
python scripts/vidlens.py video.mp4 "Beschreibe die Bewegung im Video"
python scripts/vidlens.py a.png b.png --task "Vergleiche diese beiden Designs"
```

### Lizenz

MIT. Siehe [LICENSE](LICENSE).

---

## Português

Dê aos agentes de IA apenas de texto a capacidade de ver imagens e vídeos.

O VidLens roteia arquivos visuais através de um modelo de visão externo e retorna texto simples. Qualquer agente -- Codex, Claude Code, Cursor, Cline -- pode inspecionar, verificar e responder a conteúdo visual sem suporte nativo de imagem.

**Zero dependências pip para imagens.** Apenas a biblioteca padrão do Python 3 é necessária. Vídeos usam ffmpeg (binário do sistema); opencv é um fallback opcional.

### Início rápido

```bash
cp config.example.yaml config.yaml
python scripts/vidlens.py --install-agents
python scripts/vidlens.py photo.png "O que há nesta imagem?"
```

### Como funciona

```
Imagem -> codificação base64 -> API de visão -> arquivo Markdown
Vídeo -> compactação ffmpeg -> codificação base64 -> API de visão -> arquivo Markdown
```

O VidLens não substitui seu modelo principal. Ele só é ativado quando a visão é necessária.

### Uso

```bash
python scripts/vidlens.py screenshot.png "Os elementos da interface estão alinhados?"
python scripts/vidlens.py video.mp4 "Descreva o movimento do vídeo"
python scripts/vidlens.py a.png b.png --task "Compare estes dois designs"
```

### Licença

MIT. Veja [LICENSE](LICENSE).