"""
Module Data Warehouse (MariaDB).
Crée les tables analytiques et charge les données nettoyées pour l'exploitation BI.
"""

import logging
import mariadb
from typing import Optional

from src.config import MARIADB_CONFIG

logger = logging.getLogger(__name__)

# Schéma du Data Warehouse (modèle en étoile simplifié)
SQL_CREATION = """
CREATE DATABASE IF NOT EXISTS dw_hebergements;
USE dw_hebergements;

-- Table de dimension : types d'hébergement
CREATE TABLE IF NOT EXISTS dim_type_hebergement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_hebergement VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table de dimension : localisation géographique
CREATE TABLE IF NOT EXISTS dim_localisation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commune VARCHAR(200),
    code_postal VARCHAR(10),
    departement VARCHAR(5),
    code_insee VARCHAR(10),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    UNIQUE KEY uk_localisation (commune, code_postal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table de dimension : source de données
CREATE TABLE IF NOT EXISTS dim_source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_source VARCHAR(200) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table de faits : hébergements touristiques
CREATE TABLE IF NOT EXISTS fait_hebergement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_unique VARCHAR(64) NOT NULL UNIQUE,
    nom VARCHAR(500),
    adresse TEXT,
    id_type INT,
    id_localisation INT,
    id_source INT,
    capacite_personnes INT,
    capacite_chambres INT,
    classement VARCHAR(100),
    telephone VARCHAR(50),
    email VARCHAR(200),
    site_web VARCHAR(500),
    tarif_min INT,
    tarif_max INT,
    date_chargement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_type) REFERENCES dim_type_hebergement(id),
    FOREIGN KEY (id_localisation) REFERENCES dim_localisation(id),
    FOREIGN KEY (id_source) REFERENCES dim_source(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Vue analytique : résumé par département et type
CREATE OR REPLACE VIEW vue_resume_departement AS
SELECT
    dl.departement,
    dt.type_hebergement,
    COUNT(*) AS nombre_hebergements,
    AVG(fh.capacite_personnes) AS capacite_moyenne,
    AVG(fh.tarif_min) AS tarif_min_moyen,
    AVG(fh.tarif_max) AS tarif_max_moyen
FROM fait_hebergement fh
JOIN dim_type_hebergement dt ON fh.id_type = dt.id
JOIN dim_localisation dl ON fh.id_localisation = dl.id
GROUP BY dl.departement, dt.type_hebergement;

-- Vue analytique : résumé par commune
CREATE OR REPLACE VIEW vue_resume_commune AS
SELECT
    dl.commune,
    dl.departement,
    COUNT(*) AS nombre_hebergements,
    GROUP_CONCAT(DISTINCT dt.type_hebergement SEPARATOR ', ') AS types_disponibles,
    SUM(fh.capacite_personnes) AS capacite_totale
FROM fait_hebergement fh
JOIN dim_type_hebergement dt ON fh.id_type = dt.id
JOIN dim_localisation dl ON fh.id_localisation = dl.id
GROUP BY dl.commune, dl.departement;

-- Vue Power BI : table plate denormalisee pour import direct
CREATE OR REPLACE VIEW vue_powerbi_hebergements AS
SELECT
    fh.id,
    fh.id_unique,
    fh.nom,
    fh.adresse,
    dt.type_hebergement,
    dl.commune,
    dl.code_postal,
    dl.departement,
    dl.latitude,
    dl.longitude,
    ds.nom_source AS source,
    fh.capacite_personnes,
    fh.capacite_chambres,
    fh.classement,
    fh.telephone,
    fh.email,
    fh.site_web,
    fh.tarif_min,
    fh.tarif_max,
    fh.date_chargement,
    CASE
        WHEN fh.classement LIKE '%1%' THEN 1
        WHEN fh.classement LIKE '%2%' THEN 2
        WHEN fh.classement LIKE '%3%' THEN 3
        WHEN fh.classement LIKE '%4%' THEN 4
        WHEN fh.classement LIKE '%5%' THEN 5
        ELSE 0
    END AS nb_etoiles,
    CASE
        WHEN fh.tarif_min IS NOT NULL AND fh.tarif_max IS NOT NULL
        THEN ROUND((fh.tarif_min + fh.tarif_max) / 2)
        ELSE COALESCE(fh.tarif_min, fh.tarif_max)
    END AS tarif_moyen,
    CASE
        WHEN dl.departement = '44' THEN 'Loire-Atlantique'
        WHEN dl.departement = '49' THEN 'Maine-et-Loire'
        WHEN dl.departement = '53' THEN 'Mayenne'
        WHEN dl.departement = '72' THEN 'Sarthe'
        WHEN dl.departement = '85' THEN 'Vendee'
        WHEN dl.departement = '35' THEN 'Ille-et-Vilaine'
        ELSE CONCAT('Dept. ', dl.departement)
    END AS nom_departement
FROM fait_hebergement fh
JOIN dim_type_hebergement dt ON fh.id_type = dt.id
JOIN dim_localisation dl ON fh.id_localisation = dl.id
JOIN dim_source ds ON fh.id_source = ds.id;

-- Vue Power BI : KPIs globaux
CREATE OR REPLACE VIEW vue_powerbi_kpis AS
SELECT
    COUNT(*) AS total_hebergements,
    COUNT(DISTINCT dl.commune) AS total_communes,
    COUNT(DISTINCT dl.departement) AS total_departements,
    COUNT(DISTINCT dt.type_hebergement) AS total_types,
    ROUND(AVG(fh.capacite_personnes), 1) AS capacite_moyenne,
    SUM(fh.capacite_personnes) AS capacite_totale,
    ROUND(AVG(fh.tarif_min), 0) AS tarif_min_moyen,
    ROUND(AVG(fh.tarif_max), 0) AS tarif_max_moyen,
    COUNT(CASE WHEN fh.email IS NOT NULL AND fh.email != '' THEN 1 END) AS avec_email,
    COUNT(CASE WHEN fh.site_web IS NOT NULL AND fh.site_web != '' THEN 1 END) AS avec_site_web,
    COUNT(CASE WHEN fh.classement IS NOT NULL AND fh.classement != '' THEN 1 END) AS avec_classement
FROM fait_hebergement fh
JOIN dim_type_hebergement dt ON fh.id_type = dt.id
JOIN dim_localisation dl ON fh.id_localisation = dl.id;

-- Vue Power BI : top 20 communes
CREATE OR REPLACE VIEW vue_powerbi_top_communes AS
SELECT
    dl.commune,
    dl.departement,
    COUNT(*) AS nombre_hebergements,
    SUM(fh.capacite_personnes) AS capacite_totale,
    COUNT(DISTINCT dt.type_hebergement) AS diversite_types,
    ROUND(AVG(fh.tarif_min), 0) AS tarif_min_moyen
FROM fait_hebergement fh
JOIN dim_type_hebergement dt ON fh.id_type = dt.id
JOIN dim_localisation dl ON fh.id_localisation = dl.id
GROUP BY dl.commune, dl.departement
ORDER BY nombre_hebergements DESC
LIMIT 20;
"""


class GestionnaireWarehouse:
    """Gère le Data Warehouse MariaDB avec un modèle en étoile."""

    def __init__(self, config: dict = None):
        self._config = config or MARIADB_CONFIG
        self._conn = None

    def connecter(self):
        """Ouvre la connexion à MariaDB."""
        config_connexion = {k: v for k, v in self._config.items() if k != "database"}
        self._conn = mariadb.connect(**config_connexion)
        self._conn.autocommit = True
        logger.info("Connecté à MariaDB")

    def initialiser_schema(self):
        """Crée la base et les tables du Data Warehouse."""
        curseur = self._conn.cursor()
        for statement in SQL_CREATION.split(";"):
            statement = statement.strip()
            if statement:
                curseur.execute(statement)
        curseur.close()
        logger.info("Schéma Data Warehouse créé")

    def _obtenir_ou_creer_type(self, curseur, type_hebergement: str) -> int:
        """Récupère ou crée un type d'hébergement et retourne son ID."""
        curseur.execute(
            "SELECT id FROM dim_type_hebergement WHERE type_hebergement = ?",
            (type_hebergement,)
        )
        row = curseur.fetchone()
        if row:
            return row[0]
        curseur.execute(
            "INSERT INTO dim_type_hebergement (type_hebergement) VALUES (?)",
            (type_hebergement,)
        )
        return curseur.lastrowid

    def _obtenir_ou_creer_localisation(self, curseur, doc: dict) -> int:
        """Récupère ou crée une localisation et retourne son ID."""
        commune = doc.get("commune")
        cp = doc.get("code_postal")
        curseur.execute(
            "SELECT id FROM dim_localisation WHERE commune = ? AND code_postal = ?",
            (commune, cp)
        )
        row = curseur.fetchone()
        if row:
            return row[0]
        curseur.execute(
            """INSERT INTO dim_localisation
               (commune, code_postal, departement, code_insee, latitude, longitude)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (commune, cp, doc.get("departement"), doc.get("code_insee"),
             doc.get("latitude"), doc.get("longitude"))
        )
        return curseur.lastrowid

    def _obtenir_ou_creer_source(self, curseur, source: str) -> int:
        """Récupère ou crée une source et retourne son ID."""
        curseur.execute("SELECT id FROM dim_source WHERE nom_source = ?", (source,))
        row = curseur.fetchone()
        if row:
            return row[0]
        curseur.execute("INSERT INTO dim_source (nom_source) VALUES (?)", (source,))
        return curseur.lastrowid

    def charger_donnees(self, donnees: list[dict]):
        """Charge les données nettoyées dans le Data Warehouse."""
        curseur = self._conn.cursor()
        curseur.execute("USE dw_hebergements")

        inseres = 0
        for doc in donnees:
            try:
                id_type = self._obtenir_ou_creer_type(curseur, doc.get("type_hebergement", "Non classé"))
                id_loc = self._obtenir_ou_creer_localisation(curseur, doc)
                id_source = self._obtenir_ou_creer_source(curseur, doc.get("source", "inconnu"))

                curseur.execute(
                    """INSERT INTO fait_hebergement
                       (id_unique, nom, adresse, id_type, id_localisation, id_source,
                        capacite_personnes, capacite_chambres, classement,
                        telephone, email, site_web, tarif_min, tarif_max)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ON DUPLICATE KEY UPDATE nom=VALUES(nom), adresse=VALUES(adresse)""",
                    (doc["_id_unique"], doc.get("nom"), doc.get("adresse"),
                     id_type, id_loc, id_source,
                     doc.get("capacite_personnes"), doc.get("capacite_chambres"),
                     doc.get("classement"),
                     doc.get("telephone"), doc.get("email"), doc.get("site_web"),
                     doc.get("tarif_min"), doc.get("tarif_max"))
                )
                inseres += 1
            except Exception as e:
                logger.warning(f"Erreur chargement DW : {e}")

        curseur.close()
        logger.info(f"  → {inseres} enregistrements chargés dans le Data Warehouse")
        return inseres

    def executer_requete(self, sql: str, params: tuple = None) -> list[dict]:
        """Exécute une requête SQL et retourne les résultats."""
        curseur = self._conn.cursor()
        curseur.execute("USE dw_hebergements")
        curseur.execute(sql, params or ())
        colonnes = [desc[0] for desc in curseur.description] if curseur.description else []
        resultats = [dict(zip(colonnes, row)) for row in curseur.fetchall()]
        curseur.close()
        return resultats

    def obtenir_statistiques(self) -> dict:
        """Retourne les statistiques BI depuis le Data Warehouse."""
        stats = {}
        stats["par_departement"] = self.executer_requete(
            "SELECT * FROM vue_resume_departement ORDER BY nombre_hebergements DESC"
        )
        stats["par_commune"] = self.executer_requete(
            "SELECT * FROM vue_resume_commune ORDER BY nombre_hebergements DESC LIMIT 20"
        )
        stats["total"] = self.executer_requete(
            "SELECT COUNT(*) AS total FROM fait_hebergement"
        )[0]["total"]
        return stats

    def fermer(self):
        """Ferme la connexion."""
        if self._conn:
            self._conn.close()
