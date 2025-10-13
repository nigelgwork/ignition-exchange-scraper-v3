# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ignition Exchange Scraper v3 is a microservice-based web scraper that monitors the Inductive Automation Ignition Exchange for resource updates. It consists of:

1. **FastAPI Scraper Service** (Python 3.11+) - Playwright-based browser automation
2. **Ignition Gateway Scripts** (Jython 2.7) - API client, notifications, and scheduler
3. **PostgreSQL Database** (12+) - Resource storage and history tracking
4. **Perspective Dashboard** (Design only) - UI for monitoring and control

## Architecture

### Three-Tier Architecture

```
Ignition Gateway (Jython 2.7)
  ↕ HTTP REST API
Scraper Service (Python 3.11 + FastAPI)
  ↕ PostgreSQL
Database (5 tables, 5 views, 2 functions)
```

**Key Design Decision**: The scraper service runs separately from Ignition because:
- Playwright requires Python 3.11+, Ignition uses Jython 2.7
- Browser automation is resource-intensive and should be isolated
- Allows independent scaling and troubleshooting

### Component Communication

- Ignition scripts call FastAPI endpoints using `system.net.httpGet/Post`
- Scraper service stores results directly in PostgreSQL
- Ignition reads results from database views (`vw_latest_results`, `vw_latest_changes`)

## Development Commands

### Scraper Service (Python)

```bash
# Setup
cd scraper-service
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps  # Linux: installs browser system dependencies

# Run service
export DATABASE_URL="postgresql://ignition:ignition@localhost:5434/exchange_scraper"
python -m app.api  # Runs on http://localhost:5000

# Test endpoints
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/scrape/start -H "Content-Type: application/json" -d '{"triggered_by":"manual"}'
curl http://localhost:5000/api/scrape/status
```

### Docker Environment

```bash
cd docker

# Option A: Database + Ignition only (recommended)
docker compose up -d

# Option B: All services including scraper (browser launch issue)
docker compose --profile hybrid up -d

# View logs
docker compose logs -f scraper-service
docker compose logs -f ignition

# Rebuild after code changes
docker compose build scraper-service
docker compose up -d --force-recreate scraper-service
```

### Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U ignition -d exchange_scraper

# Useful queries
SELECT * FROM scrape_jobs ORDER BY job_start_time DESC LIMIT 10;
SELECT * FROM vw_latest_changes;
SELECT * FROM get_scraper_stats();

# Apply schema changes
docker compose exec postgres psql -U ignition -d exchange_scraper -f /docker-entrypoint-initdb.d/01-schema.sql
```

## Code Structure

### Scraper Service (`scraper-service/app/`)

- **api.py** (275 lines): FastAPI app with 10 REST endpoints
  - Lifecycle: `startup_event()` initializes DB and scraper engine
  - Threading: Uses `threading.Thread` for scrape jobs (not FastAPI background tasks) to avoid Playwright conflicts
  - Global state: `scraper_engine` and `db_manager` are module-level variables

- **scraper_engine.py** (471 lines): Core scraping logic
  - `ScraperEngine.scrape_all()`: Main entry point, runs in dedicated thread
  - State management: `_is_running`, `should_stop`, `is_paused` flags
  - Progress tracking: `current_progress` dict with percentage calculation
  - Scraping flow:
    1. Launch Chromium with Playwright (headless mode)
    2. Navigate to Exchange, dismiss modals
    3. Click "Load more" button repeatedly (100 attempts max)
    4. Extract all resource URLs matching `/exchange/\d+/overview`
    5. Visit each URL, parse HTML + capture JSON API responses
    6. Store results in database via `DatabaseManager`

- **database.py** (385 lines): PostgreSQL operations
  - `store_scrape_results()`: Detects new/updated/unchanged resources by comparing versions
  - Uses database views (`vw_*`) for efficient querying
  - All timestamps use Adelaide timezone (`Australia/Adelaide`)

- **config.py** (35 lines): Settings using Pydantic
  - Environment variables: `DATABASE_URL`, `LOG_LEVEL`, `DEBUG`
  - Scraper tunables: `load_more_attempts=100`, `nav_timeout=60000ms`

### Ignition Scripts (`ignition-project/gateway-scripts/`)

**IMPORTANT**: These are Jython 2.7 scripts, not Python 3. Use:
- `system.db.*` for database queries
- `system.net.httpGet/Post` for HTTP calls (not `requests`)
- `system.util.jsonEncode/Decode` (not `json.dumps/loads`)
- Jython 2.7 syntax (e.g., `print "message"` not `print("message")`)

- **exchangeScraperAPI.py** (210 lines): API client module
  - Placed in: `Project > Scripts > exchangeScraper > api`
  - All functions use camelCase per Ignition conventions
  - Key functions: `startScrape()`, `getScraperStatus()`, `pauseScrape()`, `getLatestResults()`

- **exchangeScraperNotifications.py** (231 lines): Email and ntfy.sh notifications
  - Email: Uses Ignition's SMTP profile named "default"
  - ntfy: HTTP POST to ntfy.sh or self-hosted server
  - Reads recipients from `scraper_config` table

- **exchangeScraperScheduler.py** (219 lines): Scheduled scraping
  - To be called from Gateway Timer Script (runs every 1 minute)
  - Checks `scraper_config.schedule_enabled` and `next_run_time`
  - Updates `last_run_time` and `next_run_time` after each run

### Database Schema (`sql/schema.sql`)

**5 Tables**:
1. `exchange_resources` - Current state of all resources (master table)
2. `scrape_jobs` - Job history with status, duration, changes detected
3. `resource_history` - Historical snapshots (every scrape creates new rows)
4. `scraper_config` - Singleton table (id=1) with settings
5. `activity_log` - Application logs linked to jobs

**5 Views**:
- `vw_latest_results` - Most recent scrape (use for "Current" tab)
- `vw_latest_changes` - New/updated resources from latest scrape (use for "Updated" tab)
- `vw_previous_results` - Previous scrape results (use for "Past" tab)
- `vw_recent_jobs` - Last 50 jobs with formatted durations
- `vw_activity_log` - Last 1000 log entries

**2 Functions**:
- `cleanup_old_logs()` - Deletes logs older than 7 days
- `get_scraper_stats()` - Returns aggregate statistics

**Critical Indexes**: All on `job_id`, `resource_id`, `timestamp`, `status` for performance

## Known Issues

### Browser Launch in Docker (Outstanding)

**Symptom**: Chromium won't launch in scraper-service container despite `shm_size: 2gb` and 9 browser args.

**Current Workaround**: Run scraper service on host machine (see Quick Start Option B in README).

**Solutions Tried**:
1. Added `--disable-dev-shm-usage`, `--disable-gpu`, `--disable-software-rasterizer`
2. Set `shm_size: 2gb` in docker-compose.yml
3. Installed all Playwright dependencies in Dockerfile
4. Tried `--no-sandbox` flag

**To Debug**: Check `docs/TROUBLESHOOTING.md` Issue #1 for 5 detailed solutions.

## Important Patterns

### Version Formatting

The scraper converts numeric versions (e.g., `100030000`) to semantic versions (`1.3.0`):
- See `ScraperEngine.format_version()` in scraper_engine.py:131
- Handles 6-9 digit version numbers with complex parsing logic

### Change Detection Algorithm

In `DatabaseManager.store_scrape_results()` (database.py):
1. Query all existing resources into dict keyed by `resource_id`
2. For each scraped resource:
   - If `resource_id` not in DB → `change_type='new'`
   - If version differs → `change_type='updated'`
   - Otherwise → `change_type='unchanged'`
3. Resources not in current scrape → mark `is_deleted=TRUE`

### Pause/Stop Pattern

Scraper checks `check_pause_stop()` at two points:
1. During "Load more" loop (every button click)
2. Between resource detail extractions

This allows responsive UI controls without race conditions.

## Testing Workflow

1. **Health Check**: `curl http://localhost:5000/health` → should return `{"status":"healthy"}`
2. **Start Scrape**: `curl -X POST http://localhost:5000/api/scrape/start -d '{"triggered_by":"test"}'`
3. **Monitor Progress**: `curl http://localhost:5000/api/scrape/status | jq` → watch percentage increase
4. **Check Results**: Query `SELECT COUNT(*) FROM vw_latest_results` → should see ~400+ resources
5. **Verify Changes**: Query `SELECT * FROM vw_latest_changes` → new/updated resources

Expected scrape duration: 8-15 minutes for 400+ resources.

## File Modification Guidelines

### When editing scraper_engine.py:
- Always maintain Adelaide timezone (`ADELAIDE_TZ = ZoneInfo("Australia/Adelaide")`)
- Browser args order matters for WSL2 compatibility
- Don't remove `time.sleep()` calls - needed for page load stability
- Progress updates must be atomic (don't split `update_progress()` calls)

### When editing Ignition scripts:
- Use Jython 2.7 syntax only (no Python 3 features)
- All HTTP calls go through `makeApiCall()` helper
- Database queries use `system.db.runNamedQuery()` or `system.db.runPrepQuery()`
- Follow camelCase naming (not snake_case)

### When editing schema.sql:
- Views must use double-quoted "Column Names" for Ignition compatibility
- Always include `IF NOT EXISTS` for idempotent schema
- Add comments for all tables/views using `COMMENT ON`
- Test with `psql` before deploying

## Deployment Checklist

See `DEPLOYMENT_READY.md` for full checklist. Key steps:

1. Test scraper on host machine (Option B setup)
2. Verify 400+ resources scraped successfully
3. Import gateway scripts to Ignition: `Project > Scripts > exchangeScraper`
4. Configure database connection in Ignition
5. Set up SMTP profile named "default"
6. Update `scraper_config` table with notification settings
7. Build Perspective dashboard (11 hours estimated)
8. Create Gateway Timer Script calling `exchangeScraper.scheduler.checkAndRunSchedule()`
9. Test full end-to-end workflow

## Useful References

- Main docs: `docs/` directory (6 markdown files)
- API reference: `docs/TESTING_GUIDE.md` has all 10 endpoints documented
- Setup guide: `docs/IGNITION_SETUP.md` (7-part walkthrough)
- Dashboard design: `docs/PERSPECTIVE_DASHBOARD.md` (complete component specs)
