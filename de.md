# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [zhtw](zhtw.md) | [ja](ja.md) | [ko](ko.md) | [fr](fr.md) | [es](es.md) | [pt](pt.md)

Geben Sie KI-Agenten im Nur-Text-Modus die Fähigkeit, Bilder und Videos zu sehen.

VidLens leitet visuelle Dateien über ein externes Vision-Modell und gibt reinen Text zurück.

**Keine pip-Abhängigkeiten für Bilder.** Nur die Python-3-Standardbibliothek wird benötigt.

**Wenn Ihr Modell nativ Vision unterstützt, verwenden Sie VidLens NICHT.** Es ist nur für reine Textmodelle.

## Schnellstart: MCP-Server (empfohlen)

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
python vidlens/server.py
```

## Schnellstart: CLI (Fallback für Agenten ohne MCP)

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "Was ist auf diesem Bild?"
```

## Lizenz

MIT. Siehe [LICENSE](LICENSE).
