# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Deutsch](de.md) | [Português](pt.md)

---

Da a los agentes de IA de solo texto la capacidad de ver imágenes y videos.

VidLens enruta archivos visuales a través de un modelo de visión externo y devuelve texto sin formato.

> **Si tu modelo soporta visión nativamente, NO uses VidLens.** Solo para modelos de texto.

## Cómo funciona

```
Imagen/Video -> codificación base64 -> API de visión -> texto sin formato
```

## Requisitos

- [Python 3](https://python.org) (3.7+)
- Clave API de visión compatible con OpenAI
- (Opcional) [ffmpeg](https://ffmpeg.org)

## Inicio: Servidor MCP (recomendado)

MCP es la forma más rápida de usar VidLens.

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

Registrar en tu cliente MCP:

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

Tres herramientas: `look`, `list_media`, `find_and_look`.

## Inicio: CLI (respaldo sin MCP)

El resultado se imprime directamente en stdout.

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "¿Qué hay en esta imagen?"
```

## Regla de uso automático (Codex)

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

Verifica primero la visión nativa: si el modelo ve imágenes, VidLens se omite.

## Características

- **Cero dependencias para imágenes**
- **Modo servidor MCP**
- **Conmutación de proveedores** (hasta 9)
- **Soporte de modelos de razonamiento**
- **Respaldo OCR local**
- **Soporte de video** (ffmpeg / opencv)
- **Plantillas de prompt personalizadas**
- **Multi-proveedor**

## Configuración

| Clave | Predeterminado | Propósito |
|-----|-----|-----|
| `api_url` | `""` | URL base API de visión |
| `api_key` | `""` | Clave API |
| `model_name` | `""` | Nombre del modelo |
| `response_tokens` | `4000` | Tokens máx |
| `is_reasoning_model` | `false` | Modelos de razonamiento: true |

## Solución de problemas

| Problema | Solución |
|---------|---------|
| `NEEDS CONFIG` | Ejecutar `--init`, llenar config.yaml |
| Video falla | Instalar ffmpeg o `pip install opencv-python numpy` |

## Documentación

- [Guía de instalación](docs/SETUP.md)
- [Funciones avanzadas](docs/ADVANCED.md)
- [Solución de problemas](docs/TROUBLESHOOTING.md)
- [Registro de cambios](CHANGELOG.md)

## Licencia

MIT. Ver [LICENSE](LICENSE).
