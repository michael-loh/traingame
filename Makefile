# The Train Game - Root Makefile

.PHONY: setup-backend setup-frontend setup backend frontend demo test build help

# Default command shows help
help:
	@echo "Available commands:"
	@echo "  make setup            - Install all dependencies (backend + frontend)"
	@echo "  make backend          - Start the FastAPI backend"
	@echo "  make frontend         - Start the Vite frontend"
	@echo "  make demo             - Open the frontend in Demo Mode"
	@echo "  make test             - Run backend engine tests"
	@echo "  make build            - Build the frontend for production"

# --- Setup Commands ---

setup: setup-backend setup-frontend

setup-backend:
	cd backend && python -m venv venv
	@echo "Backend venv created. Please install dependencies with: cd backend && .\\venv\\Scripts\\activate && pip install -r requirements.txt"

setup-frontend:
	cd frontend && npm install

# --- Run Commands ---

backend:
	cd backend && venv\Scripts\python -m uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

demo:
	@echo "Starting frontend... open http://localhost:5173/?demo=true in your browser"
	cd frontend && npm run dev

# --- Quality Commands ---

test:
	cd backend && venv\Scripts\python -m pytest

build:
	cd frontend && npm run build
