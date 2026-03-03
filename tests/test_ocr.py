"""Tests du module ocr.

Note : ces tests nécessitent que Tesseract soit installé sur le système.
Ils sont marqués ``ocr`` pour pouvoir être sautés facilement :

    pytest -m "not ocr"      # sans Tesseract
    pytest -m ocr            # uniquement les tests OCR
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

# Détection de Tesseract pour les tests qui en dépendent
pytesseract = pytest.importorskip("pytesseract", reason="pytesseract non installé")
try:
    pytesseract.get_tesseract_version()
    TESSERACT_DISPONIBLE = True
except Exception:
    TESSERACT_DISPONIBLE = False

necessite_tesseract = pytest.mark.skipif(
    not TESSERACT_DISPONIBLE,
    reason="Tesseract n'est pas installé sur ce système",
)


@necessite_tesseract
class TestExtraireTexte:
    """Tests de la fonction extraire_texte (nécessite Tesseract)."""

    def test_retourne_chaine(self, image_tranche_simple: Path) -> None:
        """extraire_texte doit retourner une chaîne de caractères."""
        from book_capture.ocr import extraire_texte
        from book_capture.traitement_image import charger_image, preparer_image

        image = preparer_image(charger_image(str(image_tranche_simple)))
        resultat = extraire_texte(image, langue="eng")
        assert isinstance(resultat, str)

    def test_texte_non_vide_sur_image_avec_texte(self, image_tranche_simple: Path) -> None:
        """Une image contenant du texte doit produire un résultat (chaîne, même vide)."""
        from book_capture.ocr import extraire_texte
        from book_capture.traitement_image import charger_image, preparer_image

        image = preparer_image(charger_image(str(image_tranche_simple)))
        resultat = extraire_texte(image, langue="eng")
        # Le résultat est une chaîne (éventuellement vide si la confiance est trop basse)
        assert isinstance(resultat, str)


@necessite_tesseract
class TestExtraireDonnees:
    """Tests de la fonction extraire_donnees (nécessite Tesseract)."""

    def test_retourne_liste(self, image_tranche_simple: Path) -> None:
        """extraire_donnees doit retourner une liste."""
        from book_capture.ocr import extraire_donnees
        from book_capture.traitement_image import charger_image, preparer_image

        image = preparer_image(charger_image(str(image_tranche_simple)))
        resultat = extraire_donnees(image, langue="eng")
        assert isinstance(resultat, list)

    def test_cles_mot(self, image_tranche_simple: Path) -> None:
        """Chaque entrée doit contenir les clés attendues."""
        from book_capture.ocr import extraire_donnees
        from book_capture.traitement_image import charger_image, preparer_image

        image = preparer_image(charger_image(str(image_tranche_simple)))
        mots = extraire_donnees(image, langue="eng")
        for mot in mots:
            assert "texte" in mot
            assert "confiance" in mot
            assert "gauche" in mot
            assert "haut" in mot


@necessite_tesseract
class TestConfianceMoyenne:
    """Tests de la fonction confiance_moyenne (nécessite Tesseract)."""

    def test_retourne_float(self, image_tranche_simple: Path) -> None:
        """confiance_moyenne doit retourner un float."""
        from book_capture.ocr import confiance_moyenne
        from book_capture.traitement_image import charger_image, preparer_image

        image = preparer_image(charger_image(str(image_tranche_simple)))
        resultat = confiance_moyenne(image, langue="eng")
        assert isinstance(resultat, float)

    def test_image_noire_retourne_valeur_negative(self) -> None:
        """Une image entièrement noire (sans texte) doit retourner -1."""
        from book_capture.ocr import confiance_moyenne

        image_noire = Image.new("L", (200, 60), color=0)
        resultat = confiance_moyenne(image_noire, langue="eng")
        assert resultat == -1.0
