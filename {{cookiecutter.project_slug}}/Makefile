# Makefile
.PHONY: help up down build rebuild migrate mm superuser startapp shell logs-db logs-back logs-front clean clean-db

# Default target
help:
	@echo "Available commands:"
	@echo "  make up          - Start all containers"
	@echo "  make down        - Stop all containers"
	@echo "  make build       - Build backend and frontend images"
	@echo "  make rebuild     - Rebuild with no cache"
	@echo "  make migrate     - Run Django migrations"
	@echo "  make mm          - Make migrations (makemigrations)"
	@echo "  make superuser   - Create Django superuser"
	@echo "  make startapp APP=name - Create a new Django app inside apps/"
	@echo "  make shell       - Open Django shell"
	@echo "  make logs-back   - Tail backend logs"
	@echo "  make logs-front  - Tail frontend logs"
	@echo "  make logs-db     - Tail database logs"
	@echo "  make clean       - Stop containers and remove volumes (data loss!)"
	@echo "  make clean-db    - Remove only the database volume"

up:
	podman-compose up

down:
	podman-compose down

build:
	podman-compose build

rebuild:
	podman-compose build --no-cache

migrate:
	podman-compose exec backend uv run python manage.py migrate

mm:
	podman-compose exec backend uv run python manage.py makemigrations

superuser:
	podman-compose exec backend uv run python manage.py createsuperuser

# Create a new app inside apps/ (usage: make startapp APP=products)
startapp:
	@if [ -z "$(APP)" ]; then \
		echo "Usage: make startapp APP=app_name"; \
		exit 1; \
	fi
	podman-compose exec backend uv run python manage.py startapp $(APP) apps/$(APP)

shell:
	podman-compose exec backend uv run python manage.py shell

logs-back:
	podman-compose logs -f backend

logs-front:
	podman-compose logs -f frontend

logs-db:
	podman-compose logs -f db

clean:
	podman-compose down -v

clean-db:
	podman volume rm elana_postgres_data 2>/dev/null || echo "No volume found"