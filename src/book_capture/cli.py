"""Interface en ligne de commande (CLI) de book-capture.

Utilise Click (open source, licence BSD).

Exemples d'utilisation
----------------------
Traiter une image ::

    book-capture photo.jpg

Traiter plusieurs images avec sortie personnalisée ::

    book-capture photo1.jpg photo2.jpg -o ma_bibliotheque.xlsx

Traiter une image en mode verbeux ::

    book-capture photo.jpg -v

Forcer l'orientation verticale (livres debout sur une étagère) ::

    book-capture photo.jpg --orientation vertical
"""

import sys

import click

from . import extraction, export


@click.command(
    help=(
        "Traite des photos de tranches de livres et génère un fichier xlsx.\n\n"
        "IMAGES : un ou plusieurs fichiers image à traiter (JPEG, PNG, etc.)."
    )
)
@click.argument("images", nargs=-1, type=click.Path(exists=True))
@click.option(
    "-o",
    "--sortie",
    default="livres.xlsx",
    show_default=True,
    help="Chemin du fichier xlsx de sortie.",
)
@click.option(
    "-l",
    "--langue",
    default="fra+eng",
    show_default=True,
    help="Langue(s) OCR séparées par '+' (ex. 'fra', 'fra+eng').",
)
@click.option(
    "--orientation",
    type=click.Choice(["auto", "horizontal", "vertical"], case_sensitive=False),
    default="auto",
    show_default=True,
    help=(
        "Orientation des tranches dans l'image.\n\n"
        "  auto       – détection automatique.\n\n"
        "  horizontal – livres empilés à plat (bandes horizontales).\n\n"
        "  vertical   – livres debout côte à côte (bandes verticales)."
    ),
)
@click.option(
    "-v",
    "--verbeux",
    is_flag=True,
    help="Affiche des informations détaillées pendant le traitement.",
)
def main(images: tuple[str, ...], sortie: str, langue: str, orientation: str, verbeux: bool) -> None:
    """Point d'entrée de la commande ``book-capture``."""

    if not images:
        click.echo(
            "Erreur : aucun fichier image fourni. "
            "Utilisez 'book-capture --help' pour l'aide.",
            err=True,
        )
        sys.exit(1)

    tous_livres: list[dict] = []

    for chemin_image in images:
        if verbeux:
            click.echo(f"⏳ Traitement de : {chemin_image}")

        try:
            livres = extraction.traiter_image(chemin_image, langue=langue, orientation=orientation)
        except (OSError, IOError) as exc:
            click.echo(f"⚠️  Impossible de lire '{chemin_image}' : {exc}", err=True)
            continue
        except Exception as exc:  # noqa: BLE001 – erreurs OCR ou de traitement imprévisibles
            click.echo(f"⚠️  Erreur lors du traitement de '{chemin_image}' : {exc}", err=True)
            continue

        if verbeux:
            click.echo(f"   → {len(livres)} livre(s) détecté(s)")
        tous_livres.extend(livres)

    if not tous_livres:
        click.echo("Aucun livre détecté dans les images fournies.", err=True)
        sys.exit(1)

    # Déduplication et comptage
    livres_consolides = extraction.consolider_livres(tous_livres)

    # Export xlsx
    chemin_cree = export.exporter_xlsx(livres_consolides, sortie)

    nb_titres = len(livres_consolides)
    nb_total = sum(l["quantite"] for l in livres_consolides)

    click.echo(f"✅ Fichier généré : {chemin_cree}")
    click.echo(f"   Titres uniques  : {nb_titres}")
    click.echo(f"   Total livres    : {nb_total}")
