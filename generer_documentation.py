#!/usr/bin/env python3
"""
Génère le PDF de documentation du projet.
Explique l'architecture, la logique et le fonctionnement de chaque composant.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fpdf import FPDF

OUTPUT_PATH = Path(__file__).resolve().parent / "docs" / "Documentation_Projet.pdf"


class DocumentationPDF(FPDF):
    """PDF de documentation avec mise en page personnalisée."""

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Projet Data Engineering - Hebergements Touristiques", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def titre_section(self, texte):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(15, 52, 96)
        self.ln(5)
        self.cell(0, 12, texte, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(15, 52, 96)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def sous_titre(self, texte):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(26, 26, 46)
        self.ln(3)
        self.cell(0, 10, texte, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def paragraphe(self, texte):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(10)
        self.multi_cell(0, 5.5, texte)
        self.ln(3)

    def code_block(self, texte):
        self.set_font("Courier", "", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(30, 30, 30)
        self.set_x(10)
        self.multi_cell(0, 5, texte, fill=True)
        self.ln(3)

    def puce(self, texte):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(10)
        self.multi_cell(0, 5.5, f"  -  {texte}")


def generer():
    pdf = DocumentationPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # === PAGE DE TITRE ===
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 15, "Plateforme d'Analyse des", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 15, "Hebergements Touristiques", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Projet Final - Data Engineering & Scraping", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 8, "Donnees ouvertes issues de data.gouv.fr", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, "Technologies : Python, MongoDB, MariaDB, Flask, Docker", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Sources : data.gouv.fr / Pays de la Loire / Saint-Malo", align="C", new_x="LMARGIN", new_y="NEXT")

    # === 1. INTRODUCTION ===
    pdf.add_page()
    pdf.titre_section("1. Introduction et Contexte")
    pdf.paragraphe(
        "Ce projet consiste a developper une plateforme d'analyse des hebergements touristiques "
        "en France, en exploitant exclusivement des donnees ouvertes (Open Data) issues de data.gouv.fr. "
        "L'objectif est de creer un pipeline ETL complet : collecte, nettoyage, stockage multi-support "
        "(MongoDB, MariaDB, fichiers), exposition via une API REST et consultation via une interface web."
    )
    pdf.paragraphe(
        "Le projet couvre l'ensemble de la chaine de valeur Data Engineering : "
        "de la source de donnees brutes jusqu'a la visualisation par l'utilisateur final."
    )

    pdf.sous_titre("Sources de donnees")
    pdf.puce("Hebergements collectifs touristiques - Pays de la Loire (325 enregistrements)")
    pdf.puce("Hebergements locatifs touristiques - Pays de la Loire (4075 enregistrements)")
    pdf.puce("Hebergements touristiques - Saint-Malo (6 enregistrements, donnees agregees)")
    pdf.ln(3)
    pdf.paragraphe(
        "Au total, plus de 4400 enregistrements bruts sont collectes, "
        "produisant environ 4380 enregistrements propres apres nettoyage et deduplication."
    )

    # === 2. ARCHITECTURE ===
    pdf.add_page()
    pdf.titre_section("2. Architecture du Projet")

    pdf.sous_titre("Structure des fichiers")
    pdf.code_block(
        "plateforme_hebergements/\n"
        "|-- pipeline.py              # Pipeline ETL principal\n"
        "|-- serveur.py               # Serveur web (API + interface)\n"
        "|-- requirements.txt         # Dependances Python\n"
        "|-- src/\n"
        "|   |-- config.py            # Configuration centralisee\n"
        "|   |-- collecte/            # Module de collecte (scraping)\n"
        "|   |   |-- collecteur.py\n"
        "|   |-- nettoyage/           # Module de nettoyage\n"
        "|   |   |-- nettoyeur.py\n"
        "|   |-- mongodb/             # Gestion MongoDB\n"
        "|   |   |-- gestionnaire_mongo.py\n"
        "|   |-- warehouse/           # Data Warehouse MariaDB\n"
        "|   |   |-- gestionnaire_warehouse.py\n"
        "|   |-- datalake/            # Export Data Lake\n"
        "|   |   |-- gestionnaire_datalake.py\n"
        "|   |-- api/                 # API REST Flask\n"
        "|   |   |-- api.py\n"
        "|   |-- web/templates/       # Interface web\n"
        "|       |-- index.html\n"
        "|-- tests/                   # Tests unitaires + integration\n"
        "|-- data_lake/               # Fichiers JSON/CSV\n"
        "|   |-- raw/  clean/  analytics/\n"
        "|-- docs/                    # Documentation\n"
        "|-- Dockerfile               # Image Docker de l'application\n"
        "|-- docker-compose.yml       # Orchestration multi-conteneurs\n"
        "|-- .dockerignore            # Fichiers exclus du build\n"
        "|-- generer_dashboard_powerbi.py  # Export Excel pour Power BI"
    )

    pdf.sous_titre("Flux de donnees (Pipeline ETL)")
    pdf.paragraphe(
        "Le pipeline s'execute en 5 etapes sequentielles :"
    )
    pdf.puce("Etape 1 - Collecte : telechargement JSON/CSV depuis data.gouv.fr via l'API ou liens directs")
    pdf.puce("Etape 2 - Nettoyage : normalisation des champs, deduplication, conversion des types")
    pdf.puce("Etape 3 - MongoDB : insertion des donnees brutes (collection raw) et nettoyees (collection clean)")
    pdf.puce("Etape 4 - Data Warehouse : chargement dans MariaDB (modele en etoile)")
    pdf.puce("Etape 5 - Data Lake : export en fichiers JSON et CSV organises par zones (raw/clean/analytics)")

    # === 3. COLLECTE ===
    pdf.add_page()
    pdf.titre_section("3. Collecte des Donnees")
    pdf.paragraphe(
        "Le module collecteur.py utilise la bibliotheque requests pour telecharger les donnees "
        "depuis les API Open Data. La classe CollecteurDonnees gere la session HTTP, la detection "
        "d'encodage (UTF-8, Latin-1, CP1252) et la detection automatique du delimiteur CSV."
    )
    pdf.sous_titre("Logique de collecte")
    pdf.puce("Preference JSON si disponible (parsing natif, pas de probleme de delimiteur)")
    pdf.puce("Fallback sur CSV avec detection automatique du delimiteur (; , tabulation)")
    pdf.puce("Gestion des erreurs par source : une source en echec n'arrete pas les autres")
    pdf.puce("Toutes les sources sont configurees dans config.py (URLs, noms, types)")

    pdf.sous_titre("Donnees collectees")
    pdf.paragraphe(
        "Les donnees de Pays de la Loire sont riches : nom, type, adresse, code postal, commune, "
        "coordonnees GPS, telephone, email, site web, capacite, tarifs, classement. "
        "Les donnees de Saint-Malo sont des statistiques agregees par annee (nombre d'hotels par categorie)."
    )

    # === 4. NETTOYAGE ===
    pdf.add_page()
    pdf.titre_section("4. Nettoyage et Normalisation")
    pdf.paragraphe(
        "Le module nettoyeur.py transforme les donnees brutes heterogenes en un schema uniforme. "
        "Chaque champ est traite par une methode specialisee de la classe NettoyeurDonnees."
    )

    pdf.sous_titre("Operations de nettoyage")
    pdf.puce("Texte : suppression des espaces multiples, trim, gestion des valeurs nulles")
    pdf.puce("Telephone : normalisation au format international (+33...)")
    pdf.puce("Coordonnees GPS : validation des bornes France metropolitaine (lat 41-51.5, lon -5.5-10)")
    pdf.puce("Type d'hebergement : mapping vers des categories normalisees (Hotel, Camping, Meuble...)")
    pdf.puce("Capacite : conversion en entier, rejet des valeurs <= 0")
    pdf.puce("Adresse : concatenation des champs adresse1/2/3")

    pdf.sous_titre("Deduplication")
    pdf.paragraphe(
        "Un identifiant unique est genere par hachage MD5 de la combinaison nom + commune + code_postal. "
        "Les doublons sont automatiquement elimines. Sur 4406 enregistrements bruts, "
        "16 doublons sont supprimes et 6 enregistrements sans nom sont ignores, "
        "produisant 4384 enregistrements propres."
    )

    # === 5. MONGODB ===
    pdf.add_page()
    pdf.titre_section("5. Stockage MongoDB")
    pdf.paragraphe(
        "MongoDB est utilise comme base documentaire principale avec deux collections :"
    )
    pdf.puce("raw_hebergements : donnees brutes telles que collectees (4406 documents)")
    pdf.puce("clean_hebergements : donnees nettoyees et normalisees (4376 documents uniques)")

    pdf.sous_titre("Indexation")
    pdf.puce("Index sur commune, type_hebergement, departement, code_postal pour les recherches")
    pdf.puce("Index unique sur _id_unique pour la deduplication")
    pdf.puce("Index geospatial (2dsphere) sur le champ localisation pour les requetes geographiques")

    pdf.sous_titre("Schema du document clean")
    pdf.code_block(
        "{\n"
        '  "nom": "Hotel Ocean",\n'
        '  "type_hebergement": "Hotel",\n'
        '  "adresse": "10 rue du Port",\n'
        '  "code_postal": "44000",\n'
        '  "commune": "NANTES",\n'
        '  "departement": "44",\n'
        '  "latitude": 47.2184,\n'
        '  "longitude": -1.5536,\n'
        '  "capacite_personnes": 50,\n'
        '  "telephone": "+33240112233",\n'
        '  "source": "hebergements_collectifs",\n'
        '  "localisation": { "type": "Point", "coordinates": [-1.5536, 47.2184] }\n'
        "}"
    )

    # === 6. DATA WAREHOUSE ===
    pdf.add_page()
    pdf.titre_section("6. Data Warehouse (MariaDB)")
    pdf.paragraphe(
        "Le Data Warehouse utilise un modele en etoile simplifie pour permettre l'exploitation BI. "
        "Il est compose de 3 tables de dimension et 1 table de faits."
    )

    pdf.sous_titre("Modele en etoile")
    pdf.puce("dim_type_hebergement : les categories d'hebergement (Hotel, Camping, Meuble...)")
    pdf.puce("dim_localisation : commune, code postal, departement, coordonnees GPS")
    pdf.puce("dim_source : origine des donnees (collectifs, locatifs, saint_malo)")
    pdf.puce("fait_hebergement : table centrale avec cles etrangeres vers les dimensions, "
             "plus les mesures (capacite, tarifs, classement, contact)")

    pdf.sous_titre("Vues analytiques")
    pdf.puce("vue_resume_departement : nombre d'hebergements, capacite moyenne, tarifs par departement et type")
    pdf.puce("vue_resume_commune : nombre d'hebergements, types disponibles, capacite totale par commune")

    pdf.sous_titre("Vues Power BI")
    pdf.puce("vue_powerbi_hebergements : table plate denormalisee avec toutes les informations "
             "(type, localisation, tarifs, nombre d'etoiles calcule, nom de departement)")
    pdf.puce("vue_powerbi_kpis : indicateurs globaux (totaux, moyennes, taux de completude email/site web)")
    pdf.puce("vue_powerbi_top_communes : top 20 communes par nombre d'hebergements avec diversite des types")
    pdf.paragraphe(
        "Ces vues sont directement exploitables par un outil BI (Metabase, Grafana, Power BI) "
        "sans transformation supplementaire. La vue vue_powerbi_hebergements est optimisee "
        "pour un import direct dans Power BI via le connecteur MySQL."
    )

    # === 7. DATA LAKE ===
    pdf.add_page()
    pdf.titre_section("7. Data Lake (Fichiers JSON/CSV)")
    pdf.paragraphe(
        "Le Data Lake est organise en 3 zones selon le principe medaillon :"
    )
    pdf.puce("raw/ : donnees brutes par source et par date (JSON + CSV)")
    pdf.puce("clean/ : donnees nettoyees et unifiees (JSON + CSV)")
    pdf.puce("analytics/ : agregations pre-calculees (stats par type, par departement)")

    pdf.paragraphe(
        "Chaque export est horodate (ex: hebergements_clean_20260412.json) pour permettre "
        "le suivi historique. Les fichiers CSV utilisent le delimiteur point-virgule "
        "pour la compatibilite avec Excel en environnement francophone."
    )

    # === 8. API REST ===
    pdf.add_page()
    pdf.titre_section("8. API REST")
    pdf.paragraphe(
        "L'API est construite avec Flask et expose les endpoints suivants :"
    )

    pdf.sous_titre("Endpoints disponibles")
    pdf.code_block(
        "GET /api/hebergements        Lister/filtrer les hebergements\n"
        "    ?type=Hotel              Filtrer par type\n"
        "    ?commune=NANTES          Filtrer par commune\n"
        "    ?departement=44          Filtrer par departement\n"
        "    ?q=ocean                 Recherche textuelle\n"
        "    ?limit=50&offset=0       Pagination\n"
        "\n"
        "GET /api/hebergements/<id>   Detail d'un hebergement\n"
        "GET /api/types               Liste des types\n"
        "GET /api/communes            Liste des communes\n"
        "GET /api/departements        Liste des departements\n"
        "GET /api/statistiques        Statistiques globales\n"
        "GET /api/health              Etat de sante de l'API"
    )

    pdf.paragraphe(
        "L'API retourne du JSON avec pagination. La recherche textuelle utilise "
        "les expressions regulieres MongoDB ($regex) pour une recherche flexible "
        "sur le nom, la commune et le type d'hebergement."
    )

    # === 9. INTERFACE WEB ===
    pdf.add_page()
    pdf.titre_section("9. Interface Web")
    pdf.paragraphe(
        "Le mini site web est une Single Page Application (SPA) en HTML/CSS/JavaScript pur, "
        "sans framework externe. Il communique avec l'API REST via fetch()."
    )

    pdf.sous_titre("Fonctionnalites")
    pdf.puce("Barre de statistiques en temps reel (total, types, communes, departements)")
    pdf.puce("Filtres : recherche textuelle, filtre par type, filtre par departement")
    pdf.puce("Affichage en grille de cartes responsives")
    pdf.puce("Pagination avec navigation precedent/suivant")
    pdf.puce("Design moderne avec effets de survol et transitions")

    # === 10. TESTS ===
    pdf.add_page()
    pdf.titre_section("10. Tests")
    pdf.paragraphe(
        "Le projet comporte 39 tests repartis en tests unitaires et tests d'integration :"
    )

    pdf.sous_titre("Tests unitaires (test_nettoyeur.py)")
    pdf.puce("TestNettoyerTexte : normalisation des chaines (3 tests)")
    pdf.puce("TestNettoyerTelephone : format telephone francais (4 tests)")
    pdf.puce("TestNettoyerCoordonnees : validation GPS (3 tests)")
    pdf.puce("TestNettoyerType : mapping des types (5 tests)")
    pdf.puce("TestNettoyerCapacite : conversion numerique (4 tests)")
    pdf.puce("TestNettoyerEnregistrement : transformation complete (2 tests)")
    pdf.puce("TestNettoyerLot : deduplication et filtrage (2 tests)")

    pdf.sous_titre("Tests unitaires (test_collecteur.py)")
    pdf.puce("Verification source inconnue, URL invalide CSV, URL invalide JSON (3 tests)")

    pdf.sous_titre("Tests d'integration (test_integration.py)")
    pdf.puce("TestMongoDB : connexion, recherche, statistiques, departements (4 tests)")
    pdf.puce("TestAPI : health, listing, filtrage, recherche, types, departements, "
             "communes, statistiques, 404 (9 tests)")

    # === 11. PRINCIPES SOLID ===
    pdf.add_page()
    pdf.titre_section("11. Principes SOLID et Bonnes Pratiques")

    pdf.puce("S - Single Responsibility : chaque module a une responsabilite unique "
             "(collecte, nettoyage, stockage, API, export)")
    pdf.puce("O - Open/Closed : les sources de donnees sont configurables dans config.py "
             "sans modifier le code de collecte")
    pdf.puce("L - Liskov Substitution : les gestionnaires (Mongo, Warehouse, Datalake) "
             "suivent des interfaces coherentes (connecter, charger, fermer)")
    pdf.puce("I - Interface Segregation : les modules exposent des interfaces specifiques "
             "(ex: rechercher vs exporter_tout)")
    pdf.puce("D - Dependency Inversion : la configuration est injectee via config.py, "
             "les modules dependent d'abstractions et non d'implementations concretes")

    # === 12. POWER BI ===
    pdf.add_page()
    pdf.titre_section("12. Integration Power BI")
    pdf.paragraphe(
        "Le Data Warehouse est concu pour etre exploite avec Power BI. "
        "Deux methodes de connexion sont disponibles."
    )

    pdf.sous_titre("Methode 1 : Import Excel (recommande pour debuter)")
    pdf.paragraphe(
        "Le script generer_dashboard_powerbi.py genere un fichier Excel multi-onglets "
        "pret pour import dans Power BI. Ce fichier contient les donnees pre-formatees "
        "avec graphiques, KPIs et mise en forme professionnelle."
    )
    pdf.code_block(
        "python generer_dashboard_powerbi.py\n"
        "# Genere docs/Dashboard_PowerBI_YYYYMMDD.xlsx"
    )
    pdf.paragraphe(
        "Le fichier Excel contient 5 onglets :"
    )
    pdf.puce("Dashboard : KPIs (total hebergements, types, departements, communes), "
             "graphique a barres par type, camembert par departement")
    pdf.puce("Donnees detaillees : 4379 lignes avec filtres automatiques, "
             "pret pour tableaux croises dynamiques")
    pdf.puce("Analyse par type : 11 types avec pourcentage et capacite moyenne")
    pdf.puce("Analyse par departement : 6 departements avec pourcentage du total")
    pdf.puce("Carte geographique : coordonnees latitude/longitude de chaque hebergement, "
             "permet de creer une carte interactive dans Power BI (visualisation Map)")

    pdf.paragraphe(
        "Import dans Power BI : Obtenir des donnees > Excel > selectionner le fichier > "
        "cocher tous les onglets > Charger."
    )

    pdf.sous_titre("Methode 2 : Connexion directe MariaDB")
    pdf.paragraphe(
        "Avec Docker lance, MariaDB est accessible sur le port 3306 et accepte "
        "les connexions distantes (bind-address=0.0.0.0). Power BI peut s'y connecter "
        "via le connecteur MySQL (compatible MariaDB)."
    )
    pdf.code_block(
        "Serveur : localhost (ou IP de la machine)\n"
        "Port : 3306\n"
        "Base de donnees : dw_hebergements\n"
        "Utilisateur : etl_user\n"
        "Mot de passe : etl_pass\n"
        "Vue principale : vue_powerbi_hebergements"
    )
    pdf.paragraphe(
        "La vue vue_powerbi_hebergements fournit une table plate denormalisee avec "
        "toutes les informations necessaires : nom, type, localisation, tarifs, capacite, "
        "nombre d'etoiles calcule et nom complet du departement. "
        "Power BI detecte automatiquement les relations si les tables de dimension sont importees."
    )

    pdf.sous_titre("Visualisations recommandees")
    pdf.puce("Carte geographique : utiliser les colonnes Latitude et Longitude pour "
             "afficher les hebergements sur une carte interactive")
    pdf.puce("Graphique a barres : repartition par type d'hebergement")
    pdf.puce("Camembert : repartition par departement")
    pdf.puce("Tableau croise : type x departement avec mesure capacite ou tarif moyen")
    pdf.puce("KPIs : total hebergements, capacite totale, tarif moyen, taux de classement")
    pdf.puce("Segments (slicers) : filtres par type, departement, commune, classement")

    # === 13. DOCKERISATION ===
    pdf.add_page()
    pdf.titre_section("13. Dockerisation")
    pdf.paragraphe(
        "Le projet est entierement conteneurise avec Docker et Docker Compose. "
        "Cela permet de deployer l'ensemble de la plateforme (bases de donnees, pipeline ETL, "
        "serveur web) en une seule commande, sans installer de dependances sur la machine hote."
    )

    pdf.sous_titre("Architecture des conteneurs")
    pdf.paragraphe(
        "Le fichier docker-compose.yml definit 4 services :"
    )
    pdf.puce("mongodb : base NoSQL MongoDB 7, port 27017, volume persistant mongo_data")
    pdf.puce("mariadb : Data Warehouse MariaDB 11, port 3306, volume persistant mariadb_data, "
             "avec healthcheck pour garantir que la base est prete avant le chargement")
    pdf.puce("pipeline : conteneur ephemere qui execute le pipeline ETL complet (python pipeline.py), "
             "demarre uniquement apres que MongoDB et MariaDB sont operationnels")
    pdf.puce("web : serveur Flask exposant l'API REST et l'interface web sur le port 5050")

    pdf.sous_titre("Dockerfile")
    pdf.paragraphe(
        "L'image est basee sur python:3.11-slim. Les dependances systeme pour le connecteur "
        "MariaDB (libmariadb-dev, gcc) sont installees, puis les dependances Python via pip. "
        "Le code source est copie dans /app et le serveur est lance par defaut."
    )
    pdf.code_block(
        "FROM python:3.11-slim\n"
        "RUN apt-get update && apt-get install -y libmariadb-dev gcc\n"
        "WORKDIR /app\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY . .\n"
        "EXPOSE 5050\n"
        'CMD ["python", "serveur.py"]'
    )

    pdf.sous_titre("Configuration reseau")
    pdf.paragraphe(
        "En mode Docker, la connexion a MariaDB passe par TCP (host + port) au lieu du socket Unix "
        "utilise en mode local. La detection est automatique dans config.py : si la variable "
        "d'environnement MARIADB_HOST est definie, la connexion TCP est utilisee. "
        "Sinon, le socket Unix est utilise pour le developpement local."
    )

    pdf.sous_titre("Volumes persistants")
    pdf.puce("mongo_data : donnees MongoDB persistees entre les redemarrages")
    pdf.puce("mariadb_data : donnees MariaDB persistees entre les redemarrages")
    pdf.puce("datalake : fichiers JSON/CSV du Data Lake partages entre les conteneurs pipeline et web")

    pdf.sous_titre("Commandes Docker")
    pdf.code_block(
        "# Lancer toute la plateforme\n"
        "docker compose up --build\n"
        "\n"
        "# Lancer seulement les bases de donnees\n"
        "docker compose up -d mongodb mariadb\n"
        "\n"
        "# Executer le pipeline ETL\n"
        "docker compose run pipeline\n"
        "\n"
        "# Demarrer le serveur web\n"
        "docker compose up web\n"
        "\n"
        "# Arreter et supprimer les conteneurs\n"
        "docker compose down\n"
        "\n"
        "# Supprimer aussi les volumes (reinitialiser les donnees)\n"
        "docker compose down -v"
    )

    # === 14. MISE EN ROUTE ===
    pdf.add_page()
    pdf.titre_section("14. Guide d'Installation et d'Utilisation")

    pdf.sous_titre("Option A : Avec Docker (recommande)")
    pdf.puce("Docker et Docker Compose installes sur la machine")
    pdf.code_block(
        "# Lancer toute la plateforme en une commande\n"
        "docker compose up --build\n"
        "\n"
        "# Ouvrir http://localhost:5050"
    )

    pdf.sous_titre("Option B : Installation locale")
    pdf.puce("Python 3.10+")
    pdf.puce("MongoDB Community (brew install mongodb-community)")
    pdf.puce("MariaDB (brew install mariadb)")

    pdf.code_block(
        "# Installer les dependances\n"
        "pip install -r requirements.txt\n"
        "\n"
        "# Demarrer MongoDB et MariaDB\n"
        "brew services start mongodb-community\n"
        "brew services start mariadb\n"
        "\n"
        "# 1. Executer le pipeline ETL complet\n"
        "python pipeline.py\n"
        "\n"
        "# 2. Lancer le serveur (API + Web)\n"
        "python serveur.py\n"
        "# Ouvrir http://localhost:5050\n"
        "\n"
        "# 3. Lancer les tests\n"
        "python -m pytest tests/ -v"
    )

    # === SAVE ===
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT_PATH))
    print(f"PDF genere : {OUTPUT_PATH}")


if __name__ == "__main__":
    generer()
