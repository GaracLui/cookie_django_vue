# Makefile — lawyer project
# Uses `podman compose` (Podman 5.x native, requires Docker Compose plugin)
COMPOSE = podman compose

.PHONY: help \
        up dev down build rebuild \
        migrate mm superuser startapp shell test \
        logs logs-back logs-front logs-db \
        ps fix-perms \
        uv-add lint format \
        clean clean-db

# ─── Default ────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Usage: make <target> [APP=name] [PKG=package]"
	@echo ""
	@echo "── Containers ───────────────────────────────────────────────────────"
	@echo "  up            Start all containers (detached)"
	@echo "  dev           Start all containers, rebuild images first"
	@echo "  down          Stop and remove containers"
	@echo "  build         Build all images"
	@echo "  rebuild       Rebuild all images with --no-cache"
	@echo "  ps            Show running service status"
	@echo "  fix-perms     chmod -R 755 backend/ frontend/ (rootless Podman fix)"
	@echo ""
	@echo "── Django ───────────────────────────────────────────────────────────"
	@echo "  migrate       Run pending migrations"
	@echo "  mm            Make migrations  (APP=app_name for single app)"
	@echo "  superuser     Create a Django superuser"
	@echo "  startapp      Create a new app in apps/  (requires APP=name)"
	@echo "  shell         Open Django shell"
	@echo "  test          Run Django test suite  (APP=app_name for single app)"
	@echo ""
	@echo "── Dependencies ─────────────────────────────────────────────────────"
	@echo "  uv-add        Add a backend package  (requires PKG=package)"
	@echo ""
	@echo "── Logs ─────────────────────────────────────────────────────────────"
	@echo "  logs          Tail all services"
	@echo "  logs-back     Tail backend only"
	@echo "  logs-front    Tail frontend only"
	@echo "  logs-db       Tail database only"
	@echo ""
	@echo "── Frontend ─────────────────────────────────────────────────────────"
	@echo "  lint          Run ESLint on frontend"
	@echo "  format        Run Prettier on frontend"
	@echo ""
	@echo "── Cleanup ──────────────────────────────────────────────────────────"
	@echo "  clean         Remove ALL containers + volumes  (data loss!)"
	@echo "  clean-db      Remove only the database volume  (data loss!)"
	@echo ""

# ─── Containers ─────────────────────────────────────────────────────────────
up:
	$(COMPOSE) up -d

dev:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) build --no-cache

ps:
	$(COMPOSE) ps

fix-perms:
	chmod -R 755 backend/ frontend/

# ─── Django ──────────────────────────────────────────────────────────────────
migrate:
	$(COMPOSE) exec backend uv run python manage.py migrate

mm:
	$(COMPOSE) exec backend uv run python manage.py makemigrations $(APP)

superuser:
	$(COMPOSE) exec backend uv run python manage.py createsuperuser

startapp:
	@if [ -z "$(APP)" ]; then \
		echo "Usage: make startapp APP=app_name"; \
		exit 1; \
	fi
	$(COMPOSE) exec backend uv run python manage.py startapp $(APP) apps/$(APP)
	@echo ""
	@echo "Next steps:"
	@echo "  1. Set name = 'apps.$(APP)' in apps/$(APP)/apps.py"
	@echo "  2. Add 'apps.$(APP)' to INSTALLED_APPS in settings/base.py"

shell:
	$(COMPOSE) exec backend uv run python manage.py shell

test:
	$(COMPOSE) exec backend uv run python manage.py test $(APP)

# ─── Dependencies ────────────────────────────────────────────────────────────
uv-add:
	@if [ -z "$(PKG)" ]; then \
		echo "Usage: make uv-add PKG=package_name"; \
		exit 1; \
	fi
	cd backend && uv add $(PKG)
	$(COMPOSE) build backend

# ─── Logs ────────────────────────────────────────────────────────────────────
logs:
	$(COMPOSE) logs -f

logs-back:
	$(COMPOSE) logs -f backend

logs-front:
	$(COMPOSE) logs -f frontend

logs-db:
	$(COMPOSE) logs -f db

# ─── Frontend ────────────────────────────────────────────────────────────────
lint:
	$(COMPOSE) exec frontend npm run lint

format:
	$(COMPOSE) exec frontend npm run format

# ─── Cleanup ─────────────────────────────────────────────────────────────────
clean:
	@echo "WARNING: This will delete ALL volumes including the database."
	@read -p "Are you sure? [y/N] " ans && [ "$$ans" = "y" ]
	$(COMPOSE) down -v

clean-db:
	@echo "WARNING: This will delete the database volume."
	@read -p "Are you sure? [y/N] " ans && [ "$$ans" = "y" ]
	$(COMPOSE) down -v --remove-orphans
	$(COMPOSE) up -d db
