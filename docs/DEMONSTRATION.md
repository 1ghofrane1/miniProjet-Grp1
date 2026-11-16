# Scénario de démonstration et captures

Compter environ 6 à 8 minutes. Toutes les données ci-dessous sont fictives.
Réaliser d'abord ce scénario localement, puis sur l'URL Render.

1. Montrer `/health` : statut 200 et `status: ok`.
2. Ouvrir `/docs` : montrer les routes GET, POST, PUT, DELETE.
3. Exécuter POST `/stages` avec l'exemple du README : statut 201. Noter l'id retourné.
4. GET `/stages` : montrer le stage créé, statut 200.
5. GET `/stages/{id}` : retrouver le même contenu.
6. PUT `/stages/{id}` : recopier tous les champs et changer l'entreprise ; statut 200.
7. Envoyer une date de fin avant le début : statut 422 et message de validation.
8. DELETE `/stages/{id}` : statut 204, corps vide.
9. GET du même id : statut 404, « Stage introuvable ».
10. Montrer les tests, puis le Dockerfile, le conteneur et le déploiement Render.

## Captures à enregistrer dans docs/captures

- `01-swagger.png` : liste des endpoints.
- `02-creation-201.png` : requête POST et réponse avec id.
- `03-liste-200.png` : liste après création.
- `04-modification-200.png` : entreprise modifiée.
- `05-suppression-204.png` : suppression réussie.
- `06-introuvable-404.png` : lecture après suppression.
- `07-docker.png` : image construite, conteneur actif et Swagger local.
- `08-render-live.png` : tableau Render avec état Live et URL publique.
- `09-api-publique.png` : Swagger sur le domaine onrender.com avec réponse réelle.

Les captures doivent provenir des exécutions réelles. Ne pas inclure de mots de passe,
jetons ou paramètres de compte. Aucune capture de déploiement n'est fournie avant
qu'un déploiement ait réellement abouti.
