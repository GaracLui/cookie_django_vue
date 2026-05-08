# Full‑Stack Project – Project State & Standards

**Last Updated:** 2026‑04‑30
**Stack:** Django Ninja (Python) + Vue 3 (TypeScript) + Vite + PostgreSQL + Podman/Docker

This document defines the current architecture, coding conventions, and technical decisions established during the development of a web application. It is intended to align human developers and AI assistants on consistent patterns.

---

## 1. Project Overview

| Component       | Technology         | Version / Notes                            |
|-----------------|--------------------|--------------------------------------------|
| Backend         | Django             | 6.0.4                                      |
| API Framework   | Django Ninja       | ≥1.5 (using `Swagger()` for docs)          |
| Package Manager | `uv`               | Replaces `pip` for speed & reproducibility |
| Database        | PostgreSQL         | 17‑alpine (Docker image)                   |
| Frontend        | Vue 3 + TypeScript | Created with `vue‑ts` template             |
| Build Tool      | Vite               | 8.x                                        |
| Container       | Podman (rootless)  | With `docker‑compose` compatibility        |
| Dev Environment | `podman‑compose`   | Services: `db`, `backend`, `frontend`      |

---

## 2. Directory Structure
```
name_website/               # Project root
├── .env                    # Environment variables 
├── .env.example            # Template for .env
├── docker-compose.yml      # Service orchestration
├── backend/
│ ├── Dockerfile
│ ├── pyproject.toml        # Dependencies 
│ ├── uv.lock               # Locked dependency tree
│ ├── manage.py
│ ├── .dockerignore         # Excludes .venv/, pycache, etc.
│ ├── config/               # Django project settings
│ │ ├── init.py
│ │ ├── asgi.py
│ │ ├── wsgi.py
│ │ ├── urls.py
│ │ ├── api.py              # NinjaAPI instance 
│ │ └── settings/
│ │   ├── init.py           # Loads development.py by default
│ │   ├── base.py           # Shared settings 
│ │   └── development.py    # DEBUG=True, etc.
│ ├── apps/                 # Custom Django apps 
│ │ ├── init.py
│ │ └── core/               # Shared base models & utilities
│ │   ├── models.py         # TimestampedModel, SoftDeleteModel, BaseModel
│ │   ├── schemas.py        # (future) reusable Pydantic fields
│ │   └── api.py
│ ├── static/               # Collected static files 
│ └── staticfiles/          # Production static root 
├── frontend/
│ ├── Dockerfile
│ ├── package.json
│ ├── package‑lock.json
│ ├── vite.config.ts        # Proxy /api → http://backend:8000
│ ├── .dockerignore         # Excludes node_modules/, dist/, etc.
│ ├── index.html
│ ├── src/
│ │ ├── main.ts
│ │ ├── App.vue
│ │ ├── components/
│ │ ├── views/
│ │ ├── router/
│ │ ├── stores/             # Pinia stores
│ │ └── types/              # TypeScript interfaces 
│ └── public/
```


### 2.1 Planned Django Apps
| App         | Purpose                              |
|-------------|--------------------------------------|
| `core`      | Shared base models, health endpoint |
| `pages`     | Home, About, Services (static-like) |
| `blog`      | Legal articles, guides              |
| `contact`   | Consultation/contact form           |
| `accounts`  | Lawyer profiles (optional client accounts) |
---

## 3. Docker / Podman Configuration Standards

### 3.1 `docker-compose.yml` Key Directives

- **`user: "0:0"`** on `backend` and `frontend` services (development only) → bypasses permission issues with bind mounts in rootless Podman. 
- **Anonymous volumes** protect container‑specific directories:
  - → `/app/.venv` for backend
  - → `/app/node_modules` for frontend
- **`Healthcheck`** on `db` → backend waits with condition: service_healthy
- **`Healthcheck`** on `backend` (/api/health) → frontend waits with condition: service_healthy

#### Django Ninja health check
```python
# In config/api.py or apps/core/api.py
@api.get("/health", auth=None, tags=["system"])
def health(request):
    return {"status": "ok"}
```
### 3.2 `Dockerfile` Patterns

#### Backend (`backend/Dockerfile`)
```backend/dockerfile
FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /usr/local/bin/uv
WORKDIR /app
# Only curl is required (healthcheck); no build tools needed for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev && uv cache clean
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Frontend (`frontend/Dockerfile`)
```frontend/dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]
```

---

## 4. Backend Coding Standards (Django + Ninja)
### 4.1 Abstract Base Models (DRY)

Located in apps/core/models.py:
```python
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    class Meta: abstract = True

class BaseModel(TimestampedModel, SoftDeleteModel):
    class Meta: abstract = True
```

### 4.2. Structure and Organization
As your project grows, keeping all endpoints in a single file becomes unmanageable.

- **Use Routers**: Split your API into logical modules using Router objects.
- **Centralize the API Instance**: Create a main `api.py` in your project folder to group all routers together.
- **Keep Schemas Near Views**: For smaller apps, keep your Pydantic schemas in the same file as your views for better visibility, or in a `schemas.py` file within each app for larger projects. 

### 4.3. Schema Management
Schemas are the backbone of data validation and documentation in Django Ninja.

- **NO USE ModelSchema**: generate specific Pydantic schemas from each Django models.
- **Define Clear Input/Output**: Always explicitly define response and request schemas in your decorators to ensure auto-generated OpenAPI/Swagger documentation is accurate.
- **Avoid Generic Schemas**: While tempting for speed, every endpoint should ideally have its own schema to prevent linting errors and unintended data leaks. 

### 4.4. Security and Authentication 

- **Use Built-in Authenticators**: Leverage Ninja’s native support for API Keys, Bearer tokens, and Basic Auth. 
- **Session Integration**: For internal tools, use SessionAuth to leverage Django’s existing session management and CSRF protection. 
- **For this project**: admins will use Django sessions (`django-ninja-jwt` for API auth). Public endpoints ( for example: home, blog, services, contact form) will be unauthenticated. Client accounts are **not** required initially; the contact form will send an email / save a request.

### 4.5. Performance Optimization 

- **Adopt Async**: Use async def for I/O-bound tasks (like external API calls or complex database queries) to handle higher concurrency. 
- **Caching**: Fast code is good, but no code is better. Use Django’s caching framework for expensive GET requests. 

### 4.6. Development Workflow 

- **Register in INSTALLED_APPS**: Add ninja to your INSTALLED_APPS so that static files for Swagger/Redoc are served locally rather than from a CDN, ensuring your docs work offline and load faster. 
- **Exception Handling**: Create custom exception handlers to standardize error responses across your entire API. 
- **Type Safety**: Use Python type hints strictly; they are not just for documentation but drive the actual data validation engine. 

### 4.7. Testing 

- **Thorough Coverage**: Implement tests. 

### 4.8. Media / file upload handling

- **media is stored**:
    - **development**: local `/media/`
    - **production**: `S3`
    - `MEDIA_URL` must be served.
- In `docker-compose.yml` you might later add a volume for media files.
---

## 5. Frontend Standards (Vue 3 + TypeScript + Vite)
### 5.1 Vite Proxy Configuration

frontend/vite.config.ts:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,      // Required for Docker container
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true  // Better for Docker volume mounts
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://backend:8000',
        changeOrigin: true,
      }
    }
  }
})
```
#### Planned dependencies
- vue-router
- pinia

### 5.2 TypeScript Usage

- Prefer <script setup lang="ts"> in .vue files.

- Define interfaces for all API responses in src/types/.

- Use Pinia for global state (auth, cart) with typed stores.

### 5.3 Code Style (Planned)

- ESLint + Prettier (to be configured).

- Vue Router with route‑based code splitting:
    `const BlogPage = () => import('@/views/BlogPage.vue')`
    `const ServiceDetail = () => import('@/views/ServiceDetail.vue')`
---

## 6. Development Workflow Commands

All commands run from project root.
```bash
# Start all services (rebuild if needed)
podman-compose up --build

# Run Django migrations
podman-compose exec backend uv run python manage.py migrate

# Create superuser
podman-compose exec backend uv run python manage.py createsuperuser

# Add a backend dependency
cd backend && uv add <package> && cd ..
podman-compose build backend

# Access container shells
podman-compose exec backend bash
podman-compose exec frontend sh

# View logs
podman-compose logs -f backend
```
---

## 7. Standards Applied by This AI Assistant

When generating code or advice for this project, I adhere to the following principles:

- **DRY via abstract models** – Always extend BaseModel for new entities if is feasible.

- **Multiple schema classes** – Separate input, output, and patch schemas.

- **Explicit over implicit** – Prefer clear, readable code over "magic" (e.g., Ninja's function‑based views vs DRF ViewSets).

- **Type safety** – Encourage TypeScript on frontend and Pydantic on backend.

- **Environment‑aware configuration** – Use .env and split settings files.

- **Container best practices** – Use uv for speed, protect node_modules/.venv with anonymous volumes.

- **Rootless Podman compatibility** – Provide `userns_mode` or `user: "0:0"` workarounds.

---

## enviroment secret variables

```.env
POSTGRES_DB=unique_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=ChangeMeInProduction!
POSTGRES_HOST=db
POSTGRES_PORT=5432

DJANGO_SECRET_KEY='your-secret-key-here'
DJANGO_DEBUG=1
```
