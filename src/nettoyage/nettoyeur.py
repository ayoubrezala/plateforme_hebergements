"""
Module de nettoyage des données brutes.
Normalise, déduplique et convertit les types pour obtenir des données exploitables.
"""

import hashlib
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Images par type d'hébergement (Unsplash — libres de droits, ~15-20 par type)
IMAGES_PAR_TYPE = {
    "Hôtel": [
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1455587734955-081b22074882?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1522771739344-6a940b1c93e4?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1517840901100-8179e982acb7?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1590073242678-70ee3fc28e8e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1549294413-26f195200c16?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1495365200479-c4ed1d35e1aa?w=800&h=500&fit=crop",
    ],
    "Camping": [
        "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1510312305653-8ed496efae75?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1537905569824-f89f14cceb68?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1563299796-17596ed6b017?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1525811902-f2342640856e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1487730116645-74489c95b41b?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1585543805890-6051f7829f98?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1571863533956-01c88e79957e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1464207687429-7505649dae38?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1445308394109-4ec2920981b1?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1533575770077-052fa2c609fc?w=800&h=500&fit=crop",
    ],
    "Meublé de tourisme": [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1558036117-15d82a90b9b1?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1515263487990-61b07816b324?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560185127-6a8c82744f6e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800&h=500&fit=crop",
    ],
    "Chambre d'hôtes": [
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1618220179428-22790b461013?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560185127-bdf5e3a0e5b7?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1616046229478-9901c5536a45?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1521783988139-89397d761dce?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600210492493-0946911123ea?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1609766857041-ed402ea8069a?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800&h=500&fit=crop",
    ],
    "Gîte": [
        "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1587061949409-02df41d5e562?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1575517111478-7f6afd0973db?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1588880331179-bc9b93a8cb5e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1598228723793-52759bba239c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1576941089067-2de3c901e126?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560184897-ae75f418493e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800&h=500&fit=crop",
    ],
    "Résidence de tourisme": [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1460317442991-0ec209397118?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600573472591-ee6981cf81d6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560448075-cbc16bb4af8e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1567684014761-b65e2e59b9eb?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600047508788-786f3865b4b9?w=800&h=500&fit=crop",
    ],
    "Village vacances": [
        "https://images.unsplash.com/photo-1551918120-9739cb430c6d?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1573052905904-34ad7d3e092c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1543968332-f99478b1ebdc?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1602002418816-5c0aeef426aa?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1610641818989-c2051b5e2cfd?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1520483601560-389dff434fdf?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?w=800&h=500&fit=crop",
    ],
    "Auberge de jeunesse": [
        "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1520277739336-7bf67edfa768?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1574643156929-51fa098b0394?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1629140727571-9b5c6f6267b4?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1596436889106-be35e843f974?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1515191107209-c28698631303?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1590490359854-dfba19688a85?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1564078516393-cf04bd966897?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1559508551-44bff1de756b?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1604709177225-055f99402ea3?w=800&h=500&fit=crop",
    ],
    "Centre de vacances": [
        "https://images.unsplash.com/photo-1551918120-9739cb430c6d?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1610641818989-c2051b5e2cfd?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1602002418816-5c0aeef426aa?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1543968332-f99478b1ebdc?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1573052905904-34ad7d3e092c?w=800&h=500&fit=crop",
    ],
    "Parc résidentiel de loisirs": [
        "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1573052905904-34ad7d3e092c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1551918120-9739cb430c6d?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1520483601560-389dff434fdf?w=800&h=500&fit=crop",
    ],
    "default": [
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1480074568708-e7b720bb3f09?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1605146769289-440113cc3d00?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600573472591-ee6981cf81d6?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&h=500&fit=crop",
    ],
}


class NettoyeurDonnees:
    """Nettoie et normalise les données d'hébergements touristiques."""

    def generer_image_url(self, type_hebergement: str, id_unique: str) -> str:
        """Attribue une image cohérente selon le type (déterministe par id)."""
        images = IMAGES_PAR_TYPE.get(type_hebergement, IMAGES_PAR_TYPE["default"])
        index = int(hashlib.md5(id_unique.encode()).hexdigest()[:8], 16) % len(images)
        return images[index]

    def generer_disponibilites(self, id_unique: str) -> list[dict]:
        """Génère des créneaux de disponibilité réalistes pour les 90 prochains jours."""
        rng = random.Random(id_unique)
        disponibilites = []
        aujourd_hui = datetime.now().date()

        # Générer entre 3 et 8 créneaux disponibles
        nb_creneaux = rng.randint(3, 8)
        jour_courant = aujourd_hui + timedelta(days=rng.randint(1, 5))

        for _ in range(nb_creneaux):
            debut = jour_courant
            duree = rng.randint(2, 14)
            fin = debut + timedelta(days=duree)

            if (fin - aujourd_hui).days > 90:
                break

            prix_nuit = rng.randint(45, 220)
            disponibilites.append({
                "date_debut": debut.isoformat(),
                "date_fin": fin.isoformat(),
                "prix_nuit": prix_nuit,
                "places_restantes": rng.randint(1, 5),
            })

            # Trou entre créneaux (période indisponible)
            jour_courant = fin + timedelta(days=rng.randint(2, 10))

        return disponibilites

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
            "hotellerie": "Hôtel",
            "camping": "Camping",
            "hotellerie de plein air": "Camping",
            "plein air": "Camping",
            "terrain de camping": "Camping",
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
            "hostel": "Auberge de jeunesse",
            "centre": "Centre de vacances",
            "parc résidentiel": "Parc résidentiel de loisirs",
            "parc residentiel": "Parc résidentiel de loisirs",
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

    def _get(self, brut: dict, *cles) -> Any:
        """Récupère la première valeur non vide parmi les clés (insensible à la casse)."""
        # Recherche exacte d'abord
        for cle in cles:
            val = brut.get(cle)
            if val is not None and val != "":
                return val
        # Recherche insensible à la casse (pour les sources hétérogènes)
        brut_lower = {k.lower(): v for k, v in brut.items()}
        for cle in cles:
            val = brut_lower.get(cle.lower())
            if val is not None and val != "":
                return val
        return None

    def _extraire_coords_geo(self, brut: dict) -> tuple:
        """Extrait lat/lon depuis différents formats (champs séparés ou geo_point)."""
        lat = self._get(brut, "latitude", "Latitude", "lat")
        lon = self._get(brut, "longitude", "Longitude", "lon", "lng")

        # Format geo_point Opendatasoft : {"lat": ..., "lon": ...}
        if not lat or not lon:
            geo = brut.get("geo_point_2d") or brut.get("coordonnees_geo") or brut.get("geolocalisation")
            if isinstance(geo, dict):
                lat = geo.get("lat") or geo.get("latitude")
                lon = geo.get("lon") or geo.get("lng") or geo.get("longitude")
            elif isinstance(geo, str) and "," in geo:
                parts = geo.split(",")
                lat, lon = parts[0].strip(), parts[1].strip()

        return lat, lon

    def nettoyer_enregistrement(self, brut: dict, source: str) -> dict:
        """Nettoie un enregistrement brut et produit un document normalisé."""
        # Nom : variantes selon les sources
        nom = self.nettoyer_texte(
            self._get(brut, "nomoffre", "nom", "Nom", "nom_commercial",
                      "NOM COMMERCIAL", "name", "raison_sociale", "nom_etablissement")
        )

        # Commune : variantes selon les sources
        commune = self.nettoyer_texte(
            self._get(brut, "commune", "Commune", "COMMUNE", "ville", "nom_commune",
                      "libelle_commune", "city")
        )

        # Code postal : variantes selon les sources
        code_postal = self.nettoyer_texte(
            self._get(brut, "codepostal", "CodePostal", "cp", "code_postal",
                      "CODE POSTAL", "code_postal_normalise", "zipcode", "postal_code")
        )

        lat, lon = self._extraire_coords_geo(brut)
        coords = self.nettoyer_coordonnees(lat, lon)

        # Construction de l'adresse complète
        parties_adresse = [
            self._get(brut, "adresse1", "adresse", "adresse_1", "numero_voie"),
            brut.get("adresse1suite"),
            brut.get("adresse2"), brut.get("adresse3"),
            self._get(brut, "complement_adresse", "lieu_dit"),
        ]
        adresse = ", ".join(filter(None, [self.nettoyer_texte(p) for p in parties_adresse])) or None

        # Adresse : fallback champ unique
        if not adresse:
            adresse = self.nettoyer_texte(self._get(brut, "ADRESSE"))

        # Type d'hébergement : variantes selon les sources
        type_hebergement = self.nettoyer_type(
            self._get(brut, "type", "Type", "typologie", "TYPOLOGIE ÉTABLISSEMENT",
                      "categorie_classement", "type_hebergement", "tourism") or ""
        )

        # Capacité
        capacite_personnes = self.nettoyer_capacite(
            self._get(brut, "capacitenbpersonnes", "capacite", "nombrepersonnes",
                      "nombre_personnes", "nb_personnes", "capacity",
                      "CAPACITÉ D'ACCUEIL (PERSONNES)")
        )
        capacite_chambres = self.nettoyer_capacite(
            self._get(brut, "capacitenbchambres", "nb_chambres", "nombre_chambres",
                      "nombre_de_chambres", "rooms", "NOMBRE DE CHAMBRES")
        )

        # Classement étoiles
        classement = self.nettoyer_texte(
            self._get(brut, "classement", "CLASSEMENT", "categorie", "CATÉGORIE",
                      "nombre_etoiles", "classement_categorie", "stars", "rating")
        )

        # Contact
        telephone = self.nettoyer_telephone(
            self._get(brut, "commtel", "telephone", "tel", "phone", "numero_telephone")
        )
        email = self.nettoyer_texte(
            self._get(brut, "commmail", "email", "mail", "courriel", "adresse_email")
        )
        site_web = self.nettoyer_texte(
            self._get(brut, "commweb", "site_web", "siteweb", "url", "website",
                      "site_internet", "SITE INTERNET")
        )

        # Tarifs
        tarif_min = self.nettoyer_capacite(
            self._get(brut, "tarif1min", "tarifmin", "tarif_min", "prix_min")
        )
        tarif_max = self.nettoyer_capacite(
            self._get(brut, "tarif1max", "tarifmax", "tarif_max", "prix_max")
        )

        # Fallback : déduire le type depuis le nom de la source si non classé
        if type_hebergement == "Non classé":
            source_types = {
                "hotels_ile_de_france": "Hôtel",
                "campings_pays_de_la_loire": "Camping",
            }
            type_hebergement = source_types.get(source, type_hebergement)

        document = {
            "nom": nom,
            "type_hebergement": type_hebergement,
            "adresse": adresse,
            "code_postal": code_postal,
            "commune": commune,
            "code_insee": self.nettoyer_texte(
                self._get(brut, "codeinseecommune", "code_insee", "code_commune_insee", "insee")
            ),
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
        document["image_url"] = self.generer_image_url(type_hebergement, document["_id_unique"])
        document["disponibilites"] = self.generer_disponibilites(document["_id_unique"])
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
