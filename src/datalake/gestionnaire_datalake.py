"""
Module Data Lake.
Exporte les données en fichiers JSON et CSV organisés par catégorie.
"""

import csv
import json
import logging
import os
from datetime import datetime

from src.config import DATALAKE_DIR

logger = logging.getLogger(__name__)


class GestionnaireDatalake:
    """Gère l'export des données vers le Data Lake (fichiers JSON/CSV)."""

    def __init__(self, repertoire: str = DATALAKE_DIR):
        self._repertoire = repertoire
        os.makedirs(repertoire, exist_ok=True)
        # Sous-dossiers par zone
        for sous_rep in ["raw", "clean", "analytics"]:
            os.makedirs(os.path.join(repertoire, sous_rep), exist_ok=True)

    def exporter_json(self, donnees: list[dict], nom_fichier: str, zone: str = "clean"):
        """Exporte les données au format JSON."""
        chemin = os.path.join(self._repertoire, zone, f"{nom_fichier}.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Export JSON : {chemin} ({len(donnees)} enregistrements)")
        return chemin

    def exporter_csv(self, donnees: list[dict], nom_fichier: str, zone: str = "clean"):
        """Exporte les données au format CSV."""
        if not donnees:
            return None
        chemin = os.path.join(self._repertoire, zone, f"{nom_fichier}.csv")
        cles = donnees[0].keys()
        with open(chemin, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cles, delimiter=";")
            writer.writeheader()
            writer.writerows(donnees)
        logger.info(f"Export CSV : {chemin} ({len(donnees)} enregistrements)")
        return chemin

    def alimenter(self, donnees_brutes: dict[str, list[dict]], donnees_propres: list[dict]):
        """Alimente le Data Lake complet : raw, clean et analytics."""
        horodatage = datetime.now().strftime("%Y%m%d")

        # Zone raw : données brutes par source
        for source, donnees in donnees_brutes.items():
            self.exporter_json(donnees, f"{source}_{horodatage}", zone="raw")
            self.exporter_csv(donnees, f"{source}_{horodatage}", zone="raw")

        # Zone clean : données nettoyées
        self.exporter_json(donnees_propres, f"hebergements_clean_{horodatage}")
        self.exporter_csv(donnees_propres, f"hebergements_clean_{horodatage}")

        # Zone analytics : agrégations
        self._generer_analytics(donnees_propres, horodatage)

        logger.info(f"Data Lake alimenté : {self._repertoire}")

    def _generer_analytics(self, donnees: list[dict], horodatage: str):
        """Génère des fichiers d'agrégation pour l'analyse BI."""
        # Agrégation par type
        par_type = {}
        for d in donnees:
            t = d.get("type_hebergement", "Inconnu")
            par_type.setdefault(t, {"type": t, "count": 0, "communes": set()})
            par_type[t]["count"] += 1
            if d.get("commune"):
                par_type[t]["communes"].add(d["commune"])

        analytics_type = [
            {"type": v["type"], "nombre": v["count"], "communes_couvertes": len(v["communes"])}
            for v in par_type.values()
        ]
        self.exporter_json(analytics_type, f"stats_par_type_{horodatage}", zone="analytics")

        # Agrégation par département
        par_dept = {}
        for d in donnees:
            dept = d.get("departement", "Inconnu")
            par_dept.setdefault(dept, {"departement": dept, "count": 0, "types": set()})
            par_dept[dept]["count"] += 1
            par_dept[dept]["types"].add(d.get("type_hebergement", ""))

        analytics_dept = [
            {"departement": v["departement"], "nombre": v["count"],
             "types_disponibles": list(v["types"])}
            for v in par_dept.values()
        ]
        self.exporter_json(analytics_dept, f"stats_par_departement_{horodatage}", zone="analytics")
        self.exporter_csv(
            [{"departement": a["departement"], "nombre": a["nombre"],
              "types_disponibles": ", ".join(a["types_disponibles"])} for a in analytics_dept],
            f"stats_par_departement_{horodatage}", zone="analytics"
        )
