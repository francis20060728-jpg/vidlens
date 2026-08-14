# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [zhtw](zhtw.md) | [ja](ja.md) | [ko](ko.md) | [fr](fr.md) | [de](de.md) | [pt](pt.md)

Da a los agentes de IA de solo texto la capacidad de ver imágenes y videos.

VidLens enruta archivos visuales a través de un modelo de visión externo y devuelve texto sin formato.

**Cero dependencias pip para imágenes.** Solo se requiere la biblioteca estándar de Python 3.

**Si tu modelo soporta visión nativamente, NO uses VidLens.** Es solo para modelos de solo texto.

## Inicio: Servidor MCP (recomendado)

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
python vidlens/server.py
```

## Inicio: CLI (respaldo para agentes sin MCP)

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "¿Qué hay en esta imagen?"
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
