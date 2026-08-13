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

### Prerequisites

- [Python 3](https://python.org) installed (any version 3.7+)
- An OpenAI-compatible vision API key (gpt-4o, qwen-vl-max, gemini, etc.)
- (Optional) [ffmpeg](https://ffmpeg.org) for video support

### Quick Start

**Option A -- Let your AI agent do it (Codex / Claude Code / Cursor / Cline):**

> Install the vidlens skill from https://github.com/francis20060728-jpg/vidlens and configure it for me.

**Option B -- Manual setup:**

```bash
# 1. Clone
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens

# 2. Create config.yaml from template
python scripts/vidlens.py --init

# 3. Edit config.yaml (the path is printed above) and fill in:
#      api_url:     "https://api.openai.com/v1"
#      api_key:     "sk-your-key"
#      model_name:  "gpt-4o"

# 4. Verify setup
python scripts/vidlens.py --status

# 5. Look at an image
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

### Auto-Use Rule (optional)

By default, the agent decides when to use VidLens. If you want it to trigger
automatically whenever you receive an image, install the auto-use rule:

```bash
python scripts/vidlens.py --install-agents    # install (writes to ~/.codex/AGENTS.md)
python scripts/vidlens.py --remove-agents     # remove
python scripts/vidlens.py --status            # check status
```

The rule is transparent: it tells the agent to use VidLens and to inform
the user it used an external vision model. It does not hide anything.

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
| `NEEDS CONFIG` | Run `python scripts/vidlens.py --init`, fill in `config.yaml`, then `--status` |
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

### 前置条件

- 已安装 [Python 3](https://python.org)（3.7+ 任意版本）
- 一个 OpenAI 兼容的视觉 API 密钥（gpt-4o、qwen-vl-max、gemini 等）
- （可选）[ffmpeg](https://ffmpeg.org) 用于视频支持

### 快速开始

**方式一 -- 让 AI 智能体帮你（Codex / Claude Code / Cursor / Cline）：**

> 从 https://github.com/francis20060728-jpg/vidlens 安装 vidlens 技能并帮我配置好。

**方式二 -- 手动安装：**

```bash
# 1. 克隆
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens

# 2. 从模板创建 config.yaml
python scripts/vidlens.py --init

# 3. 编辑 config.yaml（路径在上面已打印），填入：
#      api_url:     "https://api.openai.com/v1"
#      api_key:     "sk-your-key"
#      model_name:  "gpt-4o"

# 4. 验证配置
python scripts/vidlens.py --status

# 5. 看一张图片
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

### 自动使用规则（可选）

默认情况下，智能体自行决定何时使用 VidLens。如果你希望收到图片时自动触发，安装自动规则：

```bash
python scripts/vidlens.py --install-agents   # 安装（写入 ~/.codex/AGENTS.md）
python scripts/vidlens.py --remove-agents    # 移除
python scripts/vidlens.py --status           # 查看状态
```

规则是透明的：它会告诉智能体使用 VidLens 并告知用户使用了外部视觉模型。

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

### 安裝

**或讓 AI 智慧體安裝（Codex / Claude Code / Cursor / Cline）：** 直接對它說「從 https://github.com/francis20060728-jpg/vidlens 安裝 vidlens 技能」。

**手動安裝：**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # 建立 config.yaml
# 編輯 config.yaml，填入 api_url、api_key、model_name
python scripts/vidlens.py --status  # 驗證設定
```

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

### インストール

**または AI エージェントにインストールさせる（Codex / Claude Code / Cursor / Cline）：**「https://github.com/francis20060728-jpg/vidlens から vidlens スキルをインストールして」と伝えるだけ。

**手動インストール：**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # config.yaml を作成
# config.yaml を編集: api_url, api_key, model_name
python scripts/vidlens.py --status  # 設定を確認
```

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

### 설치

**또는 AI 에이전트에게 설치시키기 (Codex / Claude Code / Cursor / Cline):** "https://github.com/francis20060728-jpg/vidlens에서 vidlens 스킬을 설치해 줘"라고 말하세요.

**수동 설치:**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # config.yaml 생성
# config.yaml 편집: api_url, api_key, model_name
python scripts/vidlens.py --status  # 설정 확인
```

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

### Installation

**Ou laissez votre agent IA le faire (Codex / Claude Code / Cursor / Cline) :** dites-lui simplement « Installe le skill vidlens depuis https://github.com/francis20060728-jpg/vidlens ».

**Installation manuelle :**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # Crée config.yaml
# Éditez config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status  # Vérifier la configuration
```

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

### Instalación

**O deja que tu agente de IA lo instale (Codex / Claude Code / Cursor / Cline):** simplemente dile « Instala el skill vidlens desde https://github.com/francis20060728-jpg/vidlens ».

**Instalación manual:**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # Crea config.yaml
# Edita config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status  # Verificar configuración
```

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

### Installation

**Oder lassen Sie Ihren KI-Agenten installieren (Codex / Claude Code / Cursor / Cline):** Sagen Sie einfach „Installiere das vidlens Skill von https://github.com/francis20060728-jpg/vidlens".

**Manuelle Installation:**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # Erstellt config.yaml
# config.yaml bearbeiten: api_url, api_key, model_name
python scripts/vidlens.py --status  # Konfiguration überprüfen
```

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

### Instalação

**Ou deixe seu agente de IA instalar (Codex / Claude Code / Cursor / Cline):** basta dizer « Instale o skill vidlens de https://github.com/francis20060728-jpg/vidlens ».

**Instalação manual:**

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init    # Cria config.yaml
# Edite config.yaml: api_url, api_key, model_name
python scripts/vidlens.py --status  # Verificar configuração
```

### Uso

```bash
python scripts/vidlens.py screenshot.png "Os elementos da interface estão alinhados?"
python scripts/vidlens.py video.mp4 "Descreva o movimento do vídeo"
python scripts/vidlens.py a.png b.png --task "Compare estes dois designs"
```

### Licença

MIT. Veja [LICENSE](LICENSE).
