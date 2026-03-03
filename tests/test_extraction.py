"""Tests du module extraction."""

from __future__ import annotations

import pytest

from book_capture.extraction import analyser_tranche, consolider_livres, normaliser_texte


class TestNormaliserTexte:
    """Tests de la fonction normaliser_texte."""

    def test_minuscules(self) -> None:
        """Le résultat doit être en minuscules."""
        assert normaliser_texte("Bonjour") == "bonjour"

    def test_supprime_accents(self) -> None:
        """Les accents doivent être supprimés."""
        assert normaliser_texte("été") == "ete"
        assert normaliser_texte("Émile") == "emile"
        assert normaliser_texte("naïf") == "naif"

    def test_supprime_ponctuation(self) -> None:
        """La ponctuation doit être supprimée."""
        assert normaliser_texte("Bonjour, monde!") == "bonjour monde"

    def test_reduit_espaces(self) -> None:
        """Les espaces multiples doivent être réduits à un seul."""
        assert normaliser_texte("un   deux") == "un deux"

    def test_chaine_vide(self) -> None:
        """Une chaîne vide reste vide."""
        assert normaliser_texte("") == ""

    def test_texte_sans_modification(self) -> None:
        """Un texte déjà normalisé reste inchangé."""
        assert normaliser_texte("bonjour monde") == "bonjour monde"


class TestAnalyserTranche:
    """Tests de la fonction analyser_tranche."""

    def test_titre_extrait(self) -> None:
        """Le titre doit être la ligne la plus longue."""
        texte = "Le Petit Prince\nSaint-Exupéry"
        resultat = analyser_tranche(texte)
        assert resultat["titre"] == "Le Petit Prince"

    def test_auteur_extrait(self) -> None:
        """L'auteur doit être la deuxième ligne la plus longue."""
        texte = "Les Misérables\nVictor Hugo"
        resultat = analyser_tranche(texte)
        assert resultat["auteur"] == "Victor Hugo"

    def test_texte_vide(self) -> None:
        """Un texte vide doit retourner titre et auteur vides."""
        resultat = analyser_tranche("")
        assert resultat["titre"] == ""
        assert resultat["auteur"] == ""

    def test_une_seule_ligne(self) -> None:
        """Avec une seule ligne, l'auteur doit être vide."""
        resultat = analyser_tranche("Germinal")
        assert resultat["titre"] == "Germinal"
        assert resultat["auteur"] == ""

    def test_lignes_blanches_ignorees(self) -> None:
        """Les lignes vides du texte OCR doivent être ignorées."""
        # "Au Bonheur des Dames" est plus long qu'Émile Zola → c'est le titre
        texte = "\n\nAu Bonheur des Dames\n\nÉmile Zola\n\n"
        resultat = analyser_tranche(texte)
        assert resultat["titre"] == "Au Bonheur des Dames"

    def test_titre_ligne_plus_longue(self) -> None:
        """La ligne la plus longue est le titre, même si elle apparaît en second."""
        texte = "Hugo\nLes Misérables"
        resultat = analyser_tranche(texte)
        assert resultat["titre"] == "Les Misérables"
        assert resultat["auteur"] == "Hugo"


class TestConsoliderLivres:
    """Tests de la fonction consolider_livres."""

    def test_deduplique_livres_identiques(self, livres_exemple: list[dict]) -> None:
        """Deux livres identiques doivent être consolidés en un seul avec quantité 2."""
        resultat = consolider_livres(livres_exemple)
        petit_prince = next(
            (l for l in resultat if "petit prince" in l["titre"].lower()), None
        )
        assert petit_prince is not None
        assert petit_prince["quantite"] == 2

    def test_livres_differents_conserves(self, livres_exemple: list[dict]) -> None:
        """Les livres différents doivent tous apparaître dans le résultat."""
        resultat = consolider_livres(livres_exemple)
        titres = {l["titre"] for l in resultat}
        assert "Les Misérables" in titres
        assert "Germinal" in titres

    def test_quantite_unitaire_par_defaut(self) -> None:
        """Un livre présent une seule fois doit avoir une quantité de 1."""
        livres = [{"titre": "Germinal", "auteur": "Émile Zola"}]
        resultat = consolider_livres(livres)
        assert resultat[0]["quantite"] == 1

    def test_liste_vide(self) -> None:
        """Une liste vide doit retourner une liste vide."""
        resultat = consolider_livres([])
        assert resultat == []

    def test_cles_presentes(self, livres_exemple: list[dict]) -> None:
        """Chaque entrée du résultat doit avoir les clés 'titre', 'auteur', 'quantite'."""
        resultat = consolider_livres(livres_exemple)
        for livre in resultat:
            assert "titre" in livre
            assert "auteur" in livre
            assert "quantite" in livre

    def test_resultat_trie(self) -> None:
        """Le résultat doit être trié par titre normalisé."""
        livres = [
            {"titre": "Zola", "auteur": ""},
            {"titre": "Balzac", "auteur": ""},
        ]
        resultat = consolider_livres(livres)
        titres = [l["titre"] for l in resultat]
        assert titres == sorted(titres)

    def test_normalisation_doublons_avec_accents(self) -> None:
        """Deux entrées dont les titres ne diffèrent que par les accents doivent être consolidées."""
        livres = [
            {"titre": "Éte", "auteur": ""},
            {"titre": "Ete", "auteur": ""},
        ]
        resultat = consolider_livres(livres)
        assert len(resultat) == 1
        assert resultat[0]["quantite"] == 2
