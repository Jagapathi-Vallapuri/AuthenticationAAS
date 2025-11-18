# AuthenticationAAS

AuthenticationAAS is a FastAPI-powered "Authentication as a Service" stack that ships ready-made APIs for registration, login, refresh tokens, password resets, RBAC, and audit logging. It pairs an async PostgreSQL backend with Alembic migrations and includes static Vite pages for email verification and password reset flows.

## Features

- **Auth flows**: registration, login, logout, refresh-tokens, email verification, password reset, token revocation.
- **Security**: RS256 JWTs, bcrypt-hashed passwords, refresh-token rotation, session tracking per device/IP.
- **RBAC**: role, permission, and session management endpoints to administer tenants.
- **Auditing**: all user-facing actions are written to the audit log for traceability.
- **Email delivery**: SMTP-powered verification and password reset links with HTML templates.
- **Frontend helpers**: `auth-frontend/` exposes lightweight Vite apps for verification and password reset UX.

## Tech Stack

| Area | Implementation |
| --- | --- |
| API | FastAPI (async), Pydantic schemas |
| Persistence | PostgreSQL via async SQLAlchemy + psycopg |
| Migrations | Alembic |
| Auth | RS256 JWT + refresh tokens |
| Emails | aiosmtplib with HTML templates |
| Frontend | Vite + React (verification, reset) |

## Project Layout

```
AuthenticationAAS/
├── app/                # FastAPI application package
│   ├── api/            # Route modules (auth, users, roles, sessions)
│   ├── core/           # Security helpers
│   ├── db/             # Async engine + session factory
│   ├── models/         # Declarative SQLAlchemy models
│   ├── schemas/        # Pydantic request/response contracts
│   └── services/       # Business logic (auth, tokens, email, roles…)
├── migrations/         # Alembic migration scripts
├── auth-frontend/      # Vite project with static verification/reset pages
├── alembic.ini         # Alembic config
├── testing.key         # Sample private key (dev only)
├── testing_public.key  # Sample public key (dev only)
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (only needed to run the Vite helper app)
- PostgreSQL instance reachable from the API
- SMTP credentials for outbound email (startTLS capable)

## Backend Setup

1. **Create a virtual environment and install dependencies**

    ```pwsh
    cd C:\Users\Jagapathi Vallapuri\Desktop\Projects\AuthenticationAAS
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r app\requirements.txt
    ```

2. **Create a `.env` file at the project root** (matching the variables the services consume):

    ```env
    # PostgreSQL (psycopg async URL pieces)
    user=postgres
    password=postgres
    host=localhost
    port=5432
    dbname=authentication_aas

    # JWT / token settings
    PRIVATE_KEY_PATH=testing.key
    PUBLIC_KEY_PATH=testing_public.key
    ACCESS_TOKEN_EXPIRES_MINUTES=15
    REFRESH_TOKEN_EXPIRES_DAYS=30

    # Email delivery
    SMTP_HOST=smtp.example.com
    SMTP_PORT=587
    SMTP_USER=apikey
    SMTP_PASSWORD=secret
    SMTP_FROM=no-reply@example.com
    APP_BASE_URL=http://localhost:3000

    # Optional cookie name overrides
    ACCESS_TOKEN_COOKIE_NAME=access_token
    ```

    > Use either `_PATH` variables pointing to PEM files or inline `PRIVATE_KEY` / `PUBLIC_KEY` values.

3. **Run database migrations**

    ```pwsh
    alembic upgrade head
    ```

4. **Launch the API server**

    ```pwsh
    uvicorn app.main:app --reload --port 8000
    ```

    To exercise the TLS-ready certificates checked in for local testing:

    ```pwsh
    uvicorn app.main:app --host 0.0.0.0 --port 8443 ^
        --ssl-keyfile testing.key --ssl-certfile cert.crt
    ```

5. **Access interactive docs** at `http://localhost:8000/docs` (or `https://localhost:8443/docs`).

## Frontend (verification / reset helpers)

1. Install dependencies and run the dev server:

    ```pwsh
    cd auth-frontend
    npm install
    npm run dev
    ```

2. Update the `apiBase` constants in `index.html` / `verify-email.html` / `reset-password.html` if your backend URL differs.

3. Deploy the built assets with `npm run build` (served by any static host).

## Common Workflows

- **Request password reset**: `POST /auth/password-reset/request` with `{ "email": "user@example.com" }`.
- **Confirm password reset**: `POST /auth/password-reset/confirm` with `{ "token": "...", "new_password": "..." }`.
- **Verify email**: `POST /auth/verify-email/confirm` with `{ "token": "..." }`.
- **Admin endpoints**: authenticate an admin user, then call `/users`, `/roles`, `/sessions` with the `Authorization: Bearer <token>` header.

## Testing

- Add automated tests under a `tests/` package (pytest is the default choice, no suite included yet).
- Use Postman collections or HTTPie to script auth flows. Example refresh:

    ```pwsh
    curl -X POST http://localhost:8000/auth/refresh ^
         -H "Content-Type: application/json" ^
         -d "{ \"refresh_token\": \"<token>\" }"
    ```

## Troubleshooting Tips

- **Invalid token errors**: ensure you generate password-reset tokens via `/auth/password-reset/request` (they differ from email tokens).
- **Failed to fetch in browser**: accept the self-signed cert on `https://localhost:8443` or use HTTP for local dev, and confirm `apiBase` matches the backend URL.
- **Email delivery**: check SMTP credentials and that `APP_BASE_URL` matches where your static pages are hosted.

## License

This repo does not specify a license; treat it as all-rights-reserved unless a LICENSE file is added.
