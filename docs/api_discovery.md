# API Discovery — France Travail Offres d’emploi

## Objectif

Documenter les premiers tests réalisés sur l’API Offres d’emploi de France Travail pour le projet **Data Job Market Radar**.

Cette phase sert à comprendre concrètement :

- l’authentification ;
- les endpoints disponibles ;
- la pagination ;
- les headers utiles ;
- la structure réelle des réponses ;
- les champs exploitables ;
- les limites et anomalies observées.

L’objectif n’est pas encore de définir le modèle analytique final, mais de collecter assez d’informations pour préparer une ingestion fiable et une phase de profiling.

---

## Sources

### Documentation officielle

Documentation France Travail — Offres d’emploi :

```text
https://francetravail.io/produits-partages/catalogue/offres-emploi/documentation#/api-reference/operations/recupererListeOffre
```

### Endpoint principal testé

```text
https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search
```

### Endpoint détail testé

```text
https://api.francetravail.io/partenaire/offresdemploi/v2/offres/{id}
```

---

## Authentification

L’API nécessite un token OAuth2 obtenu via le flux `client_credentials`.

### Requête de récupération du token

Méthode :

```http
POST
```

URL :

```text
https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire
```

Headers :

```http
Content-Type: application/x-www-form-urlencoded
```

Body en `x-www-form-urlencoded` :

```text
grant_type=client_credentials
client_id=<CLIENT_ID>
client_secret=<CLIENT_SECRET>
scope=api_offresdemploiv2 o2dsoffre
```

La réponse contient notamment :

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 1499
}
```

Le token doit ensuite être envoyé dans le header `Authorization` des appels API.

---

## Endpoint de recherche des offres

### Requête testée avec Bruno

Méthode :

```http
GET
```

URL :

```text
https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search?motsCles=data engineer&range=0-50
```

Headers :

```http
Authorization: Bearer <ACCESS_TOKEN>
Accept: application/json
```

### Paramètres testés

| Paramètre  |                Valeur testée | Rôle                                     |
| ---------- | ---------------------------: | ---------------------------------------- |
| `motsCles` |              `data engineer` | Recherche textuelle sur les offres       |
| `range`    | `0-50`, puis jusqu’à `0-149` | Pagination / plage de résultats demandée |

---

## Pagination et headers observés

Test réalisé avec une plage maximale observée :

```http
GET /partenaire/offresdemploi/v2/offres/search?motsCles=data engineer&range=0-149
```

Headers observés :

```http
accept-range: 150
content-range: offres 0-149/496
x-ratelimit-burst-capacity-clientidlimiter: 10
x-ratelimit-remaining-clientidlimiter: 9
x-ratelimit-replenish-rate-clientidlimiter: 10
x-ratelimit-requested-tokens-clientidlimiter: 1
```

### Interprétation

- `accept-range: 150` indique que la taille maximale de plage acceptée semble être **150 offres**.
- `content-range: offres 0-149/496` indique que la requête a retourné les offres **0 à 149** sur un total de **496 résultats** disponibles pour cette recherche.
- Les headers `x-ratelimit-*clientidlimiter` confirment une limite de **10 appels/tokens** côté client id.
- Chaque requête semble consommer **1 token**.

### Exemple de pagination théorique

Pour une recherche retournant 496 résultats :

```text
range=0-149
range=150-299
range=300-449
range=450-495
```

### Décision MVP

- Utiliser `range=0-149` comme taille de page maximale.
- Démarrer avec peu de pages par requête.
- Ajouter un délai volontaire entre les appels API.
- Logger les headers de pagination et de rate limit.

---

## Réponse observée

La réponse de `/offres/search` est un objet JSON contenant une clé principale :

```json
{
  "resultats": []
}
```

Chaque élément de `resultats` correspond à une offre d’emploi.

### Champs observés dans les offres

| Champ                         | Description observée                                                         |
| ----------------------------- | ---------------------------------------------------------------------------- |
| `id`                          | Identifiant unique de l’offre                                                |
| `intitule`                    | Titre de l’offre                                                             |
| `description`                 | Description longue de l’offre                                                |
| `dateCreation`                | Date de création de l’offre                                                  |
| `dateActualisation`           | Date de dernière actualisation                                               |
| `lieuTravail`                 | Localisation structurée : libellé, latitude, longitude, code postal, commune |
| `romeCode`                    | Code ROME associé                                                            |
| `romeLibelle`                 | Libellé ROME                                                                 |
| `appellationlibelle`          | Appellation métier                                                           |
| `entreprise`                  | Informations sur l’entreprise, parfois partielles                            |
| `typeContrat`                 | Code du type de contrat                                                      |
| `typeContratLibelle`          | Libellé du type de contrat                                                   |
| `natureContrat`               | Nature du contrat                                                            |
| `experienceExige`             | Code d’exigence d’expérience                                                 |
| `experienceLibelle`           | Libellé d’expérience, par exemple `3 An(s)` ou `Débutant accepté`            |
| `competences`                 | Liste de compétences structurées ou libres                                   |
| `salaire`                     | Salaire ou commentaire, format variable                                      |
| `dureeTravailLibelle`         | Durée de travail textuelle                                                   |
| `dureeTravailLibelleConverti` | Temps plein / temps partiel                                                  |
| `alternance`                  | Booléen indiquant si l’offre est en alternance                               |
| `contact`                     | Informations de contact ou URL de candidature                                |
| `agence`                      | Informations agence, parfois vides                                           |
| `nombrePostes`                | Nombre de postes                                                             |
| `qualificationCode`           | Code de qualification                                                        |
| `qualificationLibelle`        | Qualification du poste                                                       |
| `secteurActivite`             | Code secteur d’activité                                                      |
| `secteurActiviteLibelle`      | Libellé secteur d’activité                                                   |
| `origineOffre`                | Origine et URL de l’offre                                                    |
| `contexteTravail`             | Horaires ou conditions de travail                                            |

---

## Endpoint détail

Test réalisé avec l’offre :

```http
GET /partenaire/offresdemploi/v2/offres/207QYWM
```

### Constat

Pour l’offre testée, le endpoint détail retourne les mêmes informations que l’objet déjà présent dans la réponse de `/offres/search`.

### Décision MVP

- Ne pas appeler le endpoint détail pour toutes les offres au début.
- Se baser sur `/offres/search` pour l’ingestion initiale.
- Retester le endpoint détail plus tard sur un échantillon plus large si certains champs semblent absents, tronqués ou incohérents.

---

## Premiers constats sur les données

### Descriptions

Les descriptions sont longues et exploitables pour extraire des compétences techniques.

Exemples de technologies observées dans les descriptions ou compétences :

- Python ;
- SQL ;
- Spark ;
- Airflow ;
- dbt ;
- BigQuery ;
- Snowflake ;
- Databricks ;
- GCP ;
- AWS ;
- Power BI ;
- Tableau ;
- GitLab CI/CD.

### Compétences

Le champ `competences` peut contenir :

- des compétences normalisées avec un `code` ;
- des compétences libres sans code ;
- des compétences techniques ;
- des compétences transverses ou comportementales.

Ce champ ne suffit donc pas à lui seul pour extraire les technologies demandées. Il faudra probablement combiner :

- `competences.libelle` ;
- `description` ;
- éventuellement `intitule`.

### Salaire

Le champ `salaire` est présent mais son format varie beaucoup.

Formes observées :

```json
{
  "libelle": "Annuel de 30000.0 Euros à 40000.0 Euros sur 12.0 mois"
}
```

```json
{
  "commentaire": "Selon expérience"
}
```

```json
{
  "libelle": "Horaire de 17.0 Euros à 18.7 Euros sur 12.0 mois"
}
```

Il peut aussi contenir des compléments :

```json
{
  "complement1": "Titres restaurant / Prime de panier",
  "complement2": "Complémentaire santé",
  "listeComplements": []
}
```

### Décision MVP pour le salaire

Ne pas chercher à normaliser parfaitement les salaires dès le début.

Commencer avec :

- `has_salary_info` : booléen ;
- `salary_raw` : texte brut issu de `salaire.libelle` ou `salaire.commentaire` ;
- parsing avancé plus tard si le volume et la qualité le justifient.

---

## Qualité des filtres métier

### Mots-clés

Le paramètre `motsCles` est le filtre principal pour cibler les offres Data.

Exemples de mots-clés pertinents pour la suite :

```text
data engineer
ingénieur data
data analyst
analytics engineer
data scientist
machine learning engineer
ml engineer
```

### Code ROME

Le code ROME est utile mais ne doit pas être considéré comme parfaitement fiable.

Codes ROME envisagés pour l’analyse :

| Métier cible                                         | Code ROME |
| ---------------------------------------------------- | --------- |
| Data Engineer                                        | `M1811`   |
| Data Scientist                                       | `M1405`   |
| Data Analyst                                         | `M1419`   |
| Ingénieur systèmes, réseaux et sécurité informatique | `M1884`   |
| Ingénieur en Intelligence Artificielle               | `M1889`   |

### Anomalie observée

Une offre intitulée `ML engineer F/H` a été observée avec :

```json
{
  "romeCode": "H2904",
  "romeLibelle": "Forgeron industriel / Forgeronne industrielle"
}
```

Cette anomalie montre que le code ROME peut être mal renseigné.

### Décision MVP

- Collecter d’abord par mots-clés.
- Conserver les codes ROME pour profiling et analyse qualité.
- Ne pas filtrer exclusivement sur le code ROME.
- Utiliser les départements pour construire des vues géographiques, notamment sur l’Île-de-France.

---

## Zone géographique

Les départements sont pertinents pour limiter ou analyser les offres par zone.

Départements d’Île-de-France à cibler potentiellement :

| Département | Nom               |
| ----------: | ----------------- |
|          75 | Paris             |
|          77 | Seine-et-Marne    |
|          78 | Yvelines          |
|          91 | Essonne           |
|          92 | Hauts-de-Seine    |
|          93 | Seine-Saint-Denis |
|          94 | Val-de-Marne      |
|          95 | Val-d’Oise        |

Décision : commencer avec une collecte France entière sur quelques mots-clés, puis ajouter progressivement un mode focalisé Île-de-France.

---

## Doublons attendus

Les mêmes offres peuvent apparaître dans plusieurs recherches par mots-clés.

Exemples :

```text
motsCles=data
motsCles=data engineer
motsCles=ingénieur data
motsCles=ml engineer
```

Une même offre peut donc être collectée plusieurs fois.

### Décision MVP

- En landing/bronze : conserver les réponses telles qu’elles ont été reçues.
- En silver : dédupliquer par `id` d’offre.
- Conserver une table ou un fichier de mapping entre `offer_id`, `source_query`, `search_date` et `range` pour analyser quelles requêtes ont retourné quelles offres.

---

## Organisation des données

Structure recommandée :

```text
data/
├── landing/
│   └── france_travail/
│       └── offres/
│           └── search_date=YYYY-MM-DD/
│               └── query=data_engineer/
│                   └── range=0-149/
│                       ├── request.json
│                       ├── response.json
│                       ├── headers.json
│                       └── metadata.json
├── bronze/
│   └── france_travail/
│       └── job_offers/
│           └── search_date=YYYY-MM-DD/
│               └── part-000.jsonl
├── silver/
└── gold/
```

### Rôle des zones

| Zone      | Rôle                                                                        |
| --------- | --------------------------------------------------------------------------- |
| `landing` | Réponses API exactement comme reçues : request, response, headers, metadata |
| `bronze`  | Données brutes standardisées, par exemple une ligne JSONL par offre         |
| `silver`  | Données nettoyées, typées et dédupliquées                                   |
| `gold`    | Tables analytiques finales pour analyses et dashboard                       |

---

## Décisions actuelles

- Utiliser `/offres/search` comme endpoint principal d’ingestion.
- Ne pas appeler `/offres/{id}` systématiquement au MVP.
- Utiliser une page maximale de `range=0-149`.
- Respecter volontairement un délai entre les appels malgré la limite de 10 appels/seconde.
- Stocker les réponses brutes dans une landing zone.
- Ne pas figer le modèle analytique avant profiling.
- Utiliser les mots-clés comme stratégie principale de collecte.
- Utiliser les codes ROME comme signal d’analyse, pas comme vérité absolue.
- Dédupliquer les offres par `id` dans la couche silver.
- Traiter le salaire en `salary_raw` dans un premier temps.

---

## Questions restantes

- La limite `accept-range: 150` est-elle stable sur tous les types de requêtes ?
- Le total `content-range` varie-t-il fortement selon le moment de la journée ou les nouveaux dépôts d’offres ?
- Quelle proportion d’offres est dupliquée entre plusieurs mots-clés ?
- Quelle proportion d’offres contient une information salariale exploitable ?
- Quelle proportion d’offres contient une entreprise nommée ?
- Quelle proportion d’offres contient des compétences techniques dans `competences` versus seulement dans `description` ?
- Les codes ROME sont-ils souvent incohérents pour les métiers Data / IA ?
- Quels mots-clés donnent le meilleur compromis entre couverture et bruit ?
