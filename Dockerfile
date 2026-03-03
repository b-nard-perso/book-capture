# Dockerfile pour tester book-capture dans un environnement isolé
# Compatible avec Docker Desktop sur Windows 11.
#
# Construction :
#   docker build -t book-capture .
#
# Utilisation :
#   docker run --rm -v "$(pwd)/photos:/photos" book-capture /photos/photo.jpg
#
# Tests :
#   docker run --rm book-capture pytest

FROM python:3.11-slim

# Installation de Tesseract et des données linguistiques
# tesseract-ocr-fra : données pour le français
# tesseract-ocr-eng : données pour l'anglais (installées par défaut)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-fra \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Dossier de travail
WORKDIR /app

# Copie des fichiers du projet
COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/

# Installation du paquet en mode développement avec les dépendances de test
RUN pip install --no-cache-dir -e ".[dev]"

# Point d'entrée : par défaut, on lance la commande book-capture
ENTRYPOINT ["book-capture"]

# Commande par défaut : afficher l'aide
CMD ["--help"]
