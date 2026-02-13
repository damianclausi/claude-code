.PHONY: start stop restart build logs clean migrate create-migration seed seed-fresh test help

# Usar 'docker compose' (v2) - compatible con Docker Desktop en WSL 2
# Si falla, asegúrate de tener Docker Desktop con integración WSL activada
COMPOSE = docker compose

# Comando principal para iniciar el entorno de desarrollo
start:
	$(COMPOSE) up -d

# Detener los contenedores
stop:
	$(COMPOSE) down

# Reiniciar los contenedores
restart:
	$(COMPOSE) restart

# Construir las imágenes
build:
	$(COMPOSE) build

# Ver los logs de los contenedores
logs:
	$(COMPOSE) logs -f

# Limpiar contenedores, volúmenes e imágenes
clean:
	$(COMPOSE) down -v --rmi all --remove-orphans

# Ejecutar migraciones de la base de datos
migrate:
	$(COMPOSE) exec api bash -c "cd /app && uv run alembic -c app/alembic.ini upgrade head"

# Crear una nueva migración
create-migration:
	@read -p "Ingrese el mensaje para la migración: " message; \
	$(COMPOSE) exec api bash -c "cd /app && uv run alembic -c app/alembic.ini revision --autogenerate -m \"$$message\""

# Ejecutar seed de datos
seed:
	$(COMPOSE) exec api bash -c "cd /app && uv run python -m app.db.seed"

# Limpiar y recrear datos de seed
seed-fresh:
	$(COMPOSE) exec api bash -c "cd /app && uv run python -m app.db.seed clear"
	$(COMPOSE) exec api bash -c "cd /app && uv run python -m app.db.seed"

# Ejecutar pruebas dentro del contenedor
test:
	$(COMPOSE) exec api bash -c "cd /app && uv run pytest app/tests/ -v"

# Mostrar ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make start             - Iniciar el entorno de desarrollo"
	@echo "  make stop              - Detener los contenedores"
	@echo "  make restart           - Reiniciar los contenedores"
	@echo "  make build             - Construir las imágenes"
	@echo "  make logs              - Ver logs de los contenedores"
	@echo "  make clean             - Limpiar contenedores y volúmenes"
	@echo "  make migrate           - Ejecutar migraciones de la base de datos"
	@echo "  make create-migration  - Crear una nueva migración"
	@echo "  make seed              - Ejecutar seed de datos"
	@echo "  make seed-fresh        - Limpiar y recrear datos de seed"
	@echo "  make test              - Ejecutar pruebas dentro del contenedor"
	@echo "  make help              - Mostrar esta ayuda"

# Comando por defecto
.DEFAULT_GOAL := help 