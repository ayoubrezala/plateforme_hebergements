"""
Module de gestion MongoDB.
Gère le stockage des données brutes (raw) et nettoyées (clean).
"""

import logging
from pymongo import MongoClient, ASCENDING, GEOSPHERE
from pymongo.errors import BulkWriteError
from typing import Optional

from src.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION_RAW, MONGO_COLLECTION_CLEAN

logger = logging.getLogger(__name__)


class GestionnaireMongo:
    """Interface avec la base de données MongoDB."""

    def __init__(self, uri: str = MONGO_URI, db_name: str = MONGO_DB):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._raw = self._db[MONGO_COLLECTION_RAW]
        self._clean = self._db[MONGO_COLLECTION_CLEAN]

    def initialiser_index(self):
        """Crée les index pour optimiser les requêtes."""
        # Index sur la collection nettoyée
        self._clean.create_index([("commune", ASCENDING)])
        self._clean.create_index([("type_hebergement", ASCENDING)])
        self._clean.create_index([("departement", ASCENDING)])
        self._clean.create_index([("code_postal", ASCENDING)])
        self._clean.create_index([("_id_unique", ASCENDING)], unique=True)

        # Index géospatial (si coordonnées présentes)
        self._clean.create_index([("localisation", GEOSPHERE)], sparse=True)
        logger.info("Index MongoDB créés avec succès")

    def inserer_donnees_brutes(self, donnees: list[dict], source: str):
        """Insère les données brutes dans la collection raw."""
        if not donnees:
            return 0
        for doc in donnees:
            doc["_source"] = source
        result = self._raw.insert_many(donnees)
        count = len(result.inserted_ids)
        logger.info(f"  → {count} documents bruts insérés (source: {source})")
        return count

    def inserer_donnees_propres(self, donnees: list[dict]):
        """Insère les données nettoyées avec gestion des doublons."""
        if not donnees:
            return 0

        # Ajout du champ GeoJSON pour les requêtes géospatiales
        for doc in donnees:
            if doc.get("latitude") and doc.get("longitude"):
                doc["localisation"] = {
                    "type": "Point",
                    "coordinates": [doc["longitude"], doc["latitude"]]
                }

        inseres = 0
        for doc in donnees:
            try:
                self._clean.update_one(
                    {"_id_unique": doc["_id_unique"]},
                    {"$set": doc},
                    upsert=True
                )
                inseres += 1
            except Exception as e:
                logger.warning(f"Erreur insertion : {e}")

        logger.info(f"  → {inseres} documents propres insérés/mis à jour")
        return inseres

    def compter_documents(self, collection: str = "clean") -> int:
        """Retourne le nombre de documents dans une collection."""
        coll = self._clean if collection == "clean" else self._raw
        return coll.count_documents({})

    def rechercher(self, filtres: dict = None, projection: dict = None,
                   limite: int = 100, offset: int = 0) -> list[dict]:
        """Recherche des hébergements avec filtres."""
        filtres = filtres or {}
        curseur = self._clean.find(filtres, projection).skip(offset).limit(limite)
        return list(curseur)

    def obtenir_statistiques(self) -> dict:
        """Retourne des statistiques sur les données."""
        pipeline = [
            {"$group": {
                "_id": "$type_hebergement",
                "count": {"$sum": 1},
                "avg_capacite": {"$avg": "$capacite_personnes"}
            }},
            {"$sort": {"count": -1}}
        ]
        types = list(self._clean.aggregate(pipeline))

        pipeline_dept = [
            {"$group": {"_id": "$departement", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        departements = list(self._clean.aggregate(pipeline_dept))

        return {
            "total": self._clean.count_documents({}),
            "par_type": types,
            "par_departement": departements
        }

    def obtenir_types(self) -> list[str]:
        """Retourne la liste des types d'hébergement distincts."""
        return self._clean.distinct("type_hebergement")

    def obtenir_communes(self) -> list[str]:
        """Retourne la liste des communes distinctes."""
        return sorted(self._clean.distinct("commune"))

    def obtenir_departements(self) -> list[str]:
        """Retourne la liste des départements distincts."""
        return sorted([d for d in self._clean.distinct("departement") if d])

    def vider_collections(self):
        """Supprime toutes les données (utile pour les tests)."""
        self._raw.delete_many({})
        self._clean.delete_many({})
        logger.info("Collections vidées")

    def fermer(self):
        """Ferme la connexion."""
        self._client.close()

    def exporter_tout(self) -> list[dict]:
        """Exporte tous les documents propres."""
        docs = list(self._clean.find({}, {"_id": 0, "localisation": 0}))
        return docs
