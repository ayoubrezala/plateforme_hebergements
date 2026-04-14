"""
API REST pour la consultation des hébergements touristiques.
Endpoints de recherche, filtrage et statistiques.
"""

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from bson import json_util
import json

from datetime import datetime
from src.mongodb.gestionnaire_mongo import GestionnaireMongo
from src.config import API_HOST, API_PORT

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

mongo = GestionnaireMongo()

# --- Chatbot ---
_chatbot = None


def _get_chatbot():
    """Initialise le chatbot à la demande (lazy loading)."""
    global _chatbot
    if _chatbot is None:
        try:
            from src.chatbot.assistant import AssistantChatbot
            _chatbot = AssistantChatbot()
            logger.info("Chatbot initialisé avec succès")
        except Exception as e:
            logger.warning(f"Chatbot non disponible : {e}")
    return _chatbot


def _serialiser(obj):
    """Convertit les objets MongoDB en JSON sérialisable."""
    texte = json_util.dumps(obj)
    return json.loads(texte)


@app.route("/api/hebergements", methods=["GET"])
def lister_hebergements():
    """
    Liste les hébergements avec filtres optionnels.
    Paramètres : type, commune, departement, q (recherche), limit, offset
    """
    filtres = {}

    type_h = request.args.get("type")
    if type_h:
        filtres["type_hebergement"] = type_h

    commune = request.args.get("commune")
    if commune:
        filtres["commune"] = {"$regex": commune, "$options": "i"}

    departement = request.args.get("departement")
    if departement:
        filtres["departement"] = departement

    recherche = request.args.get("q")
    if recherche:
        filtres["$or"] = [
            {"nom": {"$regex": recherche, "$options": "i"}},
            {"commune": {"$regex": recherche, "$options": "i"}},
            {"type_hebergement": {"$regex": recherche, "$options": "i"}},
        ]

    limite = min(int(request.args.get("limit", 50)), 500)
    offset = int(request.args.get("offset", 0))

    projection = {"_id": 0, "localisation": 0}
    # Inclure image_url et disponibilites dans les résultats
    resultats = mongo.rechercher(filtres, projection, limite, offset)
    total = mongo.compter_documents()

    return jsonify({
        "total": total,
        "limit": limite,
        "offset": offset,
        "count": len(resultats),
        "data": _serialiser(resultats)
    })


@app.route("/api/hebergements/<id_unique>", methods=["GET"])
def obtenir_hebergement(id_unique):
    """Récupère un hébergement par son identifiant unique."""
    resultats = mongo.rechercher(
        {"_id_unique": id_unique},
        {"_id": 0, "localisation": 0}
    )
    if not resultats:
        return jsonify({"error": "Hébergement non trouvé"}), 404
    return jsonify(_serialiser(resultats[0]))


@app.route("/api/hebergements/<id_unique>/disponibilites", methods=["GET"])
def obtenir_disponibilites(id_unique):
    """Retourne les disponibilités d'un hébergement."""
    resultats = mongo.rechercher(
        {"_id_unique": id_unique},
        {"_id": 0, "disponibilites": 1, "nom": 1}
    )
    if not resultats:
        return jsonify({"error": "Hébergement non trouvé"}), 404
    return jsonify(_serialiser(resultats[0]))


@app.route("/api/reservations", methods=["POST"])
def creer_reservation():
    """Crée une nouvelle réservation."""
    data = request.get_json()
    champs_requis = ["id_hebergement", "nom_client", "prenom_client",
                     "email_client", "telephone_client", "date_arrivee",
                     "date_depart", "nb_personnes"]
    for champ in champs_requis:
        if not data.get(champ):
            return jsonify({"error": f"Champ requis manquant : {champ}"}), 400

    # Vérifier que l'hébergement existe
    hebergement = mongo.rechercher({"_id_unique": data["id_hebergement"]}, {"_id": 0})
    if not hebergement:
        return jsonify({"error": "Hébergement non trouvé"}), 404

    reservation = {
        "id_hebergement": data["id_hebergement"],
        "nom_hebergement": hebergement[0].get("nom"),
        "nom_client": data["nom_client"],
        "prenom_client": data["prenom_client"],
        "email_client": data["email_client"],
        "telephone_client": data["telephone_client"],
        "date_arrivee": data["date_arrivee"],
        "date_depart": data["date_depart"],
        "nb_personnes": int(data["nb_personnes"]),
        "message": data.get("message", ""),
        "statut": "en_attente",
        "date_creation": datetime.now().isoformat(),
    }

    result = mongo.inserer_reservation(reservation)
    return jsonify({"success": True, "message": "Réservation enregistrée", "id": str(result)}), 201


@app.route("/api/types", methods=["GET"])
def lister_types():
    """Retourne la liste des types d'hébergement disponibles."""
    types = mongo.obtenir_types()
    return jsonify({"types": sorted(types)})


@app.route("/api/communes", methods=["GET"])
def lister_communes():
    """Retourne la liste des communes."""
    dept = request.args.get("departement")
    if dept:
        docs = mongo.rechercher({"departement": dept}, {"commune": 1, "_id": 0})
        communes = sorted(set(d["commune"] for d in docs if d.get("commune")))
    else:
        communes = mongo.obtenir_communes()
    return jsonify({"communes": communes})


@app.route("/api/departements", methods=["GET"])
def lister_departements():
    """Retourne la liste des départements."""
    return jsonify({"departements": mongo.obtenir_departements()})


@app.route("/api/statistiques", methods=["GET"])
def obtenir_statistiques():
    """Retourne les statistiques globales des données."""
    stats = mongo.obtenir_statistiques()
    return jsonify(_serialiser(stats))


@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint du chatbot — reçoit un message et retourne la réponse IA."""
    data = request.get_json()
    message = data.get("message", "").strip()
    historique = data.get("historique", [])

    if not message:
        return jsonify({"error": "Message vide"}), 400

    bot = _get_chatbot()
    if bot is None:
        return jsonify({"error": "Chatbot non disponible (clé API manquante)"}), 503

    try:
        reponse = bot.repondre(message, historique)
        return jsonify({"reponse": reponse})
    except Exception as e:
        logger.error(f"Erreur chatbot : {e}")
        return jsonify({"error": "Erreur lors de la génération de la réponse"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Vérification de l'état de l'API."""
    return jsonify({"status": "ok", "documents": mongo.compter_documents()})


def lancer_api():
    """Lance le serveur API."""
    logger.info(f"Démarrage API sur {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=True)


if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    lancer_api()
