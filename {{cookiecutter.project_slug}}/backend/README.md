# E‑Commerce Backend

This directory contains the Django + Django Ninja backend for the SPA platform. The structure is designed for scalability, maintainability, and a clean separation of concerns—following modern Django best practices.

---
## 📁 Project Structure
```
backend/
├── .venv/                  # Virtual environment (created by uv, ignored by Docker)
├── Dockerfile              # Multi‑stage build definition
├── pyproject.toml          # Project metadata & dependencies (PEP 621)
├── uv.lock                 # Locked dependency tree (committed for reproducibility)
├── manage.py               # Django's command‑line utility
├── config/                 # Django project root
│ ├── init.py
│ ├── asgi.py               # ASGI entry point (async‑ready)
│ ├── wsgi.py               # WSGI entry point (traditional deployment)
│ ├── urls.py               # Root URL configuration
│ ├── api.py                # Django Ninja API instance
│ └── settings/             # Split settings module
│   ├── init.py             # Loads development.py by default
│   ├── base.py             # Settings common to all environments
│   ├── development.py      # Local development overrides
│   └── production.py       # (future) Production‑specific settings
├── apps/ # Custom Django applications
│   ├── init.py
│   └── core/               # Shared functionality (e.g., User profiles)
│       ├── models.py
│       ├── schemas.py      # Pydantic schemas for Ninja
│       └── api.py          # Ninja routers
├── static/                 # Collected static files (production)
└── staticfiles/            # (Optional) Additional static assets
```

---

## 🔍 Key Directories Explained

### `config/` – The Project Core

Instead of the default `backend/` or `mysite/`, the project is named `config`. This convention:

- **Avoids naming collisions** when the repository itself is already called `backend`.
- **Clearly communicates** that this folder contains configuration, not business logic.
- **Works seamlessly with Docker** where the working directory is `/app`.

---
### `config/settings/` – Split Settings Module

The monolithic `settings.py` is split into:

- **`base.py`** – Shared settings: `INSTALLED_APPS`, `MIDDLEWARE`, database configuration (via environment variables).
- **`development.py`** – Local overrides: `DEBUG=True`, relaxed `ALLOWED_HOSTS`, and additional static file directories.
- **`production.py`** – (To be added) Secure settings: `DEBUG=False`, strict `ALLOWED_HOSTS`, production email backends, and HTTPS enforcement.

**Why this matters:**
- Prevents accidental exposure of debug information in production.
- Makes environment‑specific configuration explicit and testable.
- Simplifies deployment automation (CI/CD pipelines can select the correct settings module via `DJANGO_SETTINGS_MODULE`).

---

### `apps/` – Custom Django Applications

All project‑specific apps live inside the `apps/` namespace. This avoids polluting the Python path and makes it easy to:

- **Distinguish** between third‑party packages and your own code.
- **Reuse** apps across projects if needed.
- **Maintain a clean root directory** (only `config`, `apps`, `static`, and `manage.py`).

**Note:** The `startapp` command creates an app with a dotted path:
```bash
python manage.py startapp products apps/products
```
Then update the app's apps.py:
```
name = 'apps.products'
```

---

### `config/api.py` – Centralised Ninja API Instance

Django Ninja requires a single `NinjaAPI` instance. Placing it in `config/api.py`:

- Keeps the root `urls.py` lean.

- Allows easy import of the `api` object into app‑specific routers.

- Provides a central place to configure API metadata, authentication, and documentation.

---

### 🧠 Why This Structure?

| Traditional Structure	        | This Structure	               | Benefit                                                        |
|-------------------------------|-------------------------------|----------------------------------------------------------------|
| `settings.py` in project root | `config/settings/*.py`        | Environment‑specific settings without conditional logic.       |
| Apps in project root	         | Apps inside `apps/`           | Clean separation between custom code and third‑party packages. |
| Single `urls.py`              | `config/api.py` + app routers | API endpoints are co‑located with their owning apps.           |
| `requirements.txt`            | `pyproject.toml` + `uv.lock`  | Faster, reproducible installs with uv.                         |

---

### 🐳 Docker & Podman Integration

The `Dockerfile` uses multi‑stage builds and `uv` for dependency management:

- `uv` is 10–100x faster than `pip` and creates a fully reproducible environment via `uv.lock`.

- Non‑root user (optional, configurable via `--build-arg UID`) improves security.

- Bind mounts in development (`.:/app`) enable hot‑reload while an anonymous volume protects the container’s `.venv`.

---

### 🔧 Development Workflow (with Podman)
```
# Start all services
podman-compose up

# Run migrations
podman-compose exec backend uv run python manage.py migrate

# Create a superuser
podman-compose exec backend uv run python manage.py createsuperuser

# Add a dependency
uv add <package>                 # Updates pyproject.toml and uv.lock
podman-compose build backend     # Rebuild image with new dependency

# Access the Django shell
podman-compose exec backend uv run python manage.py shell
```