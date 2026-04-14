"""
Configuration globale du projet.
Centralise les paramètres de connexion et les URLs des sources de données.
"""

import os

# --- Sources de données (data.gouv.fr) ---
SOURCES_DONNEES = {
    # --- Pays de la Loire ---
    "hebergements_collectifs": {
        "nom": "Hébergements collectifs touristiques - Pays de la Loire",
        "url_csv": "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-003_offre-touristique-hebergements-collectifs-rpdl/exports/csv?use_labels=true&delimiter=%3B",
        "url_json": "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-003_offre-touristique-hebergements-collectifs-rpdl/exports/json",
        "type": "collectif"
    },
    "hebergements_locatifs": {
        "nom": "Hébergements locatifs touristiques - Pays de la Loire",
        "url_csv": "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-004_offre-touristique-hebergements-locatifs-rpdl/exports/csv?use_labels=true&delimiter=%3B",
        "url_json": "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-004_offre-touristique-hebergements-locatifs-rpdl/exports/json",
        "type": "locatif"
    },
    "campings_pays_de_la_loire": {
        "nom": "Hôtelleries de plein air - Pays de la Loire",
        "url_csv": "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-005_offre-touristique-hotelleries-de-plein-air-rpdl/exports/csv?use_labels=true&delimiter=%3B",
        "url_json": "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-005_offre-touristique-hotelleries-de-plein-air-rpdl/exports/json",
        "type": "camping"
    },
    # --- Loire-Atlantique ---
    "collectifs_loire_atlantique": {
        "nom": "Hébergements collectifs - Loire-Atlantique",
        "url_csv": "https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/793866443_hebergements-collectifs-touristiques-en-loire-atlantique/exports/csv?delimiter=%3B",
        "url_json": "https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/793866443_hebergements-collectifs-touristiques-en-loire-atlantique/exports/json",
        "type": "collectif"
    },
    "locatifs_loire_atlantique": {
        "nom": "Hébergements locatifs - Loire-Atlantique",
        "url_csv": "https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/793866443_hebergements-locatifs-meubles-chambre-hotes-en-loire-atlantique/exports/csv?delimiter=%3B",
        "url_json": "https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/793866443_hebergements-locatifs-meubles-chambre-hotes-en-loire-atlantique/exports/json",
        "type": "locatif"
    },
    # --- Île-de-France ---
    "hotels_ile_de_france": {
        "nom": "Hôtels classés - Île-de-France",
        "url_csv": "https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/les_hotels_classes_en_ile-de-france/exports/csv?delimiter=%3B",
        "url_json": "https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/les_hotels_classes_en_ile-de-france/exports/json",
        "type": "hotel"
    },
    # --- National (Atout France) ---
    "hebergements_classes_france": {
        "nom": "Hébergements classés en France - Atout France",
        "url_csv": "https://data.classement.atout-france.fr/static/exportHebergementsClasses/hebergements_classes.csv",
        "url_json": None,
        "type": "mixte"
    },
    # --- Bretagne / Saint-Malo ---
    "hebergements_saint_malo": {
        "nom": "Hébergements touristiques - Saint-Malo",
        "url_csv": "https://static.data.gouv.fr/resources/hebergements-touristiques-1/20150622-165725/35288-STMALO-Hebergements-touristiques.csv",
        "url_json": None,
        "type": "mixte"
    },
}

# --- MongoDB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = "hebergements_touristiques"
MONGO_COLLECTION_RAW = "raw_hebergements"
MONGO_COLLECTION_CLEAN = "clean_hebergements"

# --- MariaDB (Data Warehouse) ---
# En mode Docker : connexion TCP via MARIADB_HOST
# En local : connexion unix_socket
if os.getenv("MARIADB_HOST"):
    MARIADB_CONFIG = {
        "host": os.getenv("MARIADB_HOST"),
        "port": int(os.getenv("MARIADB_PORT", "3306")),
        "user": os.getenv("MARIADB_USER", "etl_user"),
        "password": os.getenv("MARIADB_PASSWORD", "etl_pass"),
        "database": "dw_hebergements"
    }
else:
    MARIADB_CONFIG = {
        "unix_socket": os.getenv("MARIADB_SOCKET", "/tmp/mysql.sock"),
        "user": os.getenv("MARIADB_USER", "labelco-pilotes-video"),
        "database": "dw_hebergements"
    }

# --- Data Lake ---
DATALAKE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_lake")

# --- API ---
API_HOST = "0.0.0.0"
API_PORT = 5050
