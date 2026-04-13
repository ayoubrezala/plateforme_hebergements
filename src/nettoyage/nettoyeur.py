"""
Module de nettoyage des données brutes.
Normalise, déduplique et convertit les types pour obtenir des données exploitables.
"""

import hashlib
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


class NettoyeurDonnees:
    """Nettoie et normalise les données d'hébergements touristiques."""

    def nettoyer_texte(self, valeur: Any) -> Optional[str]:
        """Normalise une chaîne de caractères."""
        if valeur is None or (isinstance(valeur, str) and valeur.strip() == ""):
            return None
        texte = str(valeur).strip()
        # Suppression des espaces multiples
        texte = re.sub(r"\s+", " ", texte)
        return texte

    def nettoyer_telephone(self, valeur: Any) -> Optional[str]:
        """Normalise un numéro de téléphone français."""
        if valeur is None:
            return None
        if isinstance(valeur, list):
            valeur = valeur[0] if valeur else None
        if not valeur:
            return None
        tel = re.sub(r"[^\d+]", "", str(valeur))
        if tel.startswith("0") and len(tel) == 10:
            return f"+33{tel[1:]}"
        return tel if tel else None

    def nettoyer_coordonnees(self, lat: Any, lon: Any) -> dict:
        """Valide et normalise les coordonnées GPS."""
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            # Vérification des bornes pour la France métropolitaine
            if 41.0 <= lat_f <= 51.5 and -5.5 <= lon_f <= 10.0:
                return {"latitude": round(lat_f, 6), "longitude": round(lon_f, 6)}
        except (TypeError, ValueError):
            pass
        return {"latitude": None, "longitude": None}

    def nettoyer_type(self, valeur: Any) -> str:
        """Normalise le type d'hébergement."""
        if isinstance(valeur, list):
            valeur = valeur[0] if valeur else ""
        valeur = str(valeur).strip().lower()

        correspondances = {
            "hôtel": "Hôtel",
            "hotel": "Hôtel",
            "camping": "Camping",
            "meublé": "Meublé de tourisme",
            "meublés": "Meublé de tourisme",
            "chambre d'hôtes": "Chambre d'hôtes",
            "chambre d'hotes": "Chambre d'hôtes",
            "résidence": "Résidence de tourisme",
            "residence": "Résidence de tourisme",
            "gîte": "Gîte",
            "gite": "Gîte",
            "village": "Village vacances",
            "auberge": "Auberge de jeunesse",
            "centre": "Centre de vacances",
        }

        for motif, categorie in correspondances.items():
            if motif in valeur:
                return categorie
        return valeur.title() if valeur else "Non classé"

    def nettoyer_capacite(self, valeur: Any) -> Optional[int]:
        """Convertit une capacité en entier."""
        if valeur is None:
            return None
        try:
            v = int(float(str(valeur)))
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None

    def generer_id_unique(self, enregistrement: dict) -> str:
        """Génère un identifiant unique basé sur le contenu."""
        cle = f"{enregistrement.get('nom', '')}-{enregistrement.get('commune', '')}-{enregistrement.get('code_postal', '')}"
        return hashlib.md5(cle.encode()).hexdigest()

    def nettoyer_enregistrement(self, brut: dict, source: str) -> dict:
        """Nettoie un enregistrement brut et produit un document normalisé."""
        nom = self.nettoyer_texte(brut.get("nomoffre") or brut.get("nom") or brut.get("Nom"))
        commune = self.nettoyer_texte(brut.get("commune") or brut.get("Commune") or brut.get("ville"))
        code_postal = self.nettoyer_texte(brut.get("codepostal") or brut.get("CodePostal") or brut.get("cp"))

        coords = self.nettoyer_coordonnees(
            brut.get("latitude") or brut.get("Latitude"),
            brut.get("longitude") or brut.get("Longitude")
        )

        # Construction de l'adresse complète
        parties_adresse = [
            brut.get("adresse1"), brut.get("adresse1suite"),
            brut.get("adresse2"), brut.get("adresse3")
        ]
        adresse = ", ".join(filter(None, [self.nettoyer_texte(p) for p in parties_adresse])) or None

        type_hebergement = self.nettoyer_type(brut.get("type") or brut.get("Type") or "")

        # Capacité
        capacite_personnes = self.nettoyer_capacite(
            brut.get("capacitenbpersonnes") or brut.get("capacite") or brut.get("nombrepersonnes")
        )
        capacite_chambres = self.nettoyer_capacite(
            brut.get("capacitenbchambres") or brut.get("nb_chambres")
        )

        # Classement étoiles
        classement = self.nettoyer_texte(brut.get("classement") or brut.get("categorie"))

        # Contact
        telephone = self.nettoyer_telephone(brut.get("commtel") or brut.get("telephone"))
        email = self.nettoyer_texte(brut.get("commmail") or brut.get("email"))
        site_web = self.nettoyer_texte(brut.get("commweb") or brut.get("site_web"))

        # Tarifs
        tarif_min = self.nettoyer_capacite(brut.get("tarif1min") or brut.get("tarifmin"))
        tarif_max = self.nettoyer_capacite(brut.get("tarif1max") or brut.get("tarifmax"))

        document = {
            "nom": nom,
            "type_hebergement": type_hebergement,
            "adresse": adresse,
            "code_postal": code_postal,
            "commune": commune,
            "code_insee": self.nettoyer_texte(brut.get("codeinseecommune")),
            "departement": code_postal[:2] if code_postal and len(code_postal) >= 2 else None,
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "capacite_personnes": capacite_personnes,
            "capacite_chambres": capacite_chambres,
            "classement": classement,
            "telephone": telephone,
            "email": email,
            "site_web": site_web,
            "tarif_min": tarif_min,
            "tarif_max": tarif_max,
            "source": source,
        }

        document["_id_unique"] = self.generer_id_unique(document)
        return document

    def nettoyer_lot(self, donnees_brutes: list[dict], source: str) -> list[dict]:
        """Nettoie un lot complet de données et supprime les doublons."""
        resultats = {}
        ignores = 0

        for brut in donnees_brutes:
            try:
                propre = self.nettoyer_enregistrement(brut, source)
                if not propre["nom"]:
                    ignores += 1
                    continue
                # Dédoublonnage par identifiant unique
                resultats[propre["_id_unique"]] = propre
            except Exception as e:
                logger.warning(f"Erreur nettoyage : {e}")
                ignores += 1

        logger.info(f"Nettoyage terminé : {len(resultats)} propres, {ignores} ignorés, "
                     f"{len(donnees_brutes) - len(resultats) - ignores} doublons supprimés")
        return list(resultats.values())
