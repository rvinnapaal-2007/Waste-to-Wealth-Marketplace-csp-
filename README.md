# Waste to Wealth Marketplace (Flask + PostgreSQL + Docker)

## Option A: everything in Docker (easiest)
    docker compose up -d --build
Open http://localhost:5000  (admin: /admin, password in app.py, default `admin123`)
Stop with `docker compose down` (data is kept). Start again with `docker compose up -d`.

## Option B: database in Docker, Flask on your PC (good for editing code)
    docker compose up -d db
    pip install -r requirements.txt
    python app.py
Open http://127.0.0.1:5000

## pgAdmin 4 connection
Host `localhost`, Port `5433`, Username `postgres`, Password `Admin`, database `agri_marketplace`.
Tables: Servers > agri_marketplace > Schemas > public > Tables > right-click `listings` > View/Edit Data > All Rows.

## Files
- app.py: backend (routes, validation, PostgreSQL code, JSON API, admin)
- templates/, static/: pages and styling
- Dockerfile: builds the Flask app image
- docker-compose.yml: runs the PostgreSQL database (db) and the Flask app (web)
- API: /api/listings, /api/stats

## Accounts
- Farmers and buyers sign up separately (/signup/farmer, /signup/buyer). Data is saved in the `farmers` and `buyers` tables; passwords are stored as hashes.
- Farmers get a dashboard to publish listings and see buyer requests. Buyers can contact farmers only when logged in, and see their sent requests with the farmer's phone.
- After updating an existing install run: docker compose up -d --build (new tables and columns are created automatically; old listings are kept).
