# Troubleshooting Guide - Exchange Scraper v3

## Common Issues and Solutions

### Issue 1: Scraper Hangs at Browser Launch in Docker

**Symptoms:**
- Scrape starts but shows no progress
- Status stays "running" but progress remains 0%
- Logs show "Starting scrape job #X" but nothing after
- Elapsed time increases but no resources scraped

**Cause:**
Playwright's Chromium browser fails to launch in Docker container due to:
- Insufficient shared memory (`/dev/shm`)
- Missing system dependencies
- Container resource constraints
- Graphics/display issues in headless mode

**Solutions:**

#### Solution A: Increase Shared Memory (Applied)

Edit `docker-compose.yml`:
```yaml
scraper-service:
  shm_size: '2gb'  # Add this line
```

Then restart:
```bash
docker compose --profile hybrid down
docker compose --profile hybrid up -d
```

**Status**: ✅ Already applied, but may not be sufficient alone.

#### Solution B: Add Additional Browser Arguments

Edit `/git/ignition-exchange-scraper-v3/scraper-service/app/scraper_engine.py`:

Find the browser launch section (around line 259):
```python
browser = p.chromium.launch(
    headless=self.headless,
    args=[
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
    ],
)
```

Replace with:
```python
browser = p.chromium.launch(
    headless=self.headless,
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",  # Use /tmp instead of /dev/shm
        "--disable-blink-features=AutomationControlled",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--no-first-run",
        "--no-zygote",
        "--single-process",  # Run in single process mode
    ],
)
```

Then rebuild:
```bash
docker compose build scraper-service
docker compose --profile hybrid up -d
```

#### Solution C: Run Scraper Outside Docker

The v2 scraper worked successfully outside Docker. Run the service on the host machine:

**Prerequisites:**
```bash
# Install Python 3.11+
# Install PostgreSQL client libraries

# Install dependencies
cd /git/ignition-exchange-scraper-v3/scraper-service
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps  # Install system dependencies
```

**Run Service:**
```bash
# Set environment variables
export DATABASE_URL="postgresql://ignition:ignition@localhost:5434/exchange_scraper"
export LOG_LEVEL="INFO"

# Start service
python -m app.api
```

**Update Ignition Config:**
```sql
UPDATE scraper_config
SET scraper_service_url = 'http://localhost:5000'
WHERE id = 1;
```

#### Solution D: Use Firefox Instead of Chromium

Edit `scraper_engine.py`:
```python
# Change from:
browser = p.chromium.launch(...)

# To:
browser = p.firefox.launch(
    headless=self.headless,
    args=[]
)
```

Then rebuild and restart.

#### Solution E: Increase Container Resources

Edit `docker-compose.yml`:
```yaml
scraper-service:
  shm_size: '2gb'
  mem_limit: '4g'  # Add memory limit
  cpus: '2.0'      # Add CPU limit
```

### Issue 2: Database Connection Fails

**Symptoms:**
- "Connection refused" error
- "could not connect to server" error
- Named queries fail in Ignition

**Solutions:**

#### Check PostgreSQL is Running
```bash
docker compose ps postgres
# Should show "running (healthy)"
```

#### Verify Database Exists
```bash
docker compose exec postgres psql -U ignition -l
# Should list "exchange_scraper" database
```

#### Test Connection from Ignition
In Designer > Script Console (Gateway scope):
```python
# Test database connection
result = system.db.runQuery("SELECT 1 as test", database='exchange_scraper_db')
print result
```

#### Check Connection String
In Gateway Config > Databases > Connections > exchange_scraper_db:
- **From Ignition Container**: Use host `postgres` (not IP)
- **From Host Machine**: Use `localhost:5434` (note custom port)
- **From External**: Use server IP + port 5434

#### Port Already in Use
If you see "port is already allocated":
```bash
# Check what's using the port
lsof -i :5432  # or whatever port

# Change port in docker-compose.yml
# We're using 5434 to avoid conflicts
```

### Issue 3: Scraper Service API Not Responding

**Symptoms:**
- `curl http://localhost:5000/health` fails
- API returns 500 errors
- Service logs show errors

**Solutions:**

#### Check Service is Running
```bash
docker compose ps scraper-service
docker compose logs scraper-service
```

#### Verify Database Connection
Service fails to start if database is unreachable:
```bash
docker compose logs scraper-service | grep "Database"
# Should see: "Database connection established"
```

#### Check Port Mapping
```bash
docker compose ps scraper-service
# Should show: 0.0.0.0:5000->5000/tcp
```

#### Rebuild Service
If code changes were made:
```bash
docker compose build --no-cache scraper-service
docker compose --profile hybrid up -d
```

### Issue 4: Gateway Scripts Not Found

**Symptoms:**
- "Module exchangeScraper not found" error
- Scripts don't execute in Designer

**Solutions:**

#### Verify Script Structure
In Designer > Project Browser > Scripts:
```
Scripts
└── exchangeScraper
    ├── api
    ├── notifications
    └── scheduler
```

#### Check Script Names
Module names must match exactly:
- `api` (not `exchangeScraperAPI`)
- `notifications` (not `exchangeScraperNotifications`)
- `scheduler` (not `exchangeScraperScheduler`)

#### Save and Publish
1. Save project in Designer
2. Publish project to gateway
3. Restart Designer

#### Test in Script Console
Gateway scope (not Vision Client or Perspective):
```python
import exchangeScraper.api as api
print api.testConnection()
```

### Issue 5: Email Notifications Not Sending

**Symptoms:**
- Email notification returns False
- No emails received

**Solutions:**

#### Test SMTP Profile
Gateway Config > Email > SMTP > [your profile] > Test SMTP

#### Check SMTP Settings
Common settings:
- **Gmail**: `smtp.gmail.com:587`, TLS enabled, app password required
- **Office 365**: `smtp.office365.com:587`, TLS enabled
- **Custom**: Verify host, port, credentials with IT

#### Verify Recipients
```sql
SELECT notification_email_recipients FROM scraper_config WHERE id = 1;
```

Should show comma-separated email addresses.

#### Check Gateway Logs
Gateway > Status > Diagnostics > Logs
Filter by "email" or "smtp"

#### Test from Script Console
```python
import exchangeScraper.notifications as notifications
result = notifications.testEmailNotification()
print "Success" if result else "Failed"
```

### Issue 6: ntfy Notifications Not Sending

**Symptoms:**
- ntfy notification returns False
- No notifications on mobile

**Solutions:**

#### Verify ntfy Configuration
```sql
SELECT notification_ntfy_server, notification_ntfy_topic
FROM scraper_config WHERE id = 1;
```

#### Test Topic Manually
```bash
curl -d "Test message" https://ntfy.sh/your-topic-name
```

Check if notification appears on mobile.

#### Check Topic Name
- Must be unique (not generic like "test")
- No spaces or special characters
- Example: `ignition-scraper-alerts-xyz123`

#### Test from Script Console
```python
import exchangeScraper.notifications as notifications
result = notifications.testNtfyNotification()
print "Success" if result else "Failed"
```

### Issue 7: Scheduled Scraping Not Working

**Symptoms:**
- Timer script exists but scrapes don't start automatically
- Schedule seems ignored

**Solutions:**

#### Verify Timer Script is Enabled
Gateway Config > Scripting > Gateway Timer Scripts
- "Exchange Scraper Scheduler" should be ✓ Enabled

#### Check Schedule Configuration
```sql
SELECT schedule_enabled, schedule_interval_days, next_run_time
FROM scraper_config WHERE id = 1;
```

#### Verify Next Run Time
If `next_run_time` is in the past, update it:
```sql
UPDATE scraper_config
SET next_run_time = NOW() + INTERVAL '1 hour'
WHERE id = 1;
```

#### Test Timer Script
Gateway Config > Scripting > Gateway Timer Scripts
- Select "Exchange Scraper Scheduler"
- Click "Test" button
- Check logs for output

#### Check Timer Script Logs
Gateway > Status > Diagnostics > Logs
Filter by recent time and look for script output

### Issue 8: Results Tables Empty in Perspective

**Symptoms:**
- Tables show no data
- Named queries return empty

**Solutions:**

#### Verify Scrape Completed
```sql
SELECT * FROM scrape_jobs ORDER BY job_start_time DESC LIMIT 1;
```

Status should be 'completed', not 'running' or 'failed'.

#### Check Resource Count
```sql
SELECT COUNT(*) FROM exchange_resources WHERE is_deleted = FALSE;
```

Should show 400+ after first successful scrape.

#### Test Named Query
Designer > Project Browser > Named Queries > ExchangeScraper
- Right-click query > Test Query
- Should return rows

#### Verify Database Connection
In Perspective view:
- Check binding status (should be green)
- Check for binding errors in console

#### Refresh View
Add Refresh button script:
```python
self.getSibling("ResultsTable").refreshBinding("data")
```

### Issue 9: Scrape Fails with "No resources found"

**Symptoms:**
- Job completes but finds 0 resources
- Status shows "failed"

**Solutions:**

#### Check Website Accessibility
From container:
```bash
docker compose exec scraper-service curl -I https://inductiveautomation.com/exchange
```

Should return 200 OK.

#### Verify No Network Blocks
- Check if corporate firewall blocks exchange website
- Verify no proxy required
- Test from browser on same network

#### Check for Website Changes
Exchange website structure may have changed:
- Update CSS selectors in `scraper_engine.py`
- Test manually on exchange website

#### Enable Headed Mode for Debugging
Edit `scraper_engine.py`:
```python
# Change from:
self.headless = True

# To:
self.headless = False
```

Note: Won't work in Docker, run on host to see browser.

### Issue 10: Performance Issues / Slow Scraping

**Symptoms:**
- Scrape takes over 30 minutes
- Progress is very slow

**Solutions:**

#### Normal First Scrape
First scrape takes 15-20 minutes for 400+ resources. This is expected.

#### Factors Affecting Speed
- Network speed
- Exchange website response time
- Number of "Load more" clicks (~100)
- Container CPU/memory

#### Optimize Settings
Edit `scraper-service/app/config.py`:
```python
nav_timeout: int = 60000  # Reduce from 120000 if site is fast
load_more_attempts: int = 150  # Increase if not finding all resources
```

#### Monitor Progress
```python
import exchangeScraper.api as api
status = api.getScraperStatus()
print status['progress']
```

### Issue 11: Docker Build Fails

**Symptoms:**
- `docker compose build` fails
- Missing dependencies

**Solutions:**

#### Clear Build Cache
```bash
docker compose build --no-cache scraper-service
```

#### Check Dockerfile Syntax
Verify `scraper-service/Dockerfile` is valid.

#### Verify requirements.txt
All dependencies should be listed with versions.

#### Check Disk Space
```bash
df -h
```

Docker builds require several GB free.

#### Playwright Install Fails
Playwright install can fail on some architectures:
```bash
# Try manually
docker compose run scraper-service playwright install chromium
```

## Getting Help

### Check Logs First

**All Services:**
```bash
docker compose logs
```

**Specific Service:**
```bash
docker compose logs scraper-service
docker compose logs postgres
docker compose logs ignition
```

**Follow Logs (Real-time):**
```bash
docker compose logs -f scraper-service
```

### Database Diagnostics

```bash
# Connect to database
docker compose exec postgres psql -U ignition -d exchange_scraper

# Useful queries:
SELECT * FROM scrape_jobs ORDER BY job_start_time DESC LIMIT 5;
SELECT COUNT(*) FROM exchange_resources WHERE is_deleted = FALSE;
SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 20;
SELECT * FROM scraper_config;

# Exit
\q
```

### API Diagnostics

```bash
# Health check
curl http://localhost:5000/health

# Current status
curl http://localhost:5000/api/scrape/status

# Statistics
curl http://localhost:5000/api/stats

# Recent jobs
curl http://localhost:5000/api/jobs/recent?limit=5
```

### Ignition Diagnostics

**Gateway Logs:**
Gateway > Status > Diagnostics > Logs

**Script Console Tests:**
```python
# Test database
result = system.db.runQuery("SELECT 1", database='exchange_scraper_db')
print result

# Test API connection
import exchangeScraper.api as api
print api.testConnection()

# Test scraper status
import exchangeScraper.api as api
status = api.getScraperStatus()
print status
```

## Known Limitations

1. **Browser in Docker**: Chromium may not launch reliably in all Docker environments. Consider running scraper on host.

2. **First Scrape Time**: 15-20 minutes is normal for initial scrape of 400+ resources.

3. **Exchange Website Changes**: If Inductive Automation updates the Exchange website structure, CSS selectors may need updates.

4. **Jython 2.7**: Gateway scripts use Jython 2.7 (Python 2 syntax). Modern Python features not available.

5. **Perspective Limitations**: Some advanced UI features require Perspective module license.

## Alternative Approaches

### Option A: Native Ignition Module (Future)

Develop custom Java/Python module for Ignition that includes browser automation. This eliminates Docker dependency but requires significant development effort (8-10 weeks).

### Option B: Hybrid with Host Scraper

Run scraper service on host machine instead of Docker, keep other services in Docker:

1. Stop Docker scraper: `docker compose stop scraper-service`
2. Run scraper on host (see Solution C above)
3. Update `scraper_service_url` to `http://host.docker.internal:5000` (Mac/Windows) or host IP (Linux)

### Option C: Manual Scraping

If automation fails, export resources manually:
1. Visit Exchange website
2. Use browser dev tools to extract resource data
3. Import into database manually
4. Use Perspective dashboard for viewing only

## Reporting Issues

When reporting issues, include:

1. **Environment**:
   - OS (Linux/Windows/Mac)
   - Docker version
   - Ignition version

2. **Logs**:
   - Scraper service logs: `docker compose logs scraper-service`
   - Database logs if relevant
   - Gateway logs from Ignition

3. **Configuration**:
   - Docker Compose file
   - Database connection settings
   - Any customizations made

4. **Steps to Reproduce**:
   - Exact commands run
   - What you expected
   - What actually happened

5. **Database State**:
   - Job status: `SELECT * FROM scrape_jobs ORDER BY job_start_time DESC LIMIT 1;`
   - Resource count: `SELECT COUNT(*) FROM exchange_resources;`

## Additional Resources

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures
- [IGNITION_SETUP.md](IGNITION_SETUP.md) - Setup instructions
- [PERSPECTIVE_DASHBOARD.md](PERSPECTIVE_DASHBOARD.md) - Dashboard design
- [POC_ANALYSIS.md](POC_ANALYSIS.md) - Technical analysis
- [Docker README](../docker/README.md) - Docker environment
