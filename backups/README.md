Restore into a fresh empty DB:
```bash
docker exec -i leaderboardx-postgres-service-1 psql -U user -d leaderboardx-db < backups/leaderboardx-db.sql
```

If you want a clean reset first (drops all tables and data):

```bash
docker exec -i leaderboardx-postgres-service-1 psql -U user -d leaderboardx-db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker exec -i leaderboardx-postgres-service-1 psql -U user -d leaderboardx-db < backups/leaderboardx-db.sql
```