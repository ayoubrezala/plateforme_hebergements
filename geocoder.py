#!/usr/bin/env python3
"""
Géocode les hébergements sans coordonnées GPS via l'API adresse du gouvernement.
https://adresse.data.gouv.fr/api-doc/adresse — gratuit, sans clé API.

Utilise l'endpoint /search avec adresse + code postal pour obtenir lat/lon,
puis met à jour MongoDB (collections clean + le champ localisation GeoJSON).
"""

import sys
import logging
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.mongodb.gestionnaire_mongo import GestionnaireMongo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

API_ADRESSE = "https://api-adresse.data.gouv.fr/search/"


def geocoder_adresse(adresse: str, code_postal: str, commune: str) -> dict | None:
    """Géocode une adresse via l'API adresse du gouvernement."""
    # Construire la requête la plus précise possible
    q_parts = []
    if adresse:
        q_parts.append(adresse)
    if commune:
        q_parts.append(commune)

    q = " ".join(q_parts)
    if not q.strip():
        return None

    params = {"q": q, "limit": 1}
    if code_postal:
        params["postcode"] = code_postal

    try:
        resp = requests.get(API_ADRESSE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        features = data.get("features", [])
        if not features:
            return None

        props = features[0]["properties"]
        coords = features[0]["geometry"]["coordinates"]  # [lon, lat]
        score = props.get("score", 0)

        # Seuil de confiance minimum
        if score < 0.3:
            return None

        lon, lat = coords
        # Vérification bornes France métropolitaine
        if not (41.0 <= lat <= 51.5 and -5.5 <= lon <= 10.0):
            return None

        return {"latitude": round(lat, 6), "longitude": round(lon, 6), "score": score}

    except Exception:
        return None


def geocoder_tout():
    """Géocode tous les hébergements sans coordonnées dans MongoDB."""
    mongo = GestionnaireMongo()
    db = mongo._db
    collection = db.clean_hebergements

    # Récupérer les hébergements sans coordonnées
    sans_coords = list(collection.find(
        {"$or": [{"latitude": None}, {"longitude": None}]},
        {"_id": 1, "_id_unique": 1, "adresse": 1, "code_postal": 1, "commune": 1, "nom": 1}
    ))

    total = len(sans_coords)
    logger.info(f"Hébergements sans coordonnées : {total}")

    if total == 0:
        logger.info("Rien à géocoder.")
        return

    geocodes = 0
    echecs = 0

    for i, doc in enumerate(sans_coords):
        result = geocoder_adresse(
            doc.get("adresse"),
            doc.get("code_postal"),
            doc.get("commune")
        )

        if result:
            # Mise à jour MongoDB
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "localisation": {
                        "type": "Point",
                        "coordinates": [result["longitude"], result["latitude"]]
                    }
                }}
            )
            geocodes += 1
        else:
            echecs += 1

        # Log progression toutes les 500 itérations
        if (i + 1) % 500 == 0:
            logger.info(f"  Progression : {i+1}/{total} ({geocodes} géocodés, {echecs} échoués)")

        # Respecter la limite de l'API (50 req/s max, on reste à ~30/s)
        if (i + 1) % 30 == 0:
            time.sleep(1)

    logger.info(f"\nGéocodage terminé :")
    logger.info(f"  Géocodés avec succès : {geocodes}/{total}")
    logger.info(f"  Échecs : {echecs}/{total}")

    # Vérification finale
    encore_sans = collection.count_documents({"$or": [{"latitude": None}, {"longitude": None}]})
    total_final = collection.count_documents({})
    logger.info(f"  Couverture GPS finale : {total_final - encore_sans}/{total_final} "
                f"({round(100*(total_final-encore_sans)/total_final)}%)")

    mongo.fermer()


if __name__ == "__main__":
    geocoder_tout()
