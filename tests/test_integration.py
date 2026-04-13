"""Tests d'intégration — vérifient le bon fonctionnement de la chaîne complète."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.mongodb.gestionnaire_mongo import GestionnaireMongo
from src.api.api import app


@pytest.fixture
def mongo():
    """Connexion MongoDB pour les tests (utilise la base réelle peuplée par le pipeline)."""
    m = GestionnaireMongo()
    yield m
    m.fermer()


@pytest.fixture
def client():
    """Client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestMongoDB:
    def test_connexion_et_donnees(self, mongo):
        count = mongo.compter_documents("clean")
        assert count > 0, "La collection clean doit contenir des données"

    def test_recherche_par_type(self, mongo):
        types = mongo.obtenir_types()
        assert len(types) > 0
        # Recherche avec un type existant
        resultats = mongo.rechercher({"type_hebergement": types[0]}, limite=5)
        assert len(resultats) > 0

    def test_statistiques(self, mongo):
        stats = mongo.obtenir_statistiques()
        assert stats["total"] > 0
        assert len(stats["par_type"]) > 0

    def test_departements(self, mongo):
        depts = mongo.obtenir_departements()
        assert len(depts) > 0


class TestAPI:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["documents"] > 0

    def test_lister_hebergements(self, client):
        resp = client.get("/api/hebergements?limit=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] > 0
        assert len(data["data"]) <= 5

    def test_filtrer_par_type(self, client):
        # Récupérer un type existant
        types_resp = client.get("/api/types")
        types = types_resp.get_json()["types"]
        if types:
            resp = client.get(f"/api/hebergements?type={types[0]}")
            assert resp.status_code == 200

    def test_recherche_textuelle(self, client):
        resp = client.get("/api/hebergements?q=nantes")
        assert resp.status_code == 200

    def test_lister_types(self, client):
        resp = client.get("/api/types")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["types"]) > 0

    def test_lister_departements(self, client):
        resp = client.get("/api/departements")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["departements"]) > 0

    def test_statistiques(self, client):
        resp = client.get("/api/statistiques")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] > 0

    def test_hebergement_introuvable(self, client):
        resp = client.get("/api/hebergements/id_inexistant_xyz")
        assert resp.status_code == 404

    def test_lister_communes(self, client):
        resp = client.get("/api/communes")
        assert resp.status_code == 200
        assert len(resp.get_json()["communes"]) > 0
