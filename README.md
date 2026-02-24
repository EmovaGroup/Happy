📊 Happy — EMOVA Group Analytics Dashboard
🚀 Présentation

Happy est un dashboard analytique interne développé pour EMOVA Group permettant :

l’analyse des performances commerciales magasins

le suivi des ventes et marges

la comparaison hebdomadaire / journalière

la centralisation et l’archivage des rapports PDF magasins

L’application est construite avec Streamlit et connectée à Supabase (PostgreSQL + Storage).

🧱 Architecture du projet
Happy/
│
├── app.py                    # Point d’entrée Streamlit
│
├── pages/
│   ├── page_1.py             # Dashboard Matrix (Ventes & Marge)
│   └── page_2_upload_pdf.py  # Dépôt des rapports PDF
│
├── src/
│   ├── auth.py               # Authentification Supabase
│   ├── supabase_client.py    # Connexion Supabase
│   ├── ui.py                 # Header + navigation + CSS
│   └── db.py                 # Helpers base de données
│
├── assets/
│   └── logo_emova_group.png
│
├── .streamlit/
│   ├── config.toml           # Config Streamlit
│   └── secrets.toml ❌ (non versionné)
│
├── requirements.txt
└── README.md
🔐 Authentification

Connexion sécurisée via Supabase Auth :

Email / mot de passe

Session utilisateur Streamlit

Accès dashboard restreint

📊 Fonctionnalités principales
✅ Dashboard Matrix — Ventes & Marge

KPIs principaux :

💰 CA TTC

📊 CA HT

🧾 Quantités vendues

🛒 Prix moyen

🏦 Marge HT

🔥 Marge %

Analyses disponibles :

comparaison multi-magasins

évolution Jour / Semaine / Mois

top articles

répartition familles produits

synthèses hebdomadaires dynamiques

📅 Synthèses hebdomadaires

Tableaux intelligents :

✅ jours figés à gauche
✅ moyenne figée à droite
✅ couleurs dynamiques performance
✅ export CSV
✅ comparaison multi-semaines

📈 Graphiques automatiques

Visualisations :

Articles vendus

CA TTC

Prix moyen

Comparaison :

3 dernières semaines + Moyenne
📂 Upload & Archivage PDF

Deuxième page dédiée au dépôt des rapports magasins.

Upload structuré automatiquement :
MAGASIN_CODE/
└── magasin_CODE_YYMMDD.pdf
Exemple réel :
magasin_ANGLET_0047/
└── anglet_0047_260219.pdf

✔ Sélection magasin via liste
✔ Nom PDF généré automatiquement
✔ Upload vers Supabase Storage

☁️ Stack technique
Frontend

Streamlit

Altair

HTML / CSS custom

Backend

Supabase

PostgreSQL

PostgREST API

Storage

Supabase Storage (bucket pdfs)

Python

pandas

python-dotenv

supabase-py

⚙️ Installation locale
1️⃣ Clone du projet
git clone https://github.com/EmovaGroup/Happy.git
cd Happy
2️⃣ Environnement virtuel
python -m venv .venv

Activation :

Windows

.venv\Scripts\activate

Mac / Linux

source .venv/bin/activate
3️⃣ Installer dépendances
pip install -r requirements.txt
4️⃣ Configuration Supabase

Créer :

.streamlit/secrets.toml

⚠️ Ne jamais push ce fichier

SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_ANON_KEY="xxxxx"
5️⃣ Lancer l’application
streamlit run app.py
🔒 Sécurité

Fichiers exclus du repo :

.streamlit/secrets.toml
.env
.venv/

Gestion via .gitignore.

📦 Déploiement

Compatible avec :

Streamlit Cloud

VM interne

Docker

Infrastructure EMOVA

👨‍💻 Auteur

Salah Ouni
Data Engineer & AI — EMOVA Group

🏢 EMOVA Group

Projet interne destiné à l’analyse opérationnelle de l'enseignes :

Happy

✅ Dashboard production-ready
✅ Architecture modulaire
✅ Data-driven retail analytics
