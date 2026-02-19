# Frontend React — Portfolio Livre Interactif

## Prérequis

- Node.js >= 20
- Backend FastAPI lancé (par défaut sur `http://localhost:8000` dans le conteneur)

## Installation

```bash
cd frontend_react
npm install
```

## Lancement (dev)

```bash
npm run dev
```

Puis ouvre l'URL affichée par Vite (souvent `http://localhost:5173`).

## API (important)

- Par défaut, le frontend utilise `/api` (proxy Vite) pour éviter les problèmes `Failed to fetch`.
- Le proxy redirige vers `http://localhost:8000` (côté conteneur).
- Tu peux changer la cible du proxy avec `VITE_PROXY_TARGET`.

## Build production

```bash
npm run build
```

## Fonctionnalités

- Interface livre en double-page (ouverte)
- Navigation fluide par clic sur moitié gauche/droite du livre
- Navigation clavier (`←` / `→`)
- Sommaire cliquable
- Son de tournage activable/désactivable
- Connexion API configurable en haut de page

## Endpoints consommés

- `GET /health`
- `GET /profile/global`
- `GET /projects`
- `GET /experiences`
- `GET /skills`
- `GET /technologies`
- `GET /profile/hobbies`
- `GET /skills/{name}/projects`
