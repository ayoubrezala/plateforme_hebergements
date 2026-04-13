"""Tests unitaires pour le module de nettoyage."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.nettoyage.nettoyeur import NettoyeurDonnees


@pytest.fixture
def nettoyeur():
    return NettoyeurDonnees()


class TestNettoyerTexte:
    def test_texte_normal(self, nettoyeur):
        assert nettoyeur.nettoyer_texte("  Hôtel du Port  ") == "Hôtel du Port"

    def test_texte_vide(self, nettoyeur):
        assert nettoyeur.nettoyer_texte("") is None
        assert nettoyeur.nettoyer_texte(None) is None

    def test_espaces_multiples(self, nettoyeur):
        assert nettoyeur.nettoyer_texte("Hôtel   du   Port") == "Hôtel du Port"


class TestNettoyerTelephone:
    def test_telephone_francais(self, nettoyeur):
        assert nettoyeur.nettoyer_telephone("02 40 12 34 56") == "+33240123456"

    def test_telephone_liste(self, nettoyeur):
        assert nettoyeur.nettoyer_telephone(["02 40 12 34 56"]) == "+33240123456"

    def test_telephone_none(self, nettoyeur):
        assert nettoyeur.nettoyer_telephone(None) is None

    def test_telephone_vide(self, nettoyeur):
        assert nettoyeur.nettoyer_telephone([]) is None


class TestNettoyerCoordonnees:
    def test_coordonnees_valides(self, nettoyeur):
        result = nettoyeur.nettoyer_coordonnees(47.28, -2.40)
        assert result["latitude"] == 47.28
        assert result["longitude"] == -2.4

    def test_coordonnees_hors_france(self, nettoyeur):
        result = nettoyeur.nettoyer_coordonnees(0, 0)
        assert result["latitude"] is None

    def test_coordonnees_invalides(self, nettoyeur):
        result = nettoyeur.nettoyer_coordonnees("abc", None)
        assert result["latitude"] is None


class TestNettoyerType:
    def test_hotel(self, nettoyeur):
        assert nettoyeur.nettoyer_type("hôtel") == "Hôtel"
        assert nettoyeur.nettoyer_type(["Hôtel de tourisme"]) == "Hôtel"

    def test_camping(self, nettoyeur):
        assert nettoyeur.nettoyer_type("camping") == "Camping"

    def test_meuble(self, nettoyeur):
        assert nettoyeur.nettoyer_type("Meublés") == "Meublé de tourisme"

    def test_chambre_hotes(self, nettoyeur):
        assert nettoyeur.nettoyer_type("Chambre d'hôtes") == "Chambre d'hôtes"

    def test_non_classe(self, nettoyeur):
        assert nettoyeur.nettoyer_type("") == "Non classé"


class TestNettoyerCapacite:
    def test_entier(self, nettoyeur):
        assert nettoyeur.nettoyer_capacite(10) == 10

    def test_chaine(self, nettoyeur):
        assert nettoyeur.nettoyer_capacite("25") == 25

    def test_zero(self, nettoyeur):
        assert nettoyeur.nettoyer_capacite(0) is None

    def test_invalide(self, nettoyeur):
        assert nettoyeur.nettoyer_capacite("abc") is None


class TestNettoyerEnregistrement:
    def test_enregistrement_complet(self, nettoyeur):
        brut = {
            "nomoffre": "Hôtel Océan",
            "type": ["Hôtel de tourisme"],
            "commune": "NANTES",
            "codepostal": "44000",
            "latitude": 47.2184,
            "longitude": -1.5536,
            "adresse2": "10 rue du Port",
            "commtel": ["02 40 11 22 33"],
            "capacitenbpersonnes": 50,
        }
        propre = nettoyeur.nettoyer_enregistrement(brut, "test")
        assert propre["nom"] == "Hôtel Océan"
        assert propre["type_hebergement"] == "Hôtel"
        assert propre["commune"] == "NANTES"
        assert propre["departement"] == "44"
        assert propre["capacite_personnes"] == 50
        assert propre["_id_unique"] is not None

    def test_enregistrement_minimal(self, nettoyeur):
        brut = {"nomoffre": "Test"}
        propre = nettoyeur.nettoyer_enregistrement(brut, "test")
        assert propre["nom"] == "Test"
        assert propre["commune"] is None


class TestNettoyerLot:
    def test_deduplication(self, nettoyeur):
        donnees = [
            {"nomoffre": "Hôtel A", "commune": "NANTES", "codepostal": "44000"},
            {"nomoffre": "Hôtel A", "commune": "NANTES", "codepostal": "44000"},  # doublon
            {"nomoffre": "Hôtel B", "commune": "ANGERS", "codepostal": "49000"},
        ]
        propres = nettoyeur.nettoyer_lot(donnees, "test")
        assert len(propres) == 2

    def test_ignore_sans_nom(self, nettoyeur):
        donnees = [
            {"nomoffre": "Hôtel A", "commune": "NANTES", "codepostal": "44000"},
            {"commune": "ANGERS"},  # pas de nom
        ]
        propres = nettoyeur.nettoyer_lot(donnees, "test")
        assert len(propres) == 1
