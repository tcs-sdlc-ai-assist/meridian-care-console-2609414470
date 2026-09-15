# Meridian Care Console

Private, synthetic-data internal care-management demo for coordinators, supervisors, and auditors.

## Demo accounts
All accounts use `DemoPass123!`: `coordinator@meridian.example.com`, `supervisor@meridian.example.com`, and `auditor@meridian.example.com`.

## Local development
Backend: `cd backend && python3 -m venv --copies $HOME/venvs/meridian && $HOME/venvs/meridian/bin/pip install -r requirements.txt && $HOME/venvs/meridian/bin/python -m uvicorn app.main:app --port 8000`.

Frontend: `cd frontend && npm install && node node_modules/vite/bin/vite.js`.

The frontend calls same-origin `/api` in deployed builds; Vite proxies `/api` to FastAPI locally. SQLite persists at `/tmp/meridian/app.db`; no database service is required.

## Test and build
- Backend: `cd backend && PYTHONPATH=. $HOME/venvs/meridian/bin/python -m pytest -q`
- Frontend: `cd frontend && node node_modules/vitest/vitest.mjs run`
- Build: `cd frontend && node node_modules/vite/bin/vite.js build`
- Containers: `docker compose up --build -d`

FastAPI health: `GET /api/health` (port 8000). Frontend nginx health: `GET /healthz` (port 8080).

## License
Private and proprietary. All included records are synthetic demo data only.
