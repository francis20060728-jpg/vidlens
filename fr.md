# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

Donnez aux agents IA en mode texte la capacité de voir images et vidéos.

VidLens achemine les fichiers visuels via un modèle de vision externe et renvoie du texte brut.

> **Si votre modèle supporte nativement la vision, n'utilisez PAS VidLens.** Réservé aux modèles texte uniquement.

## Fonctionnement

```
Image/Vidéo -> encodage base64 -> API Vision -> texte brut
```

## Prérequis

- [Python 3](https://python.org) (3.7+)
- Clé API de vision compatible OpenAI
- (Optionnel) [ffmpeg](https://ffmpeg.org)

## Démarrage : Serveur MCP (recommandé)

MCP est le moyen le plus rapide d'utiliser VidLens.

```bash
# 1. Installer
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. Configurer
python scripts/vidlens.py --init
# 3. Lancer le serveur MCP
python vidlens/server.py
```

Inscrire dans votre client MCP :

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

Trois outils : `look`, `list_media`, `find_and_look`.

## Démarrage : CLI (repli sans MCP)

Le résultat s'affiche directement dans stdout.

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "Que contient cette image ?"
```

## Règle d'utilisation automatique (Codex)

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

Vérifie d'abord la vision native : si le modèle voit les images, VidLens est ignoré.

## Fonctionnalités

- **Zéro dépendance pour les images**
- **Mode serveur MCP**
- **Bascule de fournisseurs** (jusqu'à 9)
- **Support des modèles de raisonnement**
- **Repli OCR local**
- **Support vidéo** (ffmpeg / opencv)
- **Modèles de prompt personnalisés**
- **Multi-fournisseurs**

## Configuration

| Clé | Défaut | Objectif |
|-----|-----|-----|
| `api_url` | `""` | URL de base API Vision |
| `api_key` | `""` | Clé API |
| `model_name` | `""` | Nom du modèle |
| `response_tokens` | `4000` | Tokens max |
| `is_reasoning_model` | `false` | Modèles de raisonnement: true |

## Dépannage

| Problème | Solution |
|---------|---------|
| `NEEDS CONFIG` | Exécuter `--init`, remplir config.yaml |
| Vidéo échoue | Installer ffmpeg ou `pip install opencv-python numpy` |

## Documentation

- [Guide d'installation](docs/SETUP.md)
- [Fonctionnalités avancées](docs/ADVANCED.md)
- [Dépannage](docs/TROUBLESHOOTING.md)
- [Journal des versions](CHANGELOG.md)

## Licence

MIT. Voir [LICENSE](LICENSE).
