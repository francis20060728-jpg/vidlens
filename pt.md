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

## Implantação em um clique (peça ao seu agente de IA)

Diga ao seu agente:

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

O agente clonará o repositório, executará --init e ajudará você a preencher config.yaml.

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

### Ferramentas MCP

| Ferramenta | Descrição | Argumentos principais |
|------|------|------|
| `look` | Analisa um único arquivo de imagem ou vídeo com o modelo de visão. Vídeos são automaticamente amostrados em uma folha de contato rotulada. | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | Encontra arquivos de imagem e vídeo em um diretório. Busca recursiva, filtragem por palavra-chave de nome de arquivo. Retorna caminhos absolutos ordenados com imagens primeiro. | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | Pesquisa um diretório por palavra-chave e depois analisa a melhor correspondência em uma chamada. Combinação conveniente de list_media + look. | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

Exemplo: `look(media_path="chart.png", prompt="O que este gráfico mostra?")`


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

## Contato

Tem alguma pergunta ou sugestão? Escreva para **francis20060728@gmail.com** e responderei em breve.
## Documentação

- [Guia de instalação](docs/SETUP.md)
- [Recursos avançados](docs/ADVANCED.md)
- [Solução de problemas](docs/TROUBLESHOOTING.md)
- [Registro de alterações](CHANGELOG.md)

## Licença

MIT. Veja [LICENSE](LICENSE).
