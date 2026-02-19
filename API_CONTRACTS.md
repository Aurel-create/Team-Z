# 📋 Contrats d'API — Portfolio Backend

---

## 🔹 GET /

### Description
Route racine — message de bienvenue.

### Paramètres
Aucun.

### Réponse 200

```json
{
  "message": "string"
}
```

---

## 🔹 GET /health

### Description
Vérification de l'état de santé de l'API.

### Paramètres
Aucun.

### Réponse 200

```json
{
  "status": "string",
  "version": "string"
}
```

---

## 🔹 GET /personal-infos

### Description
Retourne les informations personnelles (nom, prénom, contact, description) depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
{
  "id": "string",
  "nom": "string",
  "prenom": "string",
  "contact": {
    "liens_linkedin": "string | null",
    "telephone": "string | null",
    "email": "string | null"
  },
  "description": "string"
}
```

### Réponse 404

```json
{
  "detail": "Aucune info personnelle trouvée"
}
```

---

## 🔹 GET /personal-infos/certifications

### Description
Retourne la liste complète des certifications obtenues depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "image": "string | null",
    "description": "string",
    "obtention_date": "date | null"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucune certification trouvée"
}
```

---

## 🔹 GET /portfolio/skills

### Description
Retourne la liste complète des compétences depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "category": "string",
    "description": "string"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucun skill trouvé"
}
```

---

## 🔹 GET /portfolio/projets

### Description
Retourne la liste complète des projets depuis MongoDB (sans agrégation Neo4j).

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "date_debut": "date | null",
    "date_fin": "date | null",
    "description": "string",
    "images": ["string"],
    "entreprise": "string",
    "collaborateurs": ["string"],
    "lien_github": "string | null",
    "status": "string"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucun projet trouvé"
}
```

---

## 🔹 GET /portfolio/projets/details

### Description
Retourne les projets depuis MongoDB, enrichis avec les technologies et compétences liées via les relations `USES_TECHNOLOGY` et `REQUIRES_SKILL` du graphe Neo4j.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "date_debut": "date | null",
    "date_fin": "date | null",
    "description": "string",
    "images": ["string"],
    "entreprise": "string",
    "collaborateurs": ["string"],
    "lien_github": "string | null",
    "status": "string",
    "technologies": ["string"],
    "skills": ["string"]
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucun projet trouvé"
}
```

---

## 🔹 GET /portfolio/technologies

### Description
Retourne la liste complète des technologies maîtrisées depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "image": "string | null"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucune technologie trouvée"
}
```

---

## 🔹 GET /portfolio/hobbies

### Description
Retourne la liste complète des loisirs et centres d'intérêt depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "description": "string"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucun hobby trouvé"
}
```

---

## 🔹 GET /portfolio/experiences

### Description
Retourne la liste complète des expériences professionnelles depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "nom": "string",
    "description": "string",
    "image": "string | null",
    "company": "string",
    "type_de_poste": "string",
    "date_debut": "date | null",
    "date_fin": "date | null",
    "role": "string"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucune expérience trouvée"
}
```

---

## 🔹 GET /portfolio/parcours-scolaire

### Description
Retourne la liste complète du parcours scolaire depuis MongoDB.

### Paramètres
Aucun.

### Réponse 200

```json
[
  {
    "id": "string",
    "school_name": "string",
    "degree": "string",
    "description": "string",
    "start_year": "int | null",
    "end_year": "int | null",
    "grade": "string"
  }
]
```

### Réponse 404

```json
{
  "detail": "Aucun parcours scolaire trouvé"
}
```
