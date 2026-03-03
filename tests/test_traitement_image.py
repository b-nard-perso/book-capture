"""Tests du module traitement_image."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from book_capture.traitement_image import (
    charger_image,
    pivoter,
    preparer_image,
    segmenter_tranches,
)


class TestChargerImage:
    """Tests de la fonction charger_image."""

    def test_charge_fichier_existant(self, image_tranche_simple: Path) -> None:
        """Une image existante doit être chargée sans erreur."""
        image = charger_image(str(image_tranche_simple))
        assert isinstance(image, Image.Image)

    def test_mode_rgb(self, image_tranche_simple: Path) -> None:
        """L'image chargée doit être en mode RGB."""
        image = charger_image(str(image_tranche_simple))
        assert image.mode == "RGB"

    def test_fichier_inexistant(self, tmp_path: Path) -> None:
        """Un fichier inexistant doit lever une exception."""
        with pytest.raises(Exception):
            charger_image(str(tmp_path / "inexistant.png"))


class TestPreparerImage:
    """Tests de la fonction preparer_image."""

    def test_retourne_image_pillow(self, image_tranche_simple: Path) -> None:
        """preparer_image doit retourner un objet Image."""
        image = charger_image(str(image_tranche_simple))
        resultat = preparer_image(image)
        assert isinstance(resultat, Image.Image)

    def test_image_en_niveaux_de_gris(self, image_tranche_simple: Path) -> None:
        """L'image préparée doit être en niveaux de gris (mode 'L')."""
        image = charger_image(str(image_tranche_simple))
        resultat = preparer_image(image)
        assert resultat.mode == "L"

    def test_dimensions_preservees(self, image_tranche_simple: Path) -> None:
        """Les dimensions de l'image doivent être conservées après prétraitement."""
        image = charger_image(str(image_tranche_simple))
        resultat = preparer_image(image)
        assert resultat.size == image.size


class TestSegmenterTranches:
    """Tests de la fonction segmenter_tranches."""

    def test_retourne_liste(self, image_tranche_simple: Path) -> None:
        """segmenter_tranches doit retourner une liste."""
        image = charger_image(str(image_tranche_simple))
        resultat = segmenter_tranches(image)
        assert isinstance(resultat, list)

    def test_au_moins_une_tranche(self, image_tranche_simple: Path) -> None:
        """La segmentation doit retourner au moins une tranche."""
        image = charger_image(str(image_tranche_simple))
        resultat = segmenter_tranches(image)
        assert len(resultat) >= 1

    def test_tranches_sont_des_images(self, image_tranche_simple: Path) -> None:
        """Chaque tranche doit être un objet Image PIL."""
        image = charger_image(str(image_tranche_simple))
        resultat = segmenter_tranches(image)
        for tranche in resultat:
            assert isinstance(tranche, Image.Image)

    def test_orientation_forcee_horizontale(self, image_pile_livres: Path) -> None:
        """L'orientation forcée 'horizontal' doit être acceptée sans erreur."""
        image = charger_image(str(image_pile_livres))
        resultat = segmenter_tranches(image, orientation="horizontal")
        assert len(resultat) >= 1

    def test_orientation_forcee_verticale(self, image_tranche_simple: Path) -> None:
        """L'orientation forcée 'vertical' doit être acceptée sans erreur."""
        image = charger_image(str(image_tranche_simple))
        resultat = segmenter_tranches(image, orientation="vertical")
        assert len(resultat) >= 1


class TestPivoter:
    """Tests de la fonction pivoter."""

    def test_pivot_90_change_dimensions(self, image_tranche_simple: Path) -> None:
        """Une rotation de 90° doit échanger largeur et hauteur (expand=True)."""
        image = charger_image(str(image_tranche_simple))
        resultat = pivoter(image, 90)
        assert resultat.size == (image.height, image.width)

    def test_pivot_0_preserves_dimensions(self, image_tranche_simple: Path) -> None:
        """Une rotation de 0° ne doit pas modifier les dimensions."""
        image = charger_image(str(image_tranche_simple))
        resultat = pivoter(image, 0)
        assert resultat.size == image.size

    def test_pivot_180_preserves_dimensions(self, image_tranche_simple: Path) -> None:
        """Une rotation de 180° ne doit pas modifier les dimensions."""
        image = charger_image(str(image_tranche_simple))
        resultat = pivoter(image, 180)
        assert resultat.size == image.size
