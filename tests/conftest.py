"""Fixtures partagées pour les tests de book_capture.

Les fixtures créent des images synthétiques de tranches de livres afin de
tester les modules sans dépendre de fichiers image réels.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont


def _creer_image_tranche(
    titre: str,
    auteur: str,
    largeur: int = 200,
    hauteur: int = 60,
    couleur_fond: tuple = (255, 245, 200),
    couleur_texte: tuple = (0, 0, 0),
) -> Image.Image:
    """Crée une image synthétique de tranche de livre avec titre et auteur."""
    image = Image.new("RGB", (largeur, hauteur), color=couleur_fond)
    dessin = ImageDraw.Draw(image)

    # Utiliser la police par défaut (disponible sans installation)
    try:
        police_titre = ImageFont.truetype("arial.ttf", 14)
        police_auteur = ImageFont.truetype("arial.ttf", 10)
    except OSError:
        # Repli sur la police bitmap intégrée à Pillow (disponible sur toutes les plateformes)
        police_titre = ImageFont.load_default()
        police_auteur = ImageFont.load_default()

    dessin.text((5, 5), titre, fill=couleur_texte, font=police_titre)
    dessin.text((5, 35), auteur, fill=couleur_texte, font=police_auteur)

    return image


def _empiler_images(images: list[Image.Image]) -> Image.Image:
    """Assemble plusieurs images en une colonne (pile horizontale)."""
    largeur = max(img.width for img in images)
    hauteur_totale = sum(img.height for img in images)
    pile = Image.new("RGB", (largeur, hauteur_totale), color=(200, 200, 200))

    y_offset = 0
    for img in images:
        pile.paste(img, (0, y_offset))
        y_offset += img.height

    return pile


@pytest.fixture
def image_tranche_simple(tmp_path: Path) -> Path:
    """Image PNG d'une seule tranche de livre."""
    image = _creer_image_tranche("Le Petit Prince", "Antoine de Saint-Exupéry")
    chemin = tmp_path / "tranche.png"
    image.save(chemin)
    return chemin


@pytest.fixture
def image_pile_livres(tmp_path: Path) -> Path:
    """Image PNG d'une pile de trois tranches de livres empilées."""
    tranches = [
        _creer_image_tranche("Le Petit Prince", "Saint-Exupéry", hauteur=60),
        _creer_image_tranche("Les Misérables", "Victor Hugo", hauteur=60),
        _creer_image_tranche("Germinal", "Émile Zola", hauteur=60),
    ]
    pile = _empiler_images(tranches)
    chemin = tmp_path / "pile.png"
    pile.save(chemin)
    return chemin


@pytest.fixture
def livres_exemple() -> list[dict]:
    """Liste d'exemples de livres pour les tests d'extraction/export."""
    return [
        {"titre": "Le Petit Prince", "auteur": "Antoine de Saint-Exupéry"},
        {"titre": "Les Misérables", "auteur": "Victor Hugo"},
        {"titre": "Le Petit Prince", "auteur": "Antoine de Saint-Exupéry"},
        {"titre": "Germinal", "auteur": "Émile Zola"},
    ]


@pytest.fixture
def livres_consolides() -> list[dict]:
    """Liste de livres consolidés (avec quantité) pour les tests d'export."""
    return [
        {"titre": "Germinal", "auteur": "Émile Zola", "quantite": 1},
        {"titre": "Le Petit Prince", "auteur": "Antoine de Saint-Exupéry", "quantite": 2},
        {"titre": "Les Misérables", "auteur": "Victor Hugo", "quantite": 1},
    ]
