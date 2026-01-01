# Studio Guide (Company Dashboard)

This backend exposes a minimal studio dashboard plus studio APIs for managing games and leaderboards.

## Studio Dashboard (HTML)
- URL: `STUDIO_DASHBOARD_PATH` (default: `/__studio`)
- Login uses `company_id` + `company_secret` created via the API.

## Studio API Flow
1) Create a company:
```http
POST /api/v1/studio/companies
Content-Type: application/json

{ "name": "Nebula Forge" }
```
Response contains `company_id` and `company_secret`.

2) Create a game:
```http
POST /api/v1/studio/games
Content-Type: application/json

{
  "company_id": "<company_id>",
  "company_secret": "<company_secret>",
  "name": "Star Drift"
}
```

3) Create a leaderboard:
```http
POST /api/v1/studio/leaderboards
Content-Type: application/json

{
  "company_id": "<company_id>",
  "company_secret": "<company_secret>",
  "game_id": "<game_id>",
  "leaderboard_id": "global",
  "name": "Global High Scores",
  "sort_order": "desc"
}
```

4) Fetch a company summary (games + leaderboards):
```http
GET /api/v1/studio/company?company_id=<company_id>&company_secret=<company_secret>
```

Notes:
- `company_secret` is the only auth mechanism for studio APIs right now.
- `leaderboard_id` must be `[A-Za-z0-9-]` and unique per game.
