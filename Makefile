.DEFAULT_GOAL := help
SHELL := /bin/bash

BACKEND_DIR   := backend
FRONTEND_DIR  := frontend
PY            := python3
PIP           := $(PY) -m pip
PYTEST        := $(PY) -m pytest COMPOSE       := docker compose  .PHONY: help help:  ## Mostra esta ajuda 	@grep -E '^[a-zA-Z_-]+:.*?## .*$$'$(MAKEFILE_LIST) 

| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1,$$2}'

.PHONY: install
install:  ## Instala dependências backend + frontend
$(PIP) install --upgrade pip
$(PIP) install -r$(BACKEND_DIR)/requirements.txt
$(PIP) install -r$(FRONTEND_DIR)/requirements.txt

.PHONY: env
env:  ## Cria .env a partir do exemplo
@test -f .env || cp .env.example .env
@echo "Criado .env — ajuste os valores antes de rodar."

.PHONY: test
test:  ## Pytest com cobertura
$(PYTEST) $(BACKEND_DIR)/tests --cov=$(BACKEND_DIR)/app --cov-report=term-missing --cov-fail-under=80 -v

.PHONY: up
up:  ## Sobe a stack via docker compose
$(COMPOSE) up --build -d