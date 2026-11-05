# Workshop Parts Desk – Backend (Part A)

FastAPI backend for the dashboard: request management, decision history, Groq connection
status, and an **advisory** analysis assistant.

> **Competition status:** the official Workshop Parts Desk protocol (actions, observations,
> scoring) is **pending**. Nothing here is the official agent. The official agent will be built
> in `competition/solution.py` once the problem statement is provided.

## Setup (Windows PowerShell, from the `backend` folder)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env        # fill in TEAM_PROVIDER_KEY and TEAM_MODEL yourself
```

If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Run

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try the API.

## Tests

```powershell
python -m pytest -v
```

Tests use a fake Groq transport, so they need no API key and no internet.

## Picking a Groq model

Start the server, then open http://127.0.0.1:8000/api/provider/models (needs only the key in `.env`).
Copy one id into `TEAM_MODEL` in `.env` and restart. `/api/provider/status` tells you if it works.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | /api/health | Server alive |
| GET | /api/provider/status | Groq key/model check |
| GET | /api/provider/models | Models available to your key |
| POST/GET | /api/requests | Create / list (`?status=` `?search=`) |
| GET/DELETE | /api/requests/{id} | Detail with history / delete |
| PATCH | /api/requests/{id}/status | Operator status change |
| POST | /api/requests/{id}/analyze | Advisory analysis (rules + Groq) |
| GET | /api/decisions | History (`?request_id=`) |
| GET | /api/stats | Counts by status |
| GET | /api/agent/status | Activity + competition agent state |

## Design notes

- The API key is read only in `app/config.py` and used only in `app/services/groq_service.py`.
  Logs and error messages pass through a redaction filter.
- Deterministic checks (`agents/decision_engine.py`) always override the model; model output is
  validated and unknown outcomes fall back to `needs_human_review`.
- Statuses (`pending`, `needs_clarification`, `completed`, `escalated`) are dashboard labels,
  **not** official competition actions.
