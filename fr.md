# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [한국어](ko.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

Donnez aux agents IA en mode texte la capacité de voir images et vidéos.

VidLens achemine les fichiers visuels via un modèle de vision externe et renvoie du texte brut.

> **Si le modèle/fournisseur actuel est explicitement multimodal, utilisez la vision native.** En texte seul ou capacité inconnue, VidLens utilise une vision externe et renvoie uniquement du texte.

## Fonctionnement

```
Image/Vidéo -> encodage base64 -> API Vision -> texte brut
```

## Déploiement en un clic (demandez à votre agent IA)

Dites à votre agent :

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

L'agent clonera le dépôt, exécutera --init, et vous aidera à remplir config.yaml.

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

### Outils MCP

| Outil | Description | Arguments clés |
|------|------|------|
| `look` | Analyse un fichier image ou vidéo unique avec le modèle de vision. Les vidéos sont automatiquement échantillonnées en une planche-contact étiquetée. | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | Trouve les fichiers image et vidéo dans un répertoire. Recherche récursive, filtre par mot-clé de nom de fichier. Retourne les chemins absolus triés images en premier. | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | Recherche dans un répertoire par mot-clé, puis analyse la meilleure correspondance en un appel. Combinaison pratique de list_media + look. | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

Exemple : `look(media_path="chart.png", prompt="Que montre ce graphique ?")`


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

Vérifie d'abord la capacité réelle du modèle/fournisseur. Les modèles explicitement multimodaux utilisent la vision native et peuvent charger un chemin en entrée native ; en texte seul ou capacité inconnue, VidLens renvoie uniquement du texte. Une requête native rejetée n'est pas relancée.

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
| `response_tokens` | `1200` | Tokens max |
| `verification_tokens` | `350` | Budget réduit pour vérifications PASS/FAIL |
| `http_timeout` | `45` | Délai par requête |
| `total_timeout` | `60` | Délai total |
| `reasoning_effort` | `""` | Effort de raisonnement optionnel |
| `max_image_side` | `1600` | Côté maximal d'image |
| `image_jpeg_quality` | `90` | Qualité JPEG |
| `is_reasoning_model` | `false` | Modèles de raisonnement: true |

## Dépannage

| Problème | Solution |
|---------|---------|
| `NEEDS CONFIG` | Exécuter `--init`, remplir config.yaml |
| Vidéo échoue | Installer ffmpeg ou `pip install opencv-python numpy` |

## Contact

Une question ou une suggestion ? Écrivez à **francis20060728@gmail.com** et je répondrai rapidement.
## Documentation

- [Guide d'installation](docs/SETUP.md)
- [Fonctionnalités avancées](docs/ADVANCED.md)
- [Dépannage](docs/TROUBLESHOOTING.md)
- [Journal des versions](CHANGELOG.md)

## Licence

MIT. Voir [LICENSE](LICENSE).
