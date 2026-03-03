"""Extraction et organisation des informations de livres depuis le texte OCR.

Ce module analyse le texte reconnu sur les tranches de livres afin d'en
extraire le titre et l'auteur, puis regroupe les doublons pour produire
un inventaire avec quantités.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

from . import ocr as _ocr
from . import traitement_image as _ti


def normaliser_texte(texte: str) -> str:
    """Normalise un texte pour faciliter la comparaison (doublons OCR).

    - Supprime les accents
    - Convertit en minuscules
    - Élimine les caractères non alphanumériques (hors espaces)
    - Réduit les espaces multiples
    """
    # Décomposer les caractères accentués, puis supprimer les diacritiques
    nfkd = unicodedata.normalize("NFKD", texte)
    sans_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Minuscules
    minuscules = sans_accents.lower()
    # Supprimer les caractères non alphanumériques (hors espace)
    propre = re.sub(r"[^a-z0-9 ]", " ", minuscules)
    # Réduire les espaces multiples
    return re.sub(r"\s+", " ", propre).strip()


def analyser_tranche(texte: str) -> dict:
    """Analyse le texte brut d'une tranche pour en extraire titre et auteur.

    Heuristiques appliquées :
    1. On découpe le texte en lignes non vides.
    2. La ligne la plus longue (en nombre de caractères) est considérée comme
       le titre.
    3. S'il existe au moins deux lignes, la deuxième plus longue est
       considérée comme l'auteur.
    4. Les lignes restantes sont ignorées (logo éditeur, etc.).

    Parameters
    ----------
    texte:
        Texte brut issu de l'OCR pour une tranche de livre.

    Returns
    -------
    dict
        Dictionnaire avec les clés ``'titre'`` et ``'auteur'`` (chaînes,
        éventuellement vides).
    """
    lignes = [ligne.strip() for ligne in texte.splitlines() if ligne.strip()]

    if not lignes:
        return {"titre": "", "auteur": ""}

    # Trier par longueur décroissante pour trouver la ligne la plus informative
    lignes_triees = sorted(lignes, key=len, reverse=True)

    titre = lignes_triees[0] if lignes_triees else ""
    auteur = lignes_triees[1] if len(lignes_triees) > 1 else ""

    return {"titre": titre, "auteur": auteur}


def consolider_livres(livres: list[dict]) -> list[dict]:
    """Regroupe les livres identiques et calcule la quantité.

    Deux livres sont considérés identiques si leurs titres et auteurs
    normalisés sont identiques.

    Parameters
    ----------
    livres:
        Liste de dictionnaires avec les clés ``'titre'`` et ``'auteur'``.

    Returns
    -------
    list[dict]
        Liste triée par titre, avec les clés ``'titre'``, ``'auteur'``
        et ``'quantite'``.
    """
    compteur: Counter = Counter()
    # Dictionnaire clé_normalisée → (titre_original, auteur_original)
    originaux: dict[str, tuple[str, str]] = {}

    for livre in livres:
        titre = livre.get("titre", "")
        auteur = livre.get("auteur", "")
        cle = (normaliser_texte(titre), normaliser_texte(auteur))

        if cle not in originaux:
            originaux[cle] = (titre, auteur)
        compteur[cle] += 1

    resultat = [
        {
            "titre": originaux[cle][0],
            "auteur": originaux[cle][1],
            "quantite": compteur[cle],
        }
        for cle in sorted(originaux, key=lambda k: k[0])
    ]

    return resultat


def traiter_image(
    chemin_image: str,
    langue: str = "fra+eng",
    orientation: str = "auto",
) -> list[dict]:
    """Traite une image et retourne la liste des livres détectés.

    Enchaîne : chargement → prétraitement → segmentation des tranches →
    OCR avec détection automatique d'orientation → analyse texte.

    Parameters
    ----------
    chemin_image:
        Chemin vers le fichier image (JPEG, PNG, etc.).
    langue:
        Code de langue Tesseract (ex. ``'fra+eng'``).
    orientation:
        Orientation des tranches dans l'image (``'auto'``, ``'horizontal'``,
        ``'vertical'``).

    Returns
    -------
    list[dict]
        Liste de dictionnaires avec les clés ``'titre'`` et ``'auteur'``.
    """
    # Chargement et prétraitement
    image = _ti.charger_image(chemin_image)
    image_preparee = _ti.preparer_image(image)

    # Segmentation en tranches individuelles
    tranches = _ti.segmenter_tranches(image_preparee, orientation=orientation)

    livres = []
    for tranche in tranches:
        # OCR avec sélection automatique de la meilleure orientation
        texte = _ocr.extraire_texte_meilleure_orientation(tranche, langue=langue)
        if texte:
            info = analyser_tranche(texte)
            if info["titre"]:
                livres.append(info)

    return livres
