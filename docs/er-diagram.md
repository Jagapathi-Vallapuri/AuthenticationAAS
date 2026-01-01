# ER Diagram (Database Schema)

This ER diagram is derived from the SQLAlchemy models in `app/models/` and the initial Alembic migration in `migrations/versions/dd9e86f763e9_initial_schema.py`.

Preview options:
- VS Code: open this file and use the Markdown Preview (Mermaid support required).
- Mermaid Live: https://mermaid.live (paste the Mermaid block below)

```mermaid
---
title: AuthenticationAAS - ER Diagram
---
erDiagram
    direction LR

    USERS {
        BIGINT id PK
        CITEXT email UK
        TEXT password_hash UK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
        BOOLEAN is_verified
        BOOLEAN is_active
    }

    ROLES {
        BIGINT id PK
        STRING name UK
        TEXT description
    }

    PERMISSIONS {
        BIGINT id PK
        STRING name UK
        TEXT description
    }

    USER_ROLES {
        BIGINT user_id PK, FK
        BIGINT role_id PK, FK
    }

    ROLE_PERMISSIONS {
        BIGINT role_id PK, FK
        BIGINT permission_id PK, FK
    }

    REFRESH_TOKENS {
        BIGINT id PK
        BIGINT user_id FK
        TEXT token_hash
        TEXT user_agent
        INET ip_address
        TIMESTAMPTZ created_at
        TIMESTAMPTZ expires_at
        BOOLEAN revoked
    }

    SESSIONS {
        BIGINT id PK
        BIGINT user_id FK
        BIGINT refresh_token_id FK  "UNIQUE"
        TEXT device_info
        TIMESTAMPTZ last_used_at
        BOOLEAN revoked
    }

    EMAIL_VERIFICATION_TOKENS {
        BIGINT id PK
        BIGINT user_id FK
        TEXT token_hash
        TIMESTAMPTZ expires_at
        BOOLEAN used
        TIMESTAMPTZ created_at
    }

    PASSWORD_RESET_TOKENS {
        BIGINT id PK
        BIGINT user_id FK
        TEXT token_hash
        TIMESTAMPTZ expires_at
        BOOLEAN used
        TIMESTAMPTZ created_at
    }

    AUDIT_LOGS {
        BIGINT id PK
        BIGINT user_id FK
        ENUM(audit_action_enum) action_type
        JSONB metadata
        INET ip_address
        TEXT user_agent
        TIMESTAMPTZ created_at
    }

    REVOKED_TOKENS {
        STRING jti PK
        TIMESTAMPTZ revoked_at
    }

    %% Relationships (crow's foot notation)
    USERS ||--o{ SESSIONS : has
    USERS ||--o{ REFRESH_TOKENS : owns

    %% One-to-one-ish link via sessions.refresh_token_id UNIQUE
    REFRESH_TOKENS ||--o| SESSIONS : linked

    USERS ||--o{ EMAIL_VERIFICATION_TOKENS : has
    USERS ||--o{ PASSWORD_RESET_TOKENS : has

    USERS ||--o{ AUDIT_LOGS : writes

    %% Many-to-many USER <-> ROLE via USER_ROLES
    USERS ||--o{ USER_ROLES : maps
    ROLES ||--o{ USER_ROLES : maps

    %% Many-to-many ROLE <-> PERMISSION via ROLE_PERMISSIONS
    ROLES ||--o{ ROLE_PERMISSIONS : maps
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : maps
```
