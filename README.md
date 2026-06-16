# KPAstroGem MVP

KPAstroGem is a local-first MVP for a KP astrology web application. This repository contains:

- `frontend/`: Next.js + React + TypeScript + Tailwind UI
- `backend/`: FastAPI API with temporary chart sessions and structured placeholder KP responses

This version is intentionally a placeholder MVP. It does not claim final astrological accuracy and includes clear `TODO` markers where real KP calculations will later be implemented.

## Project Structure

```text
KPAstroGem/
  frontend/
  backend/
  README.md
```

## Current Status

- Multi-page frontend flow is scaffolded
- Temporary chart-session API contract is wired end to end
- Placeholder KP chart and question-answer responses are implemented
- Local install commands have not been run yet

## Prerequisites

Install these on Windows before running the app:

- Node.js LTS
- Python 3.11 or 3.12

After installing, confirm the tools are available:

```powershell
node -v
npm -v
python --version
pip --version
```

If `python` does not resolve on your machine, use the Windows Python launcher:

```powershell
py --version
```

## Backend Setup

Open PowerShell in the project root and run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If your system uses the Python launcher instead of `python`, use:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "kp-astro-backend"
}
```

## Frontend Setup

Open a second PowerShell window in the project root and run:

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm install
npm run dev
```

The frontend runs at:

- [http://localhost:3000](http://localhost:3000)

## Frontend Environment

The frontend expects this environment variable in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The included `.env.local.example` already uses the default local backend URL.

## How to Run Locally

1. Start the backend from `backend/`
2. Start the frontend from `frontend/`
3. Open [http://localhost:3000](http://localhost:3000)
4. Create a chart session from `/birth-details`
5. Review the dashboard and ask a question from the session-specific route

## Sample Test Profile

Use this profile for the first manual test:

- Name: Pradeep
- Date of birth: 1988-12-09
- Time of birth: 18:30
- Birth place: Secunderabad
- Country: India
- Question category: Career
- Question: How is my career growth?

## API Contract

### `GET /health`

Returns a small status payload for startup checks.

### `POST /api/charts/calculate`

Accepts:

```json
{
  "name": "Pradeep",
  "dateOfBirth": "1988-12-09",
  "timeOfBirth": "18:30",
  "birthPlace": "Secunderabad",
  "state": "Telangana",
  "country": "India",
  "timezone": "Asia/Kolkata",
  "questionCategory": "Career",
  "question": "How is my career growth?"
}
```

Returns:

- `chartId`
- `chart`

The `chart` contains:

- Birth summary
- Planetary positions
- House cusps
- Star lord
- Sub lord
- Dasha summary
- KP-style interpretation
- Confidence level
- Disclaimer

### `GET /api/charts/{chart_id}`

Returns the temporary chart session, including:

- `chartId`
- `createdAt`
- `expiresAt`
- `chartData`
- `questionHistory`

### `POST /api/questions/ask`

Accepts:

```json
{
  "chartId": "your-chart-id",
  "question": "How is my career growth?",
  "optionalDateRange": "Second half of 2026"
}
```

Returns structured placeholder question analysis including:

- Classified topic
- Relevant houses
- Cusp sub lord analysis
- Significator analysis
- Dasha support
- Supporting and blocking factors
- KP-based interpretation
- Possible timing window
- Calculation trail
- Disclaimer

## Suggested Local Checks

Run these after dependencies are installed:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m compileall app
```

```powershell
cd frontend
npm run lint
npm run build
```

## Notes

- No login, database, payments, or deployment are included yet
- No scraping or AstroSage integration is used
- Install commands should only be run in this Codex session after your approval
- Real KP calculations are still pending and marked with `TODO` comments in the backend
