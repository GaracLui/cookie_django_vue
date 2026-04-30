# Makefile
.PHONY: help up down build rebuild migrate mm superuser startapp shell logs-db logs-back logs-front clean clean-db

# Default target
help:
	@echo "Available commands:"
	@echo "  make up         	- Start all containers in a detached terminal"
	@echo "  make dev         	- Start all containers in a detached terminal "
	@echo "  make logs	  	- "
	@echo "  make down        	- Stop all containers"
	@echo "  make build       	- Build backend and frontend images"
	@echo "  make rebuild     	- Rebuild with no cache"
	@echo "  make migrate     	- Run Django migrations"
	@echo "  make mm          	- Make migrations (makemigrations)"
	@echo "  make superuser   	- Create Django superuser"
	@echo "  make startapp APP=name - Create a new Django app inside apps/"
	@echo "  make shell       	- Open Django shell"
	@echo "  make test        	- "
	@echo "  make clean       	- Stop containers and remove volumes (data loss!)"
	@echo "  make clean-db    	- Remove only the database volume"

up:
	podman-compose up -d
	
dev:
    	podman-compose up -d --build

logs:
	podman-compose logs -f

down:
	podman-compose down

build:
	podman-compose build

rebuild:
	podman-compose build --no-cache

migrate:
	podman-compose exec backend uv run python manage.py migrate

mm:
    	podman-compose exec backend uv run python manage.py makemigrations $(APP)

superuser:
	podman-compose exec backend uv run python manage.py createsuperuser

# Create a new app inside apps/ (usage: make startapp APP=products)
startapp:
	@if [ -z "$(APP)" ]; then \
	echo "Usage: make startapp APP=app_name"; \
	exit 1; \
	fi
	podman-compose exec backend uv run python manage.py startapp $(APP) apps/$(APP)
	@echo "IMPORTANT: Set name = 'apps.$(APP)' in apps/$(APP)/apps.py"
	@echo "Then add 'apps.$(APP)' to INSTALLED_APPS in settings."

shell:
	podman-compose exec backend uv run python manage.py shell

test:
    	podman-compose exec backend uv run python manage.py test

clean:
    	@echo "WARNING: This will delete ALL volumes including the database."
    	@read -p "Are you sure? [y/N] " ans && [ "$$ans" = "y" ]
    	podman-compose down -v

clean-db:
	@echo "WARNING: This will delete the database volume."
	@read -p "Are you sure? [y/N] " ans && [ "$$ans" = "y" ]
	podman-compose down -v --remove-orphans
	podman-compose up -d db

lint:
	podman-compose exec frontend npm run lint

format:
	podman-compose exec frontend npm run format
