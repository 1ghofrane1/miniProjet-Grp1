# Gestion des stages : API REST et déploiement Cloud

**Module :** Cloud Computing, Microservices et API  
**Enseignante :** Emna TRIGUI  
**Équipe :** Ghofrane Bouallegue, Mohamed Aziz Braham, Dheker Kraiem, Malek Gabsi

## 1. Objectif et périmètre

Le projet répond au besoin d'une école souhaitant gérer les stages des étudiants.
L'API crée, consulte, modifie et supprime les stages. Chaque stage comprend un
identifiant, le nom de l'étudiant, l'entreprise, l'intitulé et les dates de début et de fin.
L'interface de démonstration est Swagger UI. Les exemples utilisent des données fictives.

## 2. Architecture

```text
Navigateur / Swagger / Postman
              |
          HTTP JSON
              |
     Uvicorn + API FastAPI
              |
       SQLite (stages.db)

Local : application Python ou conteneur Docker + volume
Cloud : GitHub -> construction Docker sur Render -> URL publique HTTPS
```

FastAPI définit le contrat REST et génère la documentation OpenAPI. Pydantic valide
les requêtes. SQLite fournit un stockage relationnel simple, adapté à cet exercice.
Le module standard sqlite3 évite une dépendance de base de données supplémentaire.
Les services n'ont pas besoin d'un découpage supplémentaire pour ce périmètre réduit.

## 3. Modèle et règles métier

La table `stages` contient `id INTEGER PRIMARY KEY AUTOINCREMENT`, trois textes
obligatoires (`nom_etudiant`, `entreprise`, `intitule`) et deux dates stockées en texte
ISO `AAAA-MM-JJ`. Les noms sont limités à 120 caractères, l'entreprise à 160,
l'intitulé à 200. Les espaces aux extrémités sont supprimés. Les textes vides sont
refusés et la date de fin doit être supérieure ou égale au début. Une contrainte SQL
complète la validation des dates. Les identifiants restent générés par le serveur.

## 4. Contrat HTTP

POST `/stages` retourne 201, la ressource et son en-tête Location. GET `/stages`
retourne une liste paginée ; GET `/stages/{id}` retourne un stage. PUT remplace
l'ensemble des champs métier. DELETE retourne 204 sans corps. Une ressource absente
donne 404 ; une entrée invalide donne 422. Les détails et exemples figurent au README.

## 5. Qualité et sécurité

Les requêtes SQL utilisent des paramètres plutôt qu'une concaténation de texte.
Chaque opération dispose d'une connexion fermée après usage et d'une transaction.
Les tests couvrent le cycle CRUD, les erreurs, la validation, la pagination et la
réouverture d'une même base. La CI rejoue ces tests et construit l'image Docker.

Le conteneur fonctionne avec un utilisateur non root. L'API ne possède pas de système
d'identité ou d'autorisation : elle doit rester une démonstration sans données réelles.
Le HTTPS du point d'accès Cloud protège le transport mais ne remplace pas les contrôles
d'accès. Une évolution de production inclurait OAuth2/OIDC, autorisations, audit,
limites de débit, sauvegardes et une base durable.

## 6. Docker et Cloud

L'image Python embarque le code et les dépendances. Un conteneur en est une instance
d'exécution. Le port est configurable par `PORT`. Le volume Docker local conserve
SQLite sans reconstruire l'image. Render peut construire la même image depuis GitHub
et exposer l'API sur Internet. Le déploiement est celui d'une application conteneurisée
sur une plateforme gérée ; aucun cluster Kubernetes n'est requis par l'énoncé.

Le système de fichiers Render gratuit est éphémère. La base peut disparaître après
redémarrage ou redéploiement et le service peut se mettre en veille. Ce choix est
conforme à l'objectif pédagogique, sans convenir à la gestion réelle de stages.

## 7. Validation et éléments restant à compléter

Le procès-verbal `docs/VALIDATION.md` consigne les vérifications réellement exécutées.
Les liens GitHub et Render doivent être ajoutés à `docs/LIVRAISON.md` après publication.
Les captures réelles attendues sont décrites dans `docs/DEMONSTRATION.md`.
Ce rapport ne constitue pas une preuve de déploiement public.

## 8. Références

- Cours fourni : CloudComputing&MicroServices.pdf, notamment REST, Docker et déploiement.
- Énoncé fourni : miniProjeCloud&Microservices- Enoncé.pdf, parties 1 à 4 et livrables.
- https://render.com/docs/free : limites des services gratuits, consulté le 16/11/2026.
- https://render.com/docs/docker : construction et déploiement Docker sur Render.

La répartition proposée des responsabilités est dans `docs/EQUIPE.md`.
