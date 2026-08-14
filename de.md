# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Français](fr.md) | [Español](es.md) | [Português](pt.md)

---

Geben Sie KI-Agenten im Nur-Text-Modus die Fähigkeit, Bilder und Videos zu sehen.

VidLens leitet visuelle Dateien über ein externes Vision-Modell und gibt reinen Text zurück.

> **Wenn Ihr Modell nativ Vision unterstützt, verwenden Sie VidLens NICHT.** Nur für Textmodelle.

## Funktionsweise

```
Bild/Video -> base64-Kodierung -> Vision-API -> Klartext
```

## Voraussetzungen

- [Python 3](https://python.org) (3.7+)
- OpenAI-kompatibler Vision-API-Schlüssel
- (Optional) [ffmpeg](https://ffmpeg.org)

## Schnellstart: MCP-Server (empfohlen)

MCP ist die schnellste Methode, VidLens zu verwenden.

```bash
# 1. Installieren
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. Konfigurieren
python scripts/vidlens.py --init
# 3. MCP-Server starten
python vidlens/server.py
```

In Ihrem MCP-Client registrieren:

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

Drei Tools: `look`, `list_media`, `find_and_look`.

## Schnellstart: CLI (Fallback ohne MCP)

Das Ergebnis wird direkt in stdout ausgegeben.

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "Was ist auf diesem Bild?"
```

## Auto-Verwendungsregel (Codex)

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

Prüft zuerst native Vision: Wenn das Modell Bilder sehen kann, wird VidLens übersprungen.

## Funktionen

- **Keine Abhängigkeiten für Bilder**
- **MCP-Server-Modus**
- **Anbieter-Failover** (bis zu 9)
- **Support für Reasoning-Modelle**
- **Lokales OCR-Fallback**
- **Video-Support** (ffmpeg / opencv)
- **Benutzerdefinierte Prompt-Templates**
- **Multi-Anbieter**

## Konfiguration

| Schlüssel | Standard | Zweck |
|-----|-----|-----|
| `api_url` | `""` | Vision-API-Basis-URL |
| `api_key` | `""` | API-Schlüssel |
| `model_name` | `""` | Modellname |
| `response_tokens` | `4000` | Max. Tokens |
| `is_reasoning_model` | `false` | Reasoning-Modelle: true |

## Fehlerbehebung

| Problem | Lösung |
|---------|---------|
| `NEEDS CONFIG` | `--init` ausführen, config.yaml ausfüllen |
| Video schlägt fehl | ffmpeg oder `pip install opencv-python numpy` |

## Dokumentation

- [Installationsanleitung](docs/SETUP.md)
- [Erweiterte Funktionen](docs/ADVANCED.md)
- [Fehlerbehebung](docs/TROUBLESHOOTING.md)
- [Änderungsprotokoll](CHANGELOG.md)

## Lizenz

MIT. Siehe [LICENSE](LICENSE).
