# Frontend Streamlit — Portfolio (Livre Interactif)

## Lancer l'application

Depuis la racine du projet:

```bash
streamlit run frontend_streamlit/app.py
```

Le fichier `app.py` délègue vers `streamlit_app.py` (interface flipbook).
Si ton backend FastAPI n'est pas sur `http://localhost:8000`, modifie l'URL API en haut de page.

## Fonctionnalités

- Interface livre avec pages navigables (couverture, sommaire, projets, expériences, graphe, contact)
- Navigation par flèches avec état `session_state.page_index`
- Vue globale via `GET /profile/global`
- Vue projets via `GET /projects`
- Recherche de projets par compétence via `GET /skills/{name}/projects`
- Vérification de santé backend via `GET /health`
