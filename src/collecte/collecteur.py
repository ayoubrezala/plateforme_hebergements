"""
Module de collecte des données depuis data.gouv.fr.
Télécharge les fichiers CSV et JSON des hébergements touristiques.
"""

import csv
import io
import json
import logging
import requests
from typing import Optional

from src.config import SOURCES_DONNEES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class CollecteurDonnees:
    """Responsable de la collecte des données depuis les sources open data."""

    def __init__(self, timeout: int = 30):
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "PlatformeHebergements/1.0"})

    def telecharger_csv(self, url: str, delimiter: str = ";") -> list[dict]:
        """Télécharge et parse un fichier CSV depuis une URL."""
        logger.info(f"Téléchargement CSV : {url}")
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()

        # Détection de l'encodage
        contenu = response.content
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                texte = contenu.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            texte = contenu.decode("utf-8", errors="replace")

        # Détection automatique du délimiteur
        premiere_ligne = texte.split("\n")[0]
        if delimiter not in premiere_ligne:
            for d in [",", "\t", "|"]:
                if d in premiere_ligne:
                    delimiter = d
                    break

        lecteur = csv.DictReader(io.StringIO(texte), delimiter=delimiter)
        donnees = [dict(ligne) for ligne in lecteur]
        logger.info(f"  → {len(donnees)} enregistrements récupérés")
        return donnees

    def telecharger_json(self, url: str) -> list[dict]:
        """Télécharge et parse un fichier JSON depuis une URL."""
        logger.info(f"Téléchargement JSON : {url}")
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        donnees = response.json()
        if isinstance(donnees, dict):
            donnees = donnees.get("results", donnees.get("data", [donnees]))
        logger.info(f"  → {len(donnees)} enregistrements récupérés")
        return donnees

    def collecter_source(self, cle_source: str) -> list[dict]:
        """Collecte les données d'une source spécifique."""
        source = SOURCES_DONNEES.get(cle_source)
        if not source:
            raise ValueError(f"Source inconnue : {cle_source}")

        # Préférer JSON si disponible, sinon CSV
        if source["url_json"]:
            try:
                return self.telecharger_json(source["url_json"])
            except Exception as e:
                logger.warning(f"Échec JSON pour {cle_source}, tentative CSV : {e}")

        return self.telecharger_csv(source["url_csv"])

    def collecter_tout(self) -> dict[str, list[dict]]:
        """Collecte les données de toutes les sources configurées."""
        resultats = {}
        for cle, source in SOURCES_DONNEES.items():
            try:
                donnees = self.collecter_source(cle)
                resultats[cle] = donnees
                logger.info(f"✓ {source['nom']} : {len(donnees)} enregistrements")
            except Exception as e:
                logger.error(f"✗ Erreur pour {source['nom']} : {e}")
                resultats[cle] = []
        return resultats


def collecter_donnees() -> dict[str, list[dict]]:
    """Point d'entrée pour la collecte complète."""
    collecteur = CollecteurDonnees()
    return collecteur.collecter_tout()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    resultats = collecter_donnees()
    total = sum(len(v) for v in resultats.values())
    print(f"\nTotal collecté : {total} enregistrements")
