# E-commerce Digital Marketing Intelligence Platform

A full-stack portfolio project for tracking e-commerce marketing campaigns and organizing SEO keyword research.

## Stack
- Frontend: React, TypeScript, Vite, Lucide
- Backend: Python, FastAPI, SQLAlchemy
- Database: PostgreSQL (SQLite fallback for local development)

## Features
- Marketing overview dashboard with spend, revenue, clicks, impressions, conversions, CTR and ROAS
- Campaign management for Google Ads, Meta Ads, SEO and email marketing
- Automatic CTR, CPC, CPA and ROAS calculations
- SEO keyword portfolio with search volume, difficulty, ranking position and target URL
- CSV export of campaign performance
- Responsive dashboard layout
- REST API and health-check endpoint

## Local setup

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API: http://localhost:8000  
API docs: http://localhost:8000/docs

Without DATABASE_URL, the backend uses a local SQLite database file. For PostgreSQL, set DATABASE_URL to your database connection string.

### Frontend
```bash
cd frontend
npm install
# Create .env and set VITE_API_URL=http://localhost:8000
npm run dev
```

## Deploy with Render
This repository includes a `render.yaml` blueprint for the API, frontend static site and PostgreSQL database. In Render, choose **New → Blueprint**, connect this repository, review the services and deploy. After provisioning, check the API health endpoint and the frontend URL.

For a manually created API service, use:
- Runtime: Python
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/healthz`

For the frontend static site:
- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Environment variable: `VITE_API_URL` = deployed API URL

## Metric formulas
- CTR = clicks / impressions × 100
- CPC = spend / clicks
- CPA = spend / conversions
- ROAS = revenue / spend

Metrics are based on values entered by the user. This project does not connect directly to Google Ads, Meta Ads, Google Analytics or Search Console APIs. Keyword search volumes and ranking positions are manually entered; they are not fetched from live search providers.

## Notes
This is a learning/portfolio MVP. Before public production use, restrict CORS to the frontend domain, add authentication and authorization, input/rate limits, database migrations, audit logging and secure secrets management.
