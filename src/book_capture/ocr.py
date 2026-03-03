"""Reconnaissance de texte (OCR) sur les images de tranches de livres.

Utilise Tesseract via pytesseract (open source, licence Apache 2.0).
Tesseract doit être installé séparément sur le système :
- Windows / conda : ``conda install -c conda-forge tesseract``
- Termux / Android : ``pkg install tesseract-ocr``
- Docker          : voir le Dockerfile du projet
"""

from __future__ import annotations

import pytesseract
from PIL import Image


# Configuration Tesseract par défaut
# PSM 6 : suppose un bloc de texte uniforme (bien adapté aux tranches)
CONFIG_TESSERACT = "--psm 6"


def extraire_texte(image: Image.Image, langue: str = "fra+eng") -> str:
    """Extrait le texte brut d'une image avec Tesseract.

    Parameters
    ----------
    image:
        Image PIL à analyser.
    langue:
        Code de langue Tesseract, ex. ``'fra'``, ``'eng'``, ``'fra+eng'``.
        Les données linguistiques correspondantes doivent être installées.

    Returns
    -------
    str
        Texte reconnu (peut contenir des sauts de ligne).
    """
    texte = pytesseract.image_to_string(image, lang=langue, config=CONFIG_TESSERACT)
    return texte.strip()


def extraire_donnees(image: Image.Image, langue: str = "fra+eng") -> list[dict]:
    """Extrait le texte avec les métadonnées de position et de confiance.

    Retourne une liste de dictionnaires, un par mot reconnu, avec les clés :
    ``texte``, ``gauche``, ``haut``, ``largeur``, ``hauteur``, ``confiance``,
    ``numero_ligne``.

    Parameters
    ----------
    image:
        Image PIL à analyser.
    langue:
        Code de langue Tesseract.

    Returns
    -------
    list[dict]
        Mots reconnus avec leurs métadonnées.
    """
    donnees_brutes = pytesseract.image_to_data(
        image, lang=langue, config=CONFIG_TESSERACT,
        output_type=pytesseract.Output.DICT,
    )

    mots = []
    for i, texte in enumerate(donnees_brutes["text"]):
        # Ignorer les entrées vides ou peu fiables
        if not texte.strip():
            continue
        confiance = int(donnees_brutes["conf"][i])
        if confiance < 0:
            continue
        mots.append({
            "texte": texte.strip(),
            "gauche": donnees_brutes["left"][i],
            "haut": donnees_brutes["top"][i],
            "largeur": donnees_brutes["width"][i],
            "hauteur": donnees_brutes["height"][i],
            "confiance": confiance,
            "numero_ligne": donnees_brutes["line_num"][i],
        })

    return mots


def confiance_moyenne(image: Image.Image, langue: str = "fra+eng") -> float:
    """Calcule la confiance OCR moyenne pour l'image donnée.

    Utile pour choisir la meilleure orientation avant d'extraire le texte.

    Parameters
    ----------
    image:
        Image PIL à analyser.
    langue:
        Code de langue Tesseract.

    Returns
    -------
    float
        Confiance moyenne entre 0 et 100 (−1 si aucun texte détecté).
    """
    donnees = extraire_donnees(image, langue)
    if not donnees:
        return -1.0
    return sum(m["confiance"] for m in donnees) / len(donnees)


def extraire_texte_meilleure_orientation(
    image: Image.Image,
    langue: str = "fra+eng",
    angles: tuple[int, ...] = (0, 90, 270),
) -> str:
    """Essaie plusieurs rotations et retourne le texte obtenu avec la meilleure confiance.

    Les tranches de livres ont souvent du texte vertical. Cette fonction teste
    plusieurs orientations et choisit celle qui donne la confiance OCR la plus
    élevée.

    Parameters
    ----------
    image:
        Image PIL à analyser.
    langue:
        Code de langue Tesseract.
    angles:
        Angles (en degrés, sens anti-horaire) à tester.

    Returns
    -------
    str
        Texte extrait avec la meilleure orientation détectée.
    """
    meilleur_texte = ""
    meilleure_confiance = -1.0

    for angle in angles:
        image_rotee = image.rotate(angle, expand=True) if angle != 0 else image
        confiance = confiance_moyenne(image_rotee, langue)
        if confiance > meilleure_confiance:
            meilleure_confiance = confiance
            meilleur_texte = extraire_texte(image_rotee, langue)

    return meilleur_texte
