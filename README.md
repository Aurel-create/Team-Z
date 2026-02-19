# Team-Z

Ce projet a pour objectif de créer tout le back-end de son portfolio avec FastAPI et deux types de bases 
MongoDB et Neo4j.

## Commandes 

### Execution des docker bdd 
```bash
docker compose up
```

### Seed des informations

```bash
python -m backend.scripts.seed_all
```

#### lancement du back-end 
```bash
uv run python backend/run.py
```