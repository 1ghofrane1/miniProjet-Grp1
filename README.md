# Stages API - Mini-projet Cloud Computing

**Équipe :** Ghofrane Bouallegue, Mohamed Aziz Braham, Dheker Kraiem, Malek Gabsi.

API REST FastAPI avec SQLite, documentation Swagger, Docker et configuration Render.
Le périmètre suit les quatre parties de l'énoncé. Un seul service métier suffit ici :
il n'est pas nécessaire d'ajouter Kubernetes ou plusieurs microservices pour satisfaire le sujet.

## Démarrer sous Windows (PowerShell)

Depuis ce dossier, avec Python 3.12 ou plus récent :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ouvrir [Swagger](http://localhost:8000/docs), puis utiliser **Try it out** et **Execute**.
La base est créée automatiquement dans `data/stages.db`. Elle est conservée entre les
redémarrages locaux. `DATABASE_PATH` permet de choisir un autre emplacement.

## Endpoints

| Méthode | Route | Résultat |
|---|---|---|
| GET | `/` | Informations et lien vers Swagger |
| GET | `/health` | Vérification API et accès SQLite, 200 |
| POST | `/stages` | Création, 201 et en-tête Location |
| GET | `/stages` | Liste, 200 ; pagination `offset=0&limit=100` |
| GET | `/stages/{id}` | Consultation, 200 ou 404 |
| PUT | `/stages/{id}` | Remplacement de tous les champs, 200 ou 404 |
| DELETE | `/stages/{id}` | Suppression, 204 sans corps ou 404 |

Exemple de corps JSON pour POST et PUT (données fictives) :

```json
{
  "nom_etudiant": "Etudiant Demo",
  "entreprise": "Cloud Demo",
  "intitule": "Développement API et déploiement Cloud",
  "date_debut": "2026-02-01",
  "date_fin": "2026-06-30"
}
```

L'identifiant est généré par SQLite. Les textes vides, champs inconnus, dates invalides
ou inversées donnent 422. La fin peut être le même jour que le début.
Une ressource absente donne `404 {"detail":"Stage introuvable"}`.

## Tests automatisés

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

Les tests utilisent une base temporaire indépendante : CRUD complet, absence,
validation, pagination, texte ressemblant à du SQL, réouverture de base et Swagger.
GitHub Actions exécute les tests et construit l'image à chaque push ou pull request.

## Docker

Démarrer Docker Desktop avec le moteur Linux, puis :

```powershell
docker build -t stages-api .
docker run --rm -p 8000:8000 --name stages-api -v stages-data:/app/data stages-api
```

Ou utiliser `docker compose up --build -d` et `docker compose logs -f`.
Swagger reste sur [localhost:8000/docs](http://localhost:8000/docs).
Le volume nommé conserve SQLite localement. Pour arrêter Compose : `docker compose down`.

## Déployer sur GitHub puis Render

Les comptes GitHub et Render doivent appartenir à un membre du groupe.

1. Créer un dépôt GitHub vide nommé `stages-api` et copier son URL HTTPS.
2. Dans ce dossier, exécuter les commandes ci-dessous en remplaçant l'URL :

```powershell
git init
git add .
git commit -m "Mini-projet API stages FastAPI SQLite Docker"
git branch -M main
git remote add origin https://github.com/VOTRE-COMPTE/stages-api.git
git push -u origin main
```

3. Dans [Render](https://dashboard.render.com/), choisir **New > Web Service**,
   connecter GitHub et sélectionner ce dépôt.
4. Choisir la branche `main`, le runtime **Docker**, le Dockerfile `./Dockerfile`
   et le plan **Free**. Ne pas définir de commande de démarrage personnalisée.
5. Choisir `/health` comme chemin de health check et lancer le déploiement.
   Le Dockerfile écoute sur `0.0.0.0` et utilise la variable `PORT` de Render.
6. Attendre l'état **Live**, copier l'URL `https://...onrender.com` effectivement fournie.
7. Tester `/health`, `/docs`, puis tout le scénario CRUD avec cette URL.
8. Ajouter le lien GitHub et l'URL réelle dans `docs/LIVRAISON.md`.

Alternative : `render.yaml` permet un déploiement **New > Blueprint** à partir du dépôt.

Le disque d'un service gratuit Render est éphémère : SQLite peut être perdue au
redémarrage ou au redéploiement. Le service gratuit se met en veille après une période
d'inactivité. C'est une limite acceptée par le sujet. Aucun disque payant n'est requis.
Voir la [documentation officielle Render](https://render.com/docs/free) et
[Docker sur Render](https://render.com/docs/docker).

## Démonstration et remise

Suivre `docs/DEMONSTRATION.md`, compléter `docs/LIVRAISON.md` et conserver les captures
réelles. Le rapport technique est dans `docs/RAPPORT.md` et la répartition proposée
dans `docs/EQUIPE.md`. Le fichier `docs/postman_collection.json` peut être importé
dans Postman pour tester en local ou sur Render.

Ce projet pédagogique expose volontairement le CRUD sans authentification : toute
personne connaissant l'URL peut modifier les stages. Utiliser uniquement des données
fictives. Avant un usage réel, prévoir authentification, autorisations, journaux
d'audit, limitation des requêtes et stockage durable.
