# Testing Guide

## Phase 1: Test Scraper Service

### Start the Test Environment

```bash
cd /git/ignition-exchange-scraper-v3/docker
docker compose up -d
```

This starts:
- PostgreSQL database (initialized with schema)
- Ignition 8.3 Gateway
- Scraper service

### Verify Services

```bash
# Check all containers are running
docker compose ps

# Should see:
# - exchange-scraper-postgres (healthy)
# - exchange-scraper-ignition (healthy)
# - exchange-scraper-service (running)

# Check logs
docker compose logs scraper-service

# Should see:
# "Starting Exchange Scraper Service..."
# "Service started successfully"
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","timestamp":"...","version":"3.0.0"}

# Get current status
curl http://localhost:5000/api/scrape/status

# Should return:
# {"status":"idle","job_id":null,"progress":...}
```

### Run a Test Scrape

```bash
# Start scraping
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"triggered_by":"manual"}'

# Should return:
# {"success":true,"message":"Scrape started","triggered_by":"manual"}

# Monitor progress
curl http://localhost:5000/api/scrape/status

# Watch logs in real-time
docker compose logs -f scraper-service

# You should see:
# - "Loading all resources by clicking 'Load more'..."
# - Progress updates as resources are scraped
# - "✓ Scraped: [Resource Name] (v1.0.0)"
```

**Note:** A full scrape takes 30-60 minutes depending on the number of resources.

### Test Control Endpoints

```bash
# Pause the scrape
curl -X POST http://localhost:5000/api/scrape/control \
  -H "Content-Type: application/json" \
  -d '{"action":"pause"}'

# Resume
curl -X POST http://localhost:5000/api/scrape/control \
  -H "Content-Type: application/json" \
  -d '{"action":"resume"}'

# Stop
curl -X POST http://localhost:5000/api/scrape/control \
  -H "Content-Type: application/json" \
  -d '{"action":"stop"}'
```

### Check Results in Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U ignition -d exchange_scraper

# View latest results
SELECT * FROM vw_latest_results LIMIT 10;

# View recent jobs
SELECT * FROM vw_recent_jobs;

# View latest changes
SELECT * FROM vw_latest_changes;

# Exit psql
\q
```

### API Endpoints Reference

#### Health & Status
- `GET /health` - Health check
- `GET /api/scrape/status` - Current scraper status

#### Control
- `POST /api/scrape/start` - Start new scrape
- `POST /api/scrape/control` - Pause/resume/stop

#### Data Retrieval
- `GET /api/results/latest` - Latest scrape results
- `GET /api/results/changes` - Changes from latest scrape
- `GET /api/jobs/recent?limit=10` - Recent job history
- `GET /api/logs/recent?limit=50` - Recent activity logs
- `GET /api/stats` - Statistics

#### Maintenance
- `POST /api/logs/clear` - Clear old logs

### Expected First Run Results

After a successful first scrape, you should see:
- **400+ resources** found and stored
- **All marked as "new"** (change_type = 'new')
- **Job status: completed**
- **No errors** in activity log

### Troubleshooting

**Service won't start:**
```bash
docker compose logs scraper-service
# Look for import errors or connection issues
```

**Database connection error:**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check database exists
docker compose exec postgres psql -U ignition -l
```

**Scrape fails/times out:**
```bash
# Check logs for specific errors
docker compose logs scraper-service | grep ERROR

# Common issues:
# - Network connectivity
# - Playwright browser not installed
# - Website blocking bot
```

**Playwright browser missing:**
```bash
# Rebuild with --no-cache
docker compose build --no-cache scraper-service
docker compose up -d
```

## Phase 2: Test Ignition Integration

*(To be added after Perspective dashboard is built)*

### Configure Database Connection in Ignition

1. Open Ignition Gateway: http://localhost:8088
2. Login: admin/password
3. Go to Config > Databases > Connections
4. Add connection:
   - Name: `exchange_scraper_db`
   - Driver: PostgreSQL
   - Server: `postgres` (or `localhost` from host)
   - Port: `5432`
   - Database: `exchange_scraper`
   - Username: `ignition`
   - Password: `ignition`
5. Test connection → Save

### Import Ignition Project

*(Instructions will be added when project is ready)*

## Success Criteria

### Scraper Service ✅
- [ ] Docker containers start successfully
- [ ] Health endpoint responds
- [ ] Database connection works
- [ ] Can start a scrape via API
- [ ] Resources are scraped (400+)
- [ ] Data is stored in PostgreSQL
- [ ] Change detection works on second run
- [ ] Control actions (pause/stop) work
- [ ] API returns correct data

### Ignition Integration ⏳
- [ ] Project imports successfully
- [ ] Database connection configured
- [ ] Perspective dashboard loads
- [ ] Can trigger scrape from Ignition
- [ ] Status updates in real-time
- [ ] Tables display data correctly
- [ ] Notifications work

### End-to-End ⏳
- [ ] Full scrape completes successfully
- [ ] Changes detected on subsequent runs
- [ ] Email notifications sent
- [ ] ntfy notifications sent
- [ ] Scheduled scraping works
- [ ] All 400+ resources tracked

## Performance Benchmarks

**Expected Performance:**
- Initial page load: ~30 seconds
- "Load more" clicks: ~100 clicks @ 3 seconds each = ~5 minutes
- Resource scraping: 400 resources @ 1.5 seconds each = ~10 minutes
- **Total first scrape: ~15-20 minutes**

**Subsequent scrapes:**
- Same time, but change detection is instant
- Only new/updated resources flagged

## Logs to Monitor

**Scraper Service:**
```bash
docker compose logs -f scraper-service
```

**PostgreSQL:**
```bash
docker compose logs -f postgres
```

**Ignition:**
```bash
docker compose logs -f ignition
```

## Clean Slate for Re-testing

```bash
# Stop all services
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v

# Start fresh
docker compose up -d
```
