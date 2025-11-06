SHELL := /usr/bin/env bash
# Developer workflow Makefile (portable: Linux/macOS/WSL/Git Bash)
# Usage: make <target>

# ---------------------
# Variables & Defaults (override: make VAR=value target)
# ---------------------
PYTHON ?= python3
RUFF ?= ruff
BLACK ?= black
MYPY ?= mypy
PYTEST ?= pytest
UVICORN ?= uvicorn
APP_MODULE ?= app.main:app
HOST ?= 127.0.0.1
PORT ?= 8000
ALEMBIC ?= alembic
ALEMBIC_INI ?= alembic.ini
AL_OPTS := $(if $(wildcard $(ALEMBIC_INI)),-c $(ALEMBIC_INI),)
DB_SERVICE ?= postgres

# Compose binary + file detection
DOCKER_COMPOSE := $(shell command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && echo "docker compose" || (command -v docker-compose >/dev/null 2>&1 && echo docker-compose))
DOCKER_COMPOSE_FILE := $(firstword $(wildcard docker-compose.yml docker-compose.yaml compose.yml compose.yaml))

# Virtual environment detection
VENV_DIR ?= .venv
VENV_ACTIVATE := $(VENV_DIR)/bin/activate
VENV_ACTIVATE_WIN := $(VENV_DIR)/Scripts/activate

.DEFAULT_GOAL := help

.PHONY: help dev db db-logs db-stop db-down shell venv lint format typecheck test coverage migrate revision downgrade current heads stamp prune

help: ## List available targets and examples (no commands executed)
	@echo "Available targets:" && \
	printf "\nDevelopment:\n  venv      - Create .venv virtual environment\n  shell     - Activate .venv and open interactive subshell\n  dev       - Run API with reload (uvicorn)\n  db        - Start dev DB via compose (service=$(DB_SERVICE))\n" && \
	printf "\nCode quality:\n  lint      - Ruff + Black (check)\n  format    - Black (write)\n  typecheck - mypy (if installed)\n  test      - Pytest (-q)\n" && \
	printf "\nDatabase & migrations:\n  migrate   - Alembic upgrade head\n  revision  - Alembic revision (m=\"msg\")\n  downgrade - Alembic downgrade -1\n  current   - Alembic current\n" && \
	printf "\nDocker / cleanup:\n  prune     - Safe docker prune (images/containers/networks)\n" && \
	printf "\nExamples:\n  make venv\n  make shell\n  make dev PORT=9000\n  make revision m=\"add note index\"\n"

# ---------------------
# Development
# ---------------------

venv: ## Create a local Python virtual environment in .venv
	@if [ -d "$(VENV_DIR)" ]; then echo ".venv already exists"; else $(PYTHON) -m venv $(VENV_DIR) && echo ".venv created"; fi

shell: ## Activate .venv and open interactive subshell
	@if [ -f "$(VENV_ACTIVATE)" ]; then \
		echo "Activating Unix venv: $(VENV_ACTIVATE)"; \
		source $(VENV_ACTIVATE); exec bash -i; \
	elif [ -f "$(VENV_ACTIVATE_WIN)" ]; then \
		echo "Activating Windows venv: $(VENV_ACTIVATE_WIN)"; \
		source $(VENV_ACTIVATE_WIN); exec bash -i; \
	else \
		echo ".venv missing. Create it with: $(PYTHON) -m venv .venv"; exit 1; \
	fi

dev: ## Run FastAPI app locally (reload)
	@echo "Starting API (reload) on $(HOST):$(PORT) module=$(APP_MODULE)..." && \
	$(PYTHON) -m $(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

db: ## Start local DB via compose (override: make db DB_SERVICE=your_service)
ifeq ($(DOCKER_COMPOSE),)
	@echo "docker compose binary not found. Install Docker Desktop or docker-compose."
else ifeq ($(DOCKER_COMPOSE_FILE),)
	@echo "No compose file (docker-compose.yml/.yaml or compose.yml/.yaml) found. Skipping."
else
	@echo "Starting service $(DB_SERVICE) using $(DOCKER_COMPOSE_FILE)..." && \
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d $(DB_SERVICE) || \
	(echo "Service '$(DB_SERVICE)' not found. Override with: make db DB_SERVICE=<service>"; exit 1)
endif

db-logs: ## Tail DB logs via compose
	@if [ -n "$(DOCKER_COMPOSE_FILE)" ] && [ -n "$(DOCKER_COMPOSE)" ]; then \
	  $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f $(DB_SERVICE); \
	else echo "Compose not detected."; fi

db-stop: ## Stop only the DB service
	@if [ -n "$(DOCKER_COMPOSE_FILE)" ] && [ -n "$(DOCKER_COMPOSE)" ]; then \
	  $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) stop $(DB_SERVICE); \
	else echo "Compose not detected."; fi

db-down: ## Bring down DB service (no volumes)
	@if [ -n "$(DOCKER_COMPOSE_FILE)" ] && [ -n "$(DOCKER_COMPOSE)" ]; then \
	  $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down; \
	else echo "Compose not detected."; fi

# ---------------------
# Code Quality
# ---------------------

lint: ## Run ruff + black (check mode)
	@echo "Running ruff..." && \
	$(PYTHON) -m $(RUFF) check . && \
	echo "Running black (check)..." && \
	$(PYTHON) -m $(BLACK) --check .

format: ## Format with black
	@echo "Formatting with black..." && \
	$(PYTHON) -m $(BLACK) .

typecheck: ## Run mypy if installed (skip gracefully if missing)
	@echo "Typechecking..." && \
	(command -v $(MYPY) >/dev/null 2>&1 && $(PYTHON) -m $(MYPY) . || echo "mypy not installed; skipping. Install with: pip install mypy")

test: ## Run pytest quietly
	@echo "Running tests..." && \
	$(PYTHON) -m $(PYTEST) -q

coverage: ## Run tests with coverage and HTML report
	@$(PYTHON) -m $(PYTEST) --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing --cov-report=html

# ---------------------
# Database & Migrations
# ---------------------

migrate: ## Apply all migrations (upgrade head)
	@echo "Upgrading database schema to head..." && \
	$(ALEMBIC) $(AL_OPTS) upgrade head

revision: ## Create a new migration revision (usage: make revision m="message")
	# Example: make revision m="add users table"
	@if [ -z "$(m)" ]; then echo "Missing message. Usage: make revision m=\"add users table\""; exit 1; fi; \
	echo "Creating revision: $(m)" && \
	$(ALEMBIC) $(AL_OPTS) revision --autogenerate -m "$(m)"

downgrade: ## Downgrade one migration step (-1)
	@echo "Downgrading schema by one revision..." && \
	$(ALEMBIC) $(AL_OPTS) downgrade -1

current: ## Show current Alembic revision
	@$(ALEMBIC) $(AL_OPTS) current

heads: ## Show Alembic heads
	@$(ALEMBIC) $(AL_OPTS) heads

stamp: ## Stamp DB to head without migrations (requires rev=<revision|head>)
	# Example: make stamp rev=head
	@if [ -z "$(rev)" ]; then echo "Usage: make stamp rev=head"; exit 2; fi; \
	$(ALEMBIC) $(AL_OPTS) stamp $(rev)

# ---------------------
# Docker / Cleanup
# ---------------------

prune: ## Safe docker cleanup (dangling images, stopped containers, unused networks)
	@echo "Docker disk usage before:" && docker system df && \
	echo "Pruning dangling images..." && docker image prune -f && \
	echo "Pruning stopped containers..." && docker container prune -f && \
	echo "Pruning unused networks..." && docker network prune -f && \
	echo "(Skipping volumes - destructive)" && \
	echo "Docker disk usage after:" && docker system df

# End of Makefile
