# Studio Guide (Company Dashboard)

Minimal studio dashboard + APIs for managing games and leaderboards.

## Dashboard (HTML)
- Base path: `STUDIO_DASHBOARD_PATH` (default `/__studio`)
- Register or log in with **username** (`a-z, 0-9, '-'`) and password.
- Sessions last 1 month. There is **no password recovery**; email the developer for manual help.

## API Flow
1) Register a company (creates login):
```http
POST /api/v1/studio/companies
Content-Type: application/json
{
  "name": "Nebula Forge",
  "username": "nebula-forge",
  "password": "secret123"
}
```
Response: `company_id`, `company_secret`, `username`.

2) Create a game/app:
```http
POST /api/v1/studio/games
{
  "company_id": "<company_id>",
  "company_secret": "<company_secret>",
  "name": "Star Drift"
}
```

3) Create a leaderboard:
```http
POST /api/v1/studio/leaderboards
{
  "company_id": "<company_id>",
  "company_secret": "<company_secret>",
  "game_id": "<game_id>",
  "leaderboard_id": "global",
  "name": "Global High Scores",
  "sort_order": "desc"
}
```

4) Dashboard features
- Overview: list apps and open an app dashboard.
- App dashboard: leaderboard summary, total players, filtered score counts, device search (by `device_id`), manual refresh (not realtime).

Notes:
- `leaderboard_id` must be `[A-Za-z0-9-]` and unique per game.
- `company_secret` still secures the studio APIs; the dashboard uses username/password.
