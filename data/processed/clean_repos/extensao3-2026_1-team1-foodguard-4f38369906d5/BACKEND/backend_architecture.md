# FoodGuard Backend — Architecture

Reference document for understanding the backend structure before any code modification.

---

## Tech Stack

- **Framework:** Django 4.2.16 + Django REST Framework 3.15.2
- **Database:** PostgreSQL 16
- **AI:** Google Gemini API (`gemini-2.5-flash`, temperature 0.7)
- **Server:** Uvicorn (ASGI)
- **Auth:** JWT (access + refresh) via `djangorestframework-simplejwt`; login por email (`users.backends.EmailBackend`)
- **Containerization:** Docker + VS Code Dev Containers
- **Python:** 3.12.9

---

## Directory Structure

```
BACKEND/
├── config/
│   ├── settings/
│   │   ├── base.py              # Core config (DB, apps, AI, auth)
│   │   └── local.py             # Dev overrides (debug, swagger)
│   ├── urls.py                  # Root URL config
│   ├── asgi.py
│   └── wsgi.py
│
├── foodguard/
│   ├── api/                     # REST layer
│   │   ├── serializers/         # anamnese.py, chat.py, message.py
│   │   ├── views/               # anamnese.py, chat.py, message.py
│   │   ├── urls/                # anamnese.py, chat.py, message.py
│   │   └── exceptions/          # anamnese.py, chat.py, message.py
│   │
│   ├── core/                    # Core logic
│   │   ├── models/              # base.py, anamnese.py, chat.py, message.py
│   │   ├── services/
│   │   │   └── gemini_client.py
│   │   ├── migrations/          # 10 migrations
│   │   ├── admin.py
│   │   └── urls.py
│   │
│   └── users/
│       ├── models.py            # Custom User (AbstractUser)
│       ├── validation.py        # Custom password validator
│       └── migrations/          # 2 migrations
│
├── data/
│   └── system_prompt.md        # Gemini system prompt
│
├── requirements/
│   ├── base.txt
│   └── local.txt
│
├── compose/local/django/        # Dockerfile + entrypoint + start
└── docker-compose.local.yml
```

---

## Data Models

### BaseModel (abstract — `core/models/base.py`)

- `id`: UUID primary key
- `is_active`: Boolean (default: True)
- `created_at`, `updated_at`: auto timestamps

### User (`users/models.py`) — extends `AbstractUser`

- `name`: validated (letters, spaces, apostrophes, hyphens only)
- `email`: unique, required (login identifier)
- `date_of_birth`: optional date
- Password: min 8 chars, uppercase + lowercase + digit required

### Anamnese (`core/models/anamnese.py`) — 1-to-1 with User

- Clinical: `previous_consultation`, `previous_consultation_objective`, `previous_consultation_result`, `disease_history`, `medications`
- Allergen profile: `food_allergies`, `food_intolerances`
- Diet: `favorite_foods`, `food_aversions`, `eating_style` (choices: Not/Vegetarian/Vegan)
- Health: `alcohol_intake`, `smoking`, `body_feeling` (choices)

### Chat (`core/models/chat.py`)

- `user`: FK → User
- `title`: auto-set from first message snippet (default: "Nova conversa")

### Message (`core/models/message.py`)

- `chat`: FK → Chat (cascade delete)
- `role`: 'U' (User) or 'A' (Assistant)
- `content`: max 5000 chars

### Relationships

```
User (1) ──── (1) Anamnese
User (1) ──── (N) Chat
Chat (1) ──── (N) Message
```

---

## API Endpoints

### Root (`config/urls.py`)

```
/admin/           → Django Admin
/api/             → foodguard.core.urls
/api/schema/      → OpenAPI schema
/api/docs/        → Swagger UI (debug only)
```

### Auth / Users (`/api/auth/`)

| Method | Endpoint          | View                       | Behavior                                              |
| ------ | ----------------- | -------------------------- | ----------------------------------------------------- |
| POST   | `/register/`      | RegisterView               | Cadastro (name, username, email, dob, senha) — RF001  |
| POST   | `/login/`         | EmailTokenObtainPairView   | Login por email → access/refresh + `has_anamnese`     |
| POST   | `/token/refresh/` | TokenRefreshView           | Renova o access token                                 |
| POST   | `/logout/`        | LogoutView                 | Blacklist do refresh token (RF017)                    |
| GET    | `/me/`            | MeView                     | Perfil do usuário autenticado (+ `has_anamnese`)      |
| PATCH  | `/me/`            | MeView                     | Edita username/senha (RN010)                          |

### Anamnese (`/api/anamnese/`)

| Method | Endpoint | View                  | Behavior                          |
| ------ | -------- | --------------------- | --------------------------------- |
| POST   | `/`      | AnamneseCreateView    | Create anamnese (one per user)    |
| GET    | `/me/`   | AnamneseGetUpdateView | Get authenticated user's anamnese |
| PATCH  | `/me/`   | AnamneseGetUpdateView | Update + deactivate prior chats   |

### Chat (`/api/chats/`)

| Method | Endpoint      | View               | Behavior                           |
| ------ | ------------- | ------------------ | ---------------------------------- |
| GET    | `/`           | ChatListAPIView    | List user's chats (newest first)   |
| DELETE | `/<chat_id>/` | ChatDestroyAPIView | Delete chat (cascades to messages) |

### Message (`/api/chats/`)

| Method | Endpoint               | View                 | Behavior                               |
| ------ | ---------------------- | -------------------- | -------------------------------------- |
| POST   | `/message/send/`       | MessageCreateAPIView | Send msg → call Gemini → save response |
| GET    | `/<chat_id>/messages/` | MessageListAPIView   | List chat messages (paginated)         |

---

## Business Rules

1. **One anamnese per user:** raises `AnamneseHasAlreadyBeenCreatedException` if already exists
2. **Anamnese update invalidates chats:** `Chat.objects.filter(user=user, created_at__lte=updated_at).update(is_active=False)`
3. **Inactive chat blocks messages:** raises `ChatClosedException` if `chat.is_active=False`
4. **Message send flow:**
   1. Validate role (client can only send role='U')
   2. Get or create chat (uses message snippet as title if new)
   3. Save user message
   4. Call `GeminiClient.generate_response(content)`
   5. Save AI response as role='A'
   6. Return `{ chat_id, response }` — HTTP 201

---

## Gemini Service (`core/services/gemini_client.py`)

```python
class GeminiClient:
    def __init__(self, model_id=None, system_prompt=None, temperature=None)
    def generate_response(prompt: str) -> str
```

- API key: `settings.GEMINI_API_KEY` (env var)
- Model: `gemini-2.5-flash`
- System prompt: read from `data/system_prompt.md`
- Fallback: returns error message if prompt file not found

### AI Role (system_prompt.md)

Nutrition assistant specialized in food safety:

- Input: ingredients list + user anamnese + user query
- Analysis: cross-references ingredients against health profile
- Output: SAFE/DANGEROUS verdict + technical explanation + medical disclaimer

---

## Custom Exceptions

| Exception                                | Status | When                                          |
| ---------------------------------------- | ------ | --------------------------------------------- |
| `AnamneseHasAlreadyBeenCreatedException` | 400    | User already has anamnese                     |
| `AnamneseObjectiveRequiredException`     | 400    | `previous_consultation=True` but no objective |
| `ChatClosedException`                    | 400    | Message sent to inactive chat                 |
| `RoleNotAllowedException`                | 403    | Client tries to send as assistant             |

---

## Django Settings (`config/settings/base.py`)

- `AUTH_USER_MODEL = 'users.User'`
- Pagination: LimitOffset, page_size=20
- Timezone: `America/Fortaleza`
- `ATOMIC_REQUESTS = True`
- REST auth: `JWTAuthentication` (simplejwt) + `SessionAuthentication` (admin/swagger)
- `AUTHENTICATION_BACKENDS`: `users.backends.EmailBackend` → `ModelBackend`
- `SIMPLE_JWT`: access 1h, refresh 24h, rotate + blacklist

---

## Dev Environment

- Docker: `docker-compose.local.yml` (Django:8000 + Postgres:5432)
- Dev Container: VS Code → F1 → "Reopen in Container"
- Pre-commit hooks: Black, isort, Ruff, djLint
- Swagger: `http://localhost:8000/api/docs/` (debug mode only)

---

## Key Dependencies

```
django==4.2.16
djangorestframework==3.15.2
django-cors-headers==4.7.0
drf-spectacular==0.28.0
django-allauth==65.4.1
psycopg[c]==3.2.5
google-genai==1.75.0
uvicorn==0.34.0

# dev
pytest, mypy, ruff, pre-commit, factory-boy, faker
```
