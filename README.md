# book-capture

Application Python en ligne de commande (CLI) pour traiter des photos de
tranches de livres. Le programme reconnaît automatiquement les titres et les
auteurs à l'aide de la reconnaissance optique de caractères (OCR), compte les
exemplaires en double, et génère un fichier **xlsx** récapitulatif.

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Prérequis système](#prérequis-système)
3. [Installation](#installation)
4. [Utilisation CLI](#utilisation-cli)
5. [Utilisation comme bibliothèque Python](#utilisation-comme-bibliothèque-python)
6. [Tests](#tests)
7. [Docker](#docker)
8. [Android / Termux](#android--termux)
9. [Structure du projet](#structure-du-projet)

---

## Fonctionnalités

- Traitement de photos de piles de livres (tranches visibles)
- Reconnaissance OCR des titres et auteurs (Tesseract, open source)
- Détection automatique de l'orientation des tranches (horizontale / verticale)
- Déduplication : comptage des exemplaires identiques
- Export au format **xlsx** (OpenPyXL, open source)
- 100 % open source, sans dépendance à un service commercial

---

## Prérequis système

### Tesseract OCR

Tesseract doit être installé **séparément** du paquet Python.

| Environnement | Commande d'installation |
|---------------|-------------------------|
| **conda (Windows/Linux/macOS)** | `conda install -c conda-forge tesseract` |
| **Debian / Ubuntu** | `sudo apt install tesseract-ocr tesseract-ocr-fra` |
| **Termux (Android)** | `pkg install tesseract-ocr` |
| **Docker** | Voir le `Dockerfile` du projet |

Pour vérifier l'installation : `tesseract --version`

### Données linguistiques

Par défaut, l'application utilise `fra+eng`. Assurez-vous que les packs de
langue sont installés (ils le sont automatiquement avec conda/apt).

---

## Installation

### Avec conda (recommandé pour Windows 11)

```bash
# Cloner le dépôt
git clone https://github.com/b-nard-perso/book-capture.git
cd book-capture

# Créer et activer l'environnement conda
conda env create -f environment.yml
conda activate book-db

# Installer en mode développement
pip install -e .
```

### Avec pip uniquement

```bash
pip install -e ".[dev]"
```

---

## Utilisation CLI

```bash
# Traiter une image
book-capture photo.jpg

# Traiter plusieurs images avec un fichier de sortie personnalisé
book-capture photo1.jpg photo2.jpg -o ma_bibliotheque.xlsx

# Mode verbeux
book-capture photo.jpg -v

# Forcer l'orientation verticale (livres debout sur une étagère)
book-capture photo.jpg --orientation vertical

# Spécifier la langue OCR
book-capture photo.jpg --langue fra
```

Le fichier xlsx produit contient trois colonnes : **Titre**, **Auteur**,
**Quantité**.

---

## Utilisation comme bibliothèque Python

```python
from book_capture import extraction, export

# Traiter une image
livres = extraction.traiter_image("photo.jpg", langue="fra+eng")

# Consolider les doublons
livres_consolides = extraction.consolider_livres(livres)

# Exporter en xlsx
export.exporter_xlsx(livres_consolides, "livres.xlsx")
```

---

## Tests

```bash
# Lancer tous les tests
pytest

# Lancer les tests sans nécessiter Tesseract
pytest -m "not ocr"

# Avec rapport de couverture
pytest --cov=book_capture
```

---

## Docker

### Construire l'image

```bash
docker build -t book-capture .
```

### Traiter une image

```bash
# Monter le dossier contenant vos photos
docker run --rm -v "$(pwd)/photos:/photos" book-capture /photos/photo.jpg
```

### Lancer les tests dans Docker

```bash
docker run --rm --entrypoint pytest book-capture
```

---

## Android / Termux

```bash
# Installer les dépendances système
pkg install python tesseract-ocr

# Installer le paquet
pip install -e .
```

---

## Structure du projet

```
book-capture/
├── pyproject.toml           # Configuration du paquet Python
├── environment.yml          # Environnement conda
├── Dockerfile               # Image Docker pour tests isolés
├── README.md
├── src/
│   └── book_capture/
│       ├── __init__.py
│       ├── cli.py               # Interface CLI (Click)
│       ├── traitement_image.py  # Chargement et prétraitement des images
│       ├── ocr.py               # Reconnaissance de texte (pytesseract)
│       ├── extraction.py        # Extraction titre/auteur, déduplication
│       └── export.py            # Export xlsx (openpyxl)
└── tests/
    ├── conftest.py
    ├── test_traitement_image.py
    ├── test_ocr.py
    ├── test_extraction.py
    └── test_export.py
```

---

## Licences des dépendances

| Bibliothèque | Licence | Usage |
|---|---|---|
| [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) | Apache 2.0 | Moteur OCR |
| [pytesseract](https://github.com/madmaze/pytesseract) | Apache 2.0 | Liaison Python ↔ Tesseract |
| [Pillow](https://github.com/python-pillow/Pillow) | HPND | Traitement d'images |
| [OpenCV](https://github.com/opencv/opencv-python) | Apache 2.0 | Prétraitement avancé |
| [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | MIT | Export xlsx |
| [Click](https://github.com/pallets/click) | BSD | Interface CLI |
| [NumPy](https://github.com/numpy/numpy) | BSD | Calcul numérique |
