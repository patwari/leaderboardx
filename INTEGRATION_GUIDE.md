# Client Integration Guide

This service uses simple client APIs for score submission and leaderboard fetch.

## Prerequisites
- Create a company, game, and leaderboard (see `STUDIO_GUIDE.md`).
- You need: `game_id` and `leaderboard_id`.

## 1) Authenticate a device
```http
POST /api/v1/client/auth
Content-Type: application/json

{ "game_id": "<game_id>", "device_id": "device-abc123" }
```
Response gives a stable `xid` (player identity) for that device.

## 2) Submit a score
```http
POST /api/v1/client/score
Content-Type: application/json

{
  "game_id": "<game_id>",
  "xid": "<xid>",
  "leaderboard_id": "global",
  "value": 9820
}
```
Response includes `best_value` and whether the leaderboard entry was updated.

## 3) Fetch a leaderboard
```http
GET /api/v1/client/leaderboard?game_id=<game_id>&leaderboard_id=global&limit=50&offset=0
```
Optional: add `&xid=<xid>` to return the caller's rank in the response.

## Notes
- `device_id` and `leaderboard_id` must be `[A-Za-z0-9-]`.
- `value` is an integer score; sorting uses the leaderboard `sort_order`.
- Client APIs do not require API keys yet (auth will be added later).
