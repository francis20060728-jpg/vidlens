# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md)

---

Dê aos agentes de IA apenas de texto a capacidade de ver imagens e vídeos.

O VidLens roteia arquivos visuais através de um modelo de visão externo e retorna texto simples.

> **Se seu modelo suporta visão nativamente, NÃO use VidLens.** Apenas para modelos de texto.

## Como funciona

```
Imagem/Vídeo -> codificação base64 -> API de visão -> texto simples
```

## Requisitos

- [Python 3](https://python.org) (3.7+)
- Chave API de visão compatível com OpenAI
- (Opcional) [ffmpeg](https://ffmpeg.org)

## Início: Servidor MCP (recomendado)

MCP é a forma mais rápida de usar o VidLens.

```bash
# 1. Instalar
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. Configurar
python scripts/vidlens.py --init
# 3. Iniciar servidor MCP
python vidlens/server.py
```

Registrar em seu cliente MCP:

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

Três ferramentas: `look`, `list_media`, `find_and_look`.

## Início: CLI (alternativa sem MCP)

O resultado é impresso diretamente no stdout.

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "O que há nesta imagem?"
```

## Regra de uso automático (Codex)

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

Verifica primeiro a visão nativa: se o modelo vê imagens, VidLens é ignorado.

## Funcionalidades

- **Zero dependências para imagens**
- **Modo servidor MCP**
- **Failover de provedores** (até 9)
- **Suporte a modelos de raciocínio**
- **Fallback de OCR local**
- **Suporte a vídeo** (ffmpeg / opencv)
- **Modelos de prompt personalizados**
- **Multi-provedor**

## Configuração

| Chave | Padrão | Propósito |
|-----|-----|-----|
| `api_url` | `""` | URL base da API de visão |
| `api_key` | `""` | Chave API |
| `model_name` | `""` | Nome do modelo |
| `response_tokens` | `4000` | Tokens máx |
| `is_reasoning_model` | `false` | Modelos de raciocínio: true |

## Solução de problemas

| Problema | Solução |
|---------|---------|
| `NEEDS CONFIG` | Executar `--init`, preencher config.yaml |
| Vídeo falha | Instalar ffmpeg ou `pip install opencv-python numpy` |

## Documentação

- [Guia de instalação](docs/SETUP.md)
- [Recursos avançados](docs/ADVANCED.md)
- [Solução de problemas](docs/TROUBLESHOOTING.md)
- [Registro de alterações](CHANGELOG.md)

## Licença

MIT. Veja [LICENSE](LICENSE).
