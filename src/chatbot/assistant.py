"""
Chatbot IA pour la plateforme d'hébergements touristiques.
Utilise l'API Claude (Anthropic) pour répondre aux visiteurs
en s'appuyant sur les données MongoDB.
"""

import os
import logging
from anthropic import Anthropic
from src.mongodb.gestionnaire_mongo import GestionnaireMongo

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """\
Tu es l'assistant virtuel d'une plateforme d'hébergements touristiques en France.
Tu aides les visiteurs à trouver un hébergement adapté à leurs besoins.

Tu as accès à une base de données d'hébergements. Voici les données disponibles :

{contexte_donnees}

Règles :
- Réponds toujours en français, de manière amicale et concise.
- Recommande des hébergements concrets avec leur nom, commune, type et capacité.
- Si le visiteur cherche un lieu précis, filtre par commune ou département.
- Si tu ne trouves pas d'hébergement correspondant, dis-le honnêtement.
- Ne donne jamais de prix inventés — dis que le visiteur doit contacter l'hébergement.
- Propose des liens vers la fiche si possible (format: /api/hebergements/<id>).
"""


class AssistantChatbot:
    """Chatbot conversationnel basé sur Claude."""

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY non définie")
        self._client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self._mongo = GestionnaireMongo()
        self._contexte = self._charger_contexte()

    def _charger_contexte(self) -> str:
        """Charge un résumé des données pour le prompt système."""
        stats = self._mongo.obtenir_statistiques()
        types = self._mongo.obtenir_types()
        departements = self._mongo.obtenir_departements()

        lignes = [
            f"- Total hébergements : {stats['total']}",
            f"- Types disponibles : {', '.join(types)}",
            f"- Départements couverts : {', '.join(departements[:20])}",
            "- Données par type :"
        ]
        for t in stats.get("par_type", []):
            lignes.append(f"  • {t['_id']} : {t['count']} hébergements")

        return "\n".join(lignes)

    def _rechercher_hebergements(self, message: str) -> list[dict]:
        """Recherche des hébergements pertinents selon le message du visiteur."""
        filtres = {"$or": [
            {"nom": {"$regex": message, "$options": "i"}},
            {"commune": {"$regex": message, "$options": "i"}},
            {"departement": {"$regex": message, "$options": "i"}},
            {"type_hebergement": {"$regex": message, "$options": "i"}},
        ]}
        resultats = self._mongo.rechercher(filtres, {"_id": 0, "localisation": 0}, limite=10)
        return resultats

    def repondre(self, message: str, historique: list[dict] = None) -> str:
        """
        Génère une réponse à partir du message du visiteur.
        historique : liste de {"role": "user"/"assistant", "content": "..."}
        """
        # Chercher des hébergements pertinents dans la base
        resultats = self._rechercher_hebergements(message)

        contexte_recherche = ""
        if resultats:
            contexte_recherche = "\n\nRésultats de recherche pour cette question :\n"
            for r in resultats:
                contexte_recherche += (
                    f"- {r.get('nom', 'N/A')} | {r.get('type_hebergement', '')} | "
                    f"{r.get('commune', '')} ({r.get('departement', '')}) | "
                    f"Capacité: {r.get('capacite_personnes', 'N/A')} pers. | "
                    f"ID: {r.get('_id_unique', '')}\n"
                )

        system = SYSTEM_PROMPT.format(contexte_donnees=self._contexte) + contexte_recherche

        # Construire les messages
        messages = []
        if historique:
            messages.extend(historique[-10:])  # Garder les 10 derniers échanges
        messages.append({"role": "user", "content": message})

        response = self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system,
            messages=messages,
        )

        return response.content[0].text
