# The Train Game

A high-performance, real-time board game clone ("Ticket to Ride"), built with **FastAPI**, **React (Vite)**, and **TypeScript**.

## 🚀 Quick Start (Demo Mode)
To view the UI with mock data without setting up the backend:
1.  **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
2.  **Open:** `http://localhost:5173/?demo=true`

---

## 🛠️ Full Development Setup

### 1. Backend (FastAPI)
1.  **Navigate to backend:**
    ```bash
    cd backend
    ```
2.  **Create & Activate venv:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    *   **API:** `http://localhost:8000`

### 2. Frontend (React + Vite)
1.  **Navigate & Install:**
    ```bash
    cd frontend
    npm install
    ```
2.  **Run Dev Server:**
    ```bash
    npm run dev
    ```
    *   **URL:** `http://localhost:5173`

---

## 🎮 Gameplay Features
*   **Real-Time Sync**: WebSockets for instant state updates across all players.
*   **Modern Minimalist UI**: A sleek, high-fidelity schematic board with rich animations.
*   **Fog of War**: Backend sanitizes state to hide opponent hands and deck contents.
*   **Rule Engine**: Handles deck management, route claiming, and scoring algorithms.

## 🧪 Testing
### Backend
Run `pytest` inside the `backend/` directory with an activated virtual environment:
```bash
cd backend
python -m pytest
```

### Frontend
Check for type errors and linting:
```bash
cd frontend
npm run build
```

## 🛠️ Documentation
*   [AGENTS.md](backend/AGENTS.md): Essential guidelines and setup for AI/human contributors.
*   [Game Plan](train_game_plan.md): Architectural and logic overview.
