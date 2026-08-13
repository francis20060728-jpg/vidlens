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
python scripts/vidlens.py --install-agents    # auto-detects Codex, Claude Code, Cursor
python scripts/vidlens.py --remove-agents     # remove from all
python scripts/vidlens.py --status            # check per-agent status
```

The rule is transparent: it tells the agent to check first if it can see
natively, and if not, use VidLens and inform the user. It does not hide
anything.

**Using a different agent?** (opencode, zcode, mimocode, etc.) VidLens is
agent-agnostic. Write the rule to any config file:

```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

# Direct URL to an image/video (auto-downloaded)
python scripts/vidlens.py https://example.com/photo.jpg "What is this?"

# Check if a web page looks broken (use verify_page prompt)
python scripts/vidlens.py screenshot.png --prompt-name verify_page
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
| `is_reasoning_model` | false | Set true for thinking models (mimo-v2.5, o1, deepseek-r1) |

Any OpenAI-compatible vision API works (gpt-4o, qwen-vl-max, gemini, etc.).

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `python: command not found` | Use the launcher (`vidlens.cmd` / `vidlens.sh`) or add Python to PATH |
| `NEEDS CONFIG` | Run `python scripts/vidlens.py --init`, fill in `config.yaml`, then `--status` |
| Video fails | Install ffmpeg (preferred) or `pip install opencv-python numpy` |
| All providers failed | A local OCR fallback kicks in for images; check your API key/URL |
| Chinese path garbled | Fixed since v1.2 -- stdout/stderr forced to UTF-8 on Windows |
| Very slow / appears stuck | Model may be a reasoning model (thinking before answering); VidLens auto-retries with more tokens, or set `is_reasoning_model: true` |

### MCP Server Mode

For Claude Desktop, Cursor, Cline:

```bash
pip install mcp opencv-python numpy
python vidlens/server.py
```

Three tools: `look`, `list_media`, `find_and_look`.

### License

MIT. See [LICENSE](LICENSE).

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

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
python scripts/vidlens.py --install-agents   # 自动检测 Codex、Claude Code、Cursor
python scripts/vidlens.py --remove-agents    # 从全部移除
python scripts/vidlens.py --status           # 查看各 agent 状态
```

规则是透明的：它要求智能体先检查自己能否原生看图，如果不能就用 VidLens，
并告知用户使用了外部视觉模型。

**使用其他智能体？**（opencode、zcode、mimocode 等）VidLens 与 agent 无关，
可以写入任意配置文件：

```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### 自動使用規則（可選）

預設情況下，智慧體自行決定何時使用 VidLens。如果你希望收到圖片或網址時自動觸發：

```bash
python scripts/vidlens.py --install-agents   # 自動偵測 Codex、Claude Code、Cursor
python scripts/vidlens.py --remove-agents    # 從全部移除
```

規則要求智慧體先檢查自己能否原生看圖，不能就用 VidLens，並告知使用者。

**其他智慧體？**（opencode、zcode、mimocode 等）VidLens 與 agent 無關：
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### 自動使用ルール（オプション）

デフォルトでは、エージェントが VidLens の使用タイミングを判断します。画像や URL 受信時に自動トリガーしたい場合：

```bash
python scripts/vidlens.py --install-agents   # Codex、Claude Code、Cursor を自動検出
python scripts/vidlens.py --remove-agents    # すべてから削除
```

ルールは透明性を保ちます：ネイティブで表示できるか確認し、できない場合は VidLens を使用し、ユーザーに通知します。

**他のエージェント？**（opencode、zcode、mimocode 等）VidLens はエージェント非依存です：
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### 자동 사용 규칙 (선택)

기본적으로 에이전트가 VidLens 사용 시점을 결정합니다. 이미지나 URL 수신 시 자동 트리거하려면:

```bash
python scripts/vidlens.py --install-agents   # Codex, Claude Code, Cursor 자동 감지
python scripts/vidlens.py --remove-agents    # 전체에서 제거
```

규칙은 투명합니다: 네이티브로 볼 수 있는지 먼저 확인하고, 없으면 VidLens를 사용하며 사용자에게 알립니다.

**다른 에이전트?** (opencode, zcode, mimocode 등) VidLens는 에이전트 독립적입니다:
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### Règle d'utilisation automatique (optionnel)

Par défaut, l'agent décide quand utiliser VidLens. Pour un déclenchement automatique à réception d'image ou d'URL :

```bash
python scripts/vidlens.py --install-agents   # détecte Codex, Claude Code, Cursor
python scripts/vidlens.py --remove-agents    # supprimer de tous
```

La règle est transparente : l'agent vérifie d'abord s'il peut voir nativement, sinon utilise VidLens et informe l'utilisateur.

**Autre agent ?** (opencode, zcode, mimocode, etc.) VidLens est indépendant de l'agent :
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### Regla de uso automático (opcional)

Por defecto, el agente decide cuándo usar VidLens. Para activarlo automáticamente al recibir una imagen o URL:

```bash
python scripts/vidlens.py --install-agents   # detecta Codex, Claude Code, Cursor
python scripts/vidlens.py --remove-agents    # eliminar de todos
```

La regla es transparente: el agente verifica primero si puede ver nativamente, si no, usa VidLens e informa al usuario.

¿Otro agente? (opencode, zcode, mimocode, etc.) VidLens es independiente del agente:
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### Auto-Verwendungsregel (optional)

Standardmäßig entscheidet der Agent, wann VidLens verwendet wird. Für automatische Auslösung beim Empfang von Bildern oder URLs:

```bash
python scripts/vidlens.py --install-agents   # erkennt Codex, Claude Code, Cursor
python scripts/vidlens.py --remove-agents    # von allen entfernen
```

Die Regel ist transparent: Der Agent prüft zuerst, ob er nativ sehen kann, verwendet sonst VidLens und informiert den Nutzer.

Anderer Agent? (opencode, zcode, mimocode, etc.) VidLens ist agentenunabhängig:
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
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

### Regra de uso automático (opcional)

Por padrão, o agente decide quando usar o VidLens. Para acionamento automático ao receber imagem ou URL:

```bash
python scripts/vidlens.py --install-agents   # detecta Codex, Claude Code, Cursor
python scripts/vidlens.py --remove-agents    # remover de todos
```

A regra é transparente: o agente verifica primeiro se pode ver nativamente, se não, usa VidLens e informa o usuário.

Outro agente? (opencode, zcode, mimocode, etc.) VidLens é independente do agente:
```bash
python scripts/vidlens.py --install-agents --path ~/.youragent/rules.md
```

### Licença

MIT. Veja [LICENSE](LICENSE).
