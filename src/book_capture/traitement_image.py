"""Traitement et préparation des images de tranches de livres."""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def charger_image(chemin: str) -> Image.Image:
    """Charge une image depuis le chemin donné et la convertit en RGB."""
    image = Image.open(chemin).convert("RGB")
    return image


def preparer_image(image: Image.Image) -> Image.Image:
    """Prétraite l'image pour améliorer la qualité de la reconnaissance OCR.

    Applique successivement :
    - conversion en niveaux de gris,
    - amélioration du contraste,
    - légère netteté.
    """
    # Conversion en niveaux de gris
    image_grise = image.convert("L")

    # Amélioration du contraste
    ameliorateur = ImageEnhance.Contrast(image_grise)
    image_contrastee = ameliorateur.enhance(1.5)

    # Légère netteté pour aider l'OCR
    image_nette = image_contrastee.filter(ImageFilter.SHARPEN)

    return image_nette


def segmenter_tranches(image: Image.Image, orientation: str = "auto") -> list[Image.Image]:
    """Segmente l'image en régions correspondant chacune à une tranche de livre.

    Parameters
    ----------
    image:
        Image PIL en entrée (RGB ou niveaux de gris).
    orientation:
        ``'horizontal'`` – les livres sont empilés à plat (tranches en bandes
        horizontales dans l'image), ``'vertical'`` – les livres sont debout
        côte à côte (tranches en bandes verticales), ``'auto'`` – détection
        automatique selon les proportions de l'image.

    Returns
    -------
    list[Image.Image]
        Liste des sous-images correspondant aux tranches individuelles,
        pivotées pour que le texte soit horizontal (prêtes pour l'OCR).
    """
    largeur, hauteur = image.size

    if orientation == "auto":
        # Si l'image est plus large que haute, on suppose des livres debout côte à côte
        orientation = "vertical" if largeur >= hauteur else "horizontal"

    # Conversion numpy pour les calculs de projection
    tableau = np.array(image.convert("L"))

    if orientation == "horizontal":
        # Projection horizontale : somme sur chaque ligne
        tranches = _segmenter_bandes_horizontales(image, tableau)
    else:
        # Projection verticale : somme sur chaque colonne
        tranches = _segmenter_bandes_verticales(image, tableau)

    # Si la segmentation n'a rien trouvé, on retourne l'image entière
    if not tranches:
        tranches = [image]

    return tranches


def _segmenter_bandes_horizontales(
    image: Image.Image, tableau: np.ndarray
) -> list[Image.Image]:
    """Segmente l'image en bandes horizontales (livres empilés à plat)."""
    # Projection horizontale : écart-type par ligne (fort = contenu, faible = séparation)
    ecarts = tableau.std(axis=1)
    seuil = ecarts.mean() * 0.3

    # Détection des zones de transition (séparations entre livres)
    masque = ecarts > seuil
    debut_regions = []
    fin_regions = []

    en_region = False
    for i, est_actif in enumerate(masque):
        if est_actif and not en_region:
            debut_regions.append(i)
            en_region = True
        elif not est_actif and en_region:
            fin_regions.append(i)
            en_region = False
    if en_region:
        fin_regions.append(len(masque))

    largeur, _ = image.size
    tranches = []
    for debut, fin in zip(debut_regions, fin_regions):
        # Ignorer les bandes trop fines (bruit)
        if fin - debut < 20:
            continue
        bande = image.crop((0, debut, largeur, fin))
        tranches.append(bande)

    return tranches


def _segmenter_bandes_verticales(
    image: Image.Image, tableau: np.ndarray
) -> list[Image.Image]:
    """Segmente l'image en bandes verticales (livres debout côte à côte)."""
    # Projection verticale : écart-type par colonne
    ecarts = tableau.std(axis=0)
    seuil = ecarts.mean() * 0.3

    masque = ecarts > seuil
    debut_regions = []
    fin_regions = []

    en_region = False
    for i, est_actif in enumerate(masque):
        if est_actif and not en_region:
            debut_regions.append(i)
            en_region = True
        elif not est_actif and en_region:
            fin_regions.append(i)
            en_region = False
    if en_region:
        fin_regions.append(len(masque))

    _, hauteur = image.size
    tranches = []
    for debut, fin in zip(debut_regions, fin_regions):
        if fin - debut < 20:
            continue
        bande = image.crop((debut, 0, fin, hauteur))
        # Les livres debout ont le texte vertical → on pivote 90° dans le sens anti-horaire
        bande_pivotee = bande.rotate(90, expand=True)
        tranches.append(bande_pivotee)

    return tranches


def pivoter(image: Image.Image, angle: int) -> Image.Image:
    """Pivote l'image de l'angle donné (en degrés, sens anti-horaire)."""
    return image.rotate(angle, expand=True)
