{"company_id":"1959249d-ee7f-4928-b422-c62911c2d235","company_secret":"UTty0ryDpdiZeMyJdACplpWpOSH6x09xdYlNk3NRirA","name":"Indie Owl Studios"}%

curl -X POST http://localhost:8000/api/v1/studio/games \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "1959249d-ee7f-4928-b422-c62911c2d235",
    "company_secret": "UTty0ryDpdiZeMyJdACplpWpOSH6x09xdYlNk3NRirA",
    "name": "Space Runner"
  }'
{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","game_secret":"v6glKsSCb4OM4q50DS5_WIjeyJ72WxXmjqxRAsWzUls","company_id":"1959249d-ee7f-4928-b422-c62911c2d235","name":"Space Runner"}%


--------

curl -X POST http://localhost:8000/api/v1/studio/leaderboards \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "1959249d-ee7f-4928-b422-c62911c2d235",
    "company_secret": "UTty0ryDpdiZeMyJdACplpWpOSH6x09xdYlNk3NRirA",
    "game_id": "5cda18a8-dca3-4b97-a2dc-37849821570d",
    "leaderboard_id": "global-highscore",
    "sort_order": "desc"
  }'
{"leaderboard_pk":"49037692-481e-4525-b071-69964f86e9f3","game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","leaderboard_id":"global-highscore","name":null,"sort_order":"desc"}%

-----

curl -X POST http://localhost:8000/api/v1/client/auth \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "5cda18a8-dca3-4b97-a2dc-37849821570d",
    "device_id": "DEVICE-ABC-001"
  }'

{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","xid":"6c6f770b-1bb7-4e75-90a9-cb95e311c336","is_new":true}%

-----

curl -X POST http://localhost:8000/api/v1/client/score \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "5cda18a8-dca3-4b97-a2dc-37849821570d",
    "xid": "6c6f770b-1bb7-4e75-90a9-cb95e311c336",
    "leaderboard_id": "global-highscore",
    "value": 1200
  }'

{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","leaderboard_id":"global-highscore","xid":"6c6f770b-1bb7-4e75-90a9-cb95e311c336","best_value":1200,"updated":true}%                                                                   

-----

curl -X POST http://localhost:8000/api/v1/client/auth \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "5cda18a8-dca3-4b97-a2dc-37849821570d",
    "device_id": "DEVICE-XYZ-777"
  }'
{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","xid":"e06992cc-7f0f-4ff0-843a-363e0c4e62fa","is_new":true}%      

-----

curl -X POST http://localhost:8000/api/v1/client/score \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "5cda18a8-dca3-4b97-a2dc-37849821570d",
    "xid": "e06992cc-7f0f-4ff0-843a-363e0c4e62fa",
    "leaderboard_id": "global-highscore",
    "value": 1750
  }'

{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","leaderboard_id":"global-highscore","xid":"e06992cc-7f0f-4ff0-843a-363e0c4e62fa","best_value":1750,"updated":true}%

------

curl "http://localhost:8000/api/v1/client/leaderboard?game_id=5cda18a8-dca3-4b97-a2dc-37849821570d&leaderboard_id=global-highscore&limit=10"

{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","leaderboard_id":"global-highscore","sort_order":"desc","total":2,"entries":[{"rank":1,"xid":"6c6f770b-1bb7-4e75-90a9-cb95e311c336","best_value":1800,"updated_at":"2026-01-01T13:13:05.362440+00:00"},{"rank":2,"xid":"e06992cc-7f0f-4ff0-843a-363e0c4e62fa","best_value":1750,"updated_at":"2026-01-01T13:13:54.909995+00:00"}],"your_rank":null,"your_best_value":null}%


------

curl "http://localhost:8000/api/v1/client/leaderboard?game_id=5cda18a8-dca3-4b97-a2dc-37849821570d&leaderboard_id=global-highscore&limit=10&xid=e06992cc-7f0f-4ff0-843a-363e0c4e62fa"

{"game_id":"5cda18a8-dca3-4b97-a2dc-37849821570d","leaderboard_id":"global-highscore","sort_order":"desc","total":2,"entries":[{"rank":1,"xid":"6c6f770b-1bb7-4e75-90a9-cb95e311c336","best_value":1800,"updated_at":"2026-01-01T13:13:05.362440+00:00"},{"rank":2,"xid":"e06992cc-7f0f-4ff0-843a-363e0c4e62fa","best_value":1750,"updated_at":"2026-01-01T13:13:54.909995+00:00"}],"your_rank":2,"your_best_value":1750}%

------



------