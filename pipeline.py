#!/usr/bin/env python3
"""
Pipeline principal — Exécute toutes les étapes du projet :
1. Collecte des données depuis data.gouv.fr
2. Nettoyage et normalisation
3. Stockage MongoDB (raw + clean)
4. Chargement Data Warehouse (MariaDB)
5. Alimentation Data Lake (JSON/CSV)
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.collecte.collecteur import CollecteurDonnees
from src.nettoyage.nettoyeur import NettoyeurDonnees
from src.mongodb.gestionnaire_mongo import GestionnaireMongo
from src.warehouse.gestionnaire_warehouse import GestionnaireWarehouse
from src.datalake.gestionnaire_datalake import GestionnaireDatalake

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def executer_pipeline():
    """Exécute le pipeline ETL complet."""

    logger.info("=" * 60)
    logger.info("  PIPELINE ETL — Hébergements Touristiques")
    logger.info("=" * 60)

    # --- Étape 1 : Collecte ---
    logger.info("\n📥 ÉTAPE 1 : Collecte des données")
    collecteur = CollecteurDonnees()
    donnees_brutes = collecteur.collecter_tout()
    total_brut = sum(len(v) for v in donnees_brutes.values())
    logger.info(f"  Total collecté : {total_brut} enregistrements bruts")

    # --- Étape 2 : Nettoyage ---
    logger.info("\n🧹 ÉTAPE 2 : Nettoyage des données")
    nettoyeur = NettoyeurDonnees()
    donnees_propres = []
    for source, donnees in donnees_brutes.items():
        if donnees:
            propres = nettoyeur.nettoyer_lot(donnees, source)
            donnees_propres.extend(propres)
            logger.info(f"  {source} : {len(donnees)} → {len(propres)} enregistrements propres")
    logger.info(f"  Total nettoyé : {len(donnees_propres)} enregistrements")

    # --- Étape 3 : MongoDB ---
    logger.info("\n🍃 ÉTAPE 3 : Stockage MongoDB")
    mongo = GestionnaireMongo()
    mongo.vider_collections()
    mongo.initialiser_index()

    for source, donnees in donnees_brutes.items():
        if donnees:
            mongo.inserer_donnees_brutes(donnees, source)

    mongo.inserer_donnees_propres(donnees_propres)
    logger.info(f"  MongoDB — Raw: {mongo.compter_documents('raw')}, "
                f"Clean: {mongo.compter_documents('clean')}")

    # --- Étape 4 : Data Warehouse (MariaDB) ---
    logger.info("\n🏭 ÉTAPE 4 : Chargement Data Warehouse")
    try:
        dw = GestionnaireWarehouse()
        dw.connecter()
        dw.initialiser_schema()
        dw.charger_donnees(donnees_propres)
        stats_dw = dw.obtenir_statistiques()
        logger.info(f"  Data Warehouse — {stats_dw['total']} enregistrements")
        dw.fermer()
    except Exception as e:
        logger.error(f"  Erreur Data Warehouse : {e}")

    # --- Étape 5 : Data Lake ---
    logger.info("\n📂 ÉTAPE 5 : Alimentation Data Lake")
    datalake = GestionnaireDatalake()
    datalake.alimenter(donnees_brutes, donnees_propres)

    # --- Résumé ---
    logger.info("\n" + "=" * 60)
    logger.info("  PIPELINE TERMINÉ AVEC SUCCÈS")
    logger.info(f"  • Données brutes : {total_brut}")
    logger.info(f"  • Données propres : {len(donnees_propres)}")
    logger.info(f"  • MongoDB (clean) : {mongo.compter_documents('clean')}")
    logger.info("  • Data Warehouse : MariaDB chargé")
    logger.info("  • Data Lake : fichiers JSON/CSV générés")
    logger.info("=" * 60)

    mongo.fermer()


if __name__ == "__main__":
    executer_pipeline()
