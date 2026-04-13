"""
Configuration globale du projet.
Centralise les paramètres de connexion et les URLs des sources de données.
"""

import os

# --- Sources de données (data.gouv.fr) ---
SOURCES_DONNEES = {
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
    "hebergements_saint_malo": {
        "nom": "Hébergements touristiques - Saint-Malo",
        "url_csv": "https://static.data.gouv.fr/resources/hebergements-touristiques-1/20150622-165725/35288-STMALO-Hebergements-touristiques.csv",
        "url_json": None,
        "type": "mixte"
    }
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
