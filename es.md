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

## Despliegue en un clic (pídele a tu agente IA)

Dile a tu agente:

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

El agente clonará el repositorio, ejecutará --init y te ayudará a completar config.yaml.

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

### Herramientas MCP

| Herramienta | Descripción | Argumentos clave |
|------|------|------|
| `look` | Analiza un archivo individual de imagen o video con el modelo de visión. Los videos se muestrean automáticamente en una hoja de contacto etiquetada. | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | Encuentra archivos de imagen y video en un directorio. Búsqueda recursiva, filtrado por palabra clave de nombre de archivo. Devuelve rutas absolutas ordenadas con imágenes primero. | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | Busca en un directorio por palabra clave y luego analiza la mejor coincidencia en una llamada. Combinación conveniente de list_media + look. | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

Ejemplo: `look(media_path="chart.png", prompt="¿Qué muestra este gráfico?")`


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

## Contacto

¿Tienes una pregunta o sugerencia? Escribe a **francis20060728@gmail.com** y responderé pronto.
## Documentación

- [Guía de instalación](docs/SETUP.md)
- [Funciones avanzadas](docs/ADVANCED.md)
- [Solución de problemas](docs/TROUBLESHOOTING.md)
- [Registro de cambios](CHANGELOG.md)

## Licencia

MIT. Ver [LICENSE](LICENSE).
