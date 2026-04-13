#!/usr/bin/env python3
"""
Serveur web — Lance l'API REST et sert l'interface de consultation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import send_from_directory
from src.api.api import app

TEMPLATES_DIR = Path(__file__).resolve().parent / "src" / "web" / "templates"


@app.route("/")
def page_accueil():
    """Sert la page d'accueil du mini site web."""
    return send_from_directory(str(TEMPLATES_DIR), "index.html")


if __name__ == "__main__":
    print("\n🌐 Serveur démarré : http://localhost:5050")
    print("   API : http://localhost:5050/api/hebergements")
    print("   Web : http://localhost:5050/\n")
    app.run(host="0.0.0.0", port=5050, debug=True)
