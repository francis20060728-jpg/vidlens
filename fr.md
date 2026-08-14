# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [zhtw](zhtw.md) | [ja](ja.md) | [ko](ko.md) | [es](es.md) | [de](de.md) | [pt](pt.md)

Donnez aux agents IA en mode texte la capacité de voir images et vidéos.

VidLens achemine les fichiers visuels via un modèle de vision externe et renvoie du texte brut.

**Zéro dépendance pip pour les images.** Seule la bibliothèque standard Python 3 est requise.

**Si votre modèle supporte nativement la vision, n'utilisez PAS VidLens.** Il est réservé aux modèles texte uniquement.

## Démarrage : Serveur MCP (recommandé)

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
python vidlens/server.py
```

## Démarrage : CLI (repli pour agents sans MCP)

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "Que contient cette image ?"
```

## Licence

MIT. Voir [LICENSE](LICENSE).
