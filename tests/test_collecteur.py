"""Tests unitaires pour le module de collecte."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.collecte.collecteur import CollecteurDonnees


@pytest.fixture
def collecteur():
    return CollecteurDonnees(timeout=15)


class TestCollecteurDonnees:
    def test_source_inconnue(self, collecteur):
        with pytest.raises(ValueError, match="Source inconnue"):
            collecteur.collecter_source("source_inexistante")

    def test_telecharger_csv_invalide(self, collecteur):
        with pytest.raises(Exception):
            collecteur.telecharger_csv("https://invalid.example.com/data.csv")

    def test_telecharger_json_invalide(self, collecteur):
        with pytest.raises(Exception):
            collecteur.telecharger_json("https://invalid.example.com/data.json")
