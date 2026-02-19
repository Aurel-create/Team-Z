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
$env:PYTHONPATH="backend/src"
python -m scripts.seed_all
```

ou 

```bash
python backend/src/backend/scripts/seed_all.py
```

#### lancement du back-end 
```bash
uv run python backend/run.py
```

| #  | Source          | Relation          | Cible           | Logique                                            |
| -- | --------------- | ----------------- | --------------- | -------------------------------------------------- |
| 1  | `Person`        | `CREATED`         | `Project`       | La personne a créé des projets                     |
| 2  | `Person`        | `WORKED_AT`       | `Experience`    | La personne a travaillé dans ces expériences       |
| 3  | `Person`        | `STUDIED_AT`      | `Education`     | Parcours scolaire                                  |
| 4  | `Person`        | `OBTAINED`        | `Certification` | Certifications obtenues                            |
| 5  | `Person`        | `MASTER`          | `Skill`         | Compétences maîtrisées                             |
| 6  | `Person`        | `PRACTICES`       | `Hobby`         | Loisirs pratiqués                                  |
| 7  | `Person`        | `KNOWS`           | `Technology`    | Technologies connues                               |
| 8  | `Project`       | `USES_TECH`       | `Technology`    | Description du projet contient le nom d'une techno |
| 9  | `Project`       | `REQUIRES_SKILL`  | `Skill`         | Description du projet contient le nom d’un skill   |
| 10 | `Experience`    | `APPLIED_SKILL`   | `Skill`         | Description/nom contient un skill                  |
| 11 | `Experience`    | `USED_TECH`       | `Technology`    | Description/nom contient une techno                |
| 12 | `Skill`         | `BELONGS_TO`      | `Category`      | Organisation par catégorie                         |
| 13 | `Certification` | `VALIDATES_SKILL` | `Skill`         | Certification mentionne un skill                   |
| 14 | `Certification` | `VALIDATES_TECH`  | `Technology`    | Certification mentionne une techno                 |
| 15 | `Education`     | `TAUGHT_SKILL`    | `Skill`         | Formation mentionne un skill                       |
| 16 | `Education`     | `TAUGHT_TECH`     | `Technology`    | Formation mentionne une techno                     |
| 17 | `Skill`         | `INVOLVES_TECH`   | `Technology`    | Un skill implique une techno                       |
