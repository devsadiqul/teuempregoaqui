# TeuEmpregoAqui — Backend (Django + DRF)

Migration employability platform. Matches a migrant's profile against jobs using
the **ESCO ⇄ ROME crosswalk**, a transparent **compatibility scoring engine**,
a **"How to Solve" gap-resolution** layer, and **live France Travail** vacancies.

All API views are **function-based** (`@api_view`) and documented with
**`@swagger_auto_schema`** (drf-yasg). Each endpoint lives in its own file under
`<app>/views/`.

---

## 1. Project layout

```
teuempregoaqui/          project settings, root urls (+ Swagger), wsgi/asgi
manage.py
requirements.txt

crosswalk/               ESCO occupations + skills + ROME→ESCO mapping
  models.py              EscoOccupation, OccupationSkill, RomeEscoMapping
  serializers.py
  views/                 occupation_list.py, occupation_detail.py, occupation_skills.py
  management/commands/load_esco.py
  urls.py

candidate/               the 8-section assessment form + scoring + gap resolution
  models.py              CandidateProfile, Education, WorkExperience, ...
  scoring.py             Employment Compatibility Index (Fernando's matrix)
  resolutions.py         "How to Solve" knowledge base
  services.py            profile scoping + match orchestration (shared by views)
  serializers.py
  views/                 profile_collection.py, profile_detail.py, match.py, how_to_solve.py
  management/commands/purge_private_profiles.py
  urls.py

francetravail/           live job integration (OAuth2 + Offres d'emploi v2)
  client.py              OAuth token + search client
  gdpr.py                recruiter-PII redaction
  services.py            offer → ESCO resolution (by appellation label) + sync
  models.py              JobOffer (active mirror)
  serializers.py
  views/                 offer_list.py, offer_sync.py, offer_match.py
  management/commands/sync_france_travail.py
  urls.py
```

---

## 2. Setup

```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt

# (optional) PostgreSQL — recommended for the 126k-row skill table.
# Set these env vars; without them the project falls back to SQLite.
export DB_NAME=teuempregoaqui DB_USER=postgres DB_PASSWORD=secret DB_HOST=127.0.0.1

# France Travail credentials (from francetravail.io → your app → Identifiers)
export FT_CLIENT_ID="PAR_xxx..."
export FT_CLIENT_SECRET="xxx..."

python manage.py migrate
python manage.py createsuperuser        # needed for the admin-only sync endpoint
python manage.py runserver
```

API docs: **http://localhost:8000/swagger/** (or `/redoc/`).

---

## 3. Load the crosswalk data (one time)

Put these files in a folder (e.g. `./esco/`):
`occupations_en.csv`, `occupationSkillRelations_en.csv`, `EURESmapping_occs_FR.csv`.

```bash
python manage.py load_esco --dir ./esco --flush
```

Expected:
```
esco_occupation       :   3,043 (16 regulated)
esco_occupation_skill : 126,051
rome_esco_mapping     :  13,102 (18 orphan rows skipped)
```

---

## 4. Sync live France Travail offers

```bash
# via CLI (cron/celery-friendly)
python manage.py sync_france_travail --rome M1805 --departement 75

# or via the admin-only API endpoint
POST /api/offers/sync/   { "mots_cles": "developpeur", "departement": "75" }
```

Schedule on a timer (offers auto-purge when no longer active / older than 30 days):
```
*/30 * * * *  python manage.py sync_france_travail --mots-cles "developpeur"
*/15 * * * *  python manage.py purge_private_profiles      # GDPR: drop expired private profiles
```

---

## 5. Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/occupations/` | Search ESCO occupations (`?q=`) |
| GET | `/api/occupations/<uuid>/` | One occupation |
| GET | `/api/occupations/<uuid>/skills/` | Its skills (`?relation=essential`) |
| GET/POST | `/api/candidates/` | List / create candidate profiles |
| GET/PUT/PATCH/DELETE | `/api/candidates/<id>/` | Retrieve / update / delete |
| POST | `/api/match/` | Score candidate vs target occupation |
| POST | `/api/how-to-solve/` | Gap resolution (single gap or full report) |
| GET | `/api/offers/` | List mirrored live offers |
| POST | `/api/offers/sync/` | Trigger a sync (admin) |
| POST | `/api/offers/<source_id>/match/` | Score candidate vs a live offer |

### Privacy modes (GDPR/LGPD)
- **Private**: no account; profile bound to the session, auto-deleted after a TTL.
- **Account**: `mode=account` requires authentication + `consent_given=true`; stored.

---

## 6. How matching works

```
candidate profile  ──┐
                     ├─►  scoring.score()  ──►  blocks + total + classification
target occupation  ──┘                          + named missing skills
   (essential skills via ESCO)                  + evolution (current → potential)
```

Scoring weights (verbatim from the client spec, sum = 1.00):
`experience 0.25 · education 0.20 · skills 0.15 · languages 0.20 · immigration 0.15 · documentation 0.05`.

**Live offer → ESCO:** the Offres d'emploi API returns the ROME *métier* code and
the appellation *label* (no appellation code). We resolve by matching that label
(accent-normalized) against `RomeEscoMapping.rome_label`. For the rare offers whose
label doesn't match, add the ROME 4.0 Professions referential as a métier-level
fallback (both APIs are already subscribable on the same France Travail app).

---

## 7. Notes / things to verify before production

- The "How to Solve" institution names, URLs, costs and timelines in
  `candidate/resolutions.py` are **starter values — verify them** and ideally move
  to an admin-editable table.
- `EQF_TO_EDU_SCORE` (EQF 5) and the 50/50 documentation blend in `scoring.py` are
  the only interpolations where the spec was silent — tune as the client prefers.
- Run `python manage.py makemigrations` then `migrate` if you change any model.
```
