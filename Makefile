.PHONY: install dev build test lint clean help

# Colors
CYAN := \033[36m
RESET := \033[0m

help: ## Show this help message
	@echo "NeoGravity Core - Elite Infrastructure Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-15s$(RESET) %s\n", $$1, $$2}'

install: ## Setup PNPM workspace AND Python virtual environments
	@echo "1. Installing Node dependencies via PNPM..."
	pnpm install
	@echo "2. Bootstrapping Python backend (.venv)..."
	python -m venv packages/sovereign-memory/.venv
	packages/sovereign-memory/.venv/Scripts/pip install -r packages/sovereign-memory/requirements.txt
	@echo "$(CYAN)Installation complete.$(RESET)"

dev: ## Start Turborepo watcher for local development
	pnpm run dev

build: ## Build all packages via Turborepo
	pnpm run build

test: ## Run tests across all packages
	pnpm run test

lint: ## Run linters across all packages
	pnpm run lint

clean: ## Remove node_modules, .venvs, and build artifacts
	@echo "Cleaning repository..."
	rm -rf node_modules
	rm -rf packages/*/node_modules
	rm -rf packages/sovereign-memory/.venv
	rm -rf packages/sovereign-memory/__pycache__
	@echo "$(CYAN)Clean complete.$(RESET)"
