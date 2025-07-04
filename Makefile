# Makefile for the docu-researcher App

install:
	sudo uv pip install --system .
	npm --prefix frontend install concurrently --save-dev
	npm --prefix frontend audit fix --force
	

# New command for the one-time, interactive gcloud login.
# It uses the --no-browser flag to provide a copy-paste link.
first-time-setup:
	@echo "Logging into Google Cloud. Please follow the instructions."
	gcloud auth application-default login --no-browser

# Starts both backend and frontend development servers.
dev:
	npm --prefix frontend exec concurrently "make dev-backend" "make dev-frontend"

dev-backend:
	adk api_server app --allow_origins="*"

dev-frontend:
	npm --prefix frontend run dev

.PHONY: install first-time-setup dev dev-backend dev-frontend

playground:
	adk web --port 8501

lint:
	codespell
	ruff check . --diff
	ruff format . --check --diff
	mypy .