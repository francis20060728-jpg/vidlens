# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [zhtw](zhtw.md) | [ja](ja.md) | [ko](ko.md) | [fr](fr.md) | [es](es.md) | [de](de.md)

Dê aos agentes de IA apenas de texto a capacidade de ver imagens e vídeos.

O VidLens roteia arquivos visuais através de um modelo de visão externo e retorna texto simples.

**Zero dependências pip para imagens.** Apenas a biblioteca padrão do Python 3 é necessária.

**Se seu modelo suporta visão nativamente, NÃO use VidLens.** É apenas para modelos de texto.

## Início: Servidor MCP (recomendado)

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
python vidlens/server.py
```

## Início: CLI (alternativa para agentes sem MCP)

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "O que há nesta imagem?"
```

## Licença

MIT. Veja [LICENSE](LICENSE).
