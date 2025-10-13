# Quick Start Guide - Ignition Exchange Scraper v3

**Status**: Scraper service tested and operational (512 resources scraped successfully!)
**Current Step**: Ignition Integration

## Prerequisites ✅

- [x] PostgreSQL running (Docker, port 5434)
- [x] Database populated with 512 resources
- [x] Scraper service operational on host machine
- [x] Ignition Gateway running (http://localhost:8088)

## Integration Steps (Manual - Requires Ignition Designer)

### Step 1: Database Connection (5 minutes)

**Gateway Config**:
1. Open: http://localhost:8088
2. Login: `admin` / `password`
3. Navigate to: **Config > Databases > Connections**
4. Click: **Create new Database Connection...**
5. Configure:
   ```
   Name: exchange_scraper_db
   Connect URL: jdbc:postgresql://postgres:5432/exchange_scraper
   Username: ignition
   Password: ignition
   ```
6. Click **Create New Database Connection**
7. Verify: Status shows "Valid" with green checkmark

**Troubleshooting**:
- If connection fails, check PostgreSQL is running: `docker compose ps`
- Verify port: Should be `postgres:5432` (internal Docker network) not `localhost:5434`

### Step 2: Import Gateway Scripts (15 minutes)

**Designer Setup**:
1. Open Ignition Designer
2. Go to: **Project Browser** (left panel)
3. Right-click on **Scripts** folder
4. Select: **New Script** > **Script Package**
5. Name it: `exchangeScraper`

**Import Each Module**:

**Module 1: api** (API Client)
1. Right-click `exchangeScraper` > **New Script** > **Script Module**
2. Name: `api`
3. Open file: `ignition-project/gateway-scripts/exchangeScraperAPI.py`
4. Copy entire contents
5. Paste into Designer script editor
6. Save (Ctrl+S)

**Module 2: notifications** (Email & ntfy)
1. Right-click `exchangeScraper` > **New Script** > **Script Module**
2. Name: `notifications`
3. Open file: `ignition-project/gateway-scripts/exchangeScraperNotifications.py`
4. Copy entire contents
5. Paste into Designer
6. Save

**Module 3: scheduler** (Scheduling & Control)
1. Right-click `exchangeScraper` > **New Script** > **Script Module**
2. Name: `scheduler`
3. Open file: `ignition-project/gateway-scripts/exchangeScraperScheduler.py`
4. Copy entire contents
5. Paste into Designer
6. Save

**Test in Script Console**:
```python
# Test API connection
import exchangeScraper.api as api
print api.testConnection()  # Should print True

# Test getting status
status = api.getScraperStatus()
print status

# Get statistics
stats = api.getStatistics()
print stats  # Should show 512 resources
```

### Step 3: Create Named Queries (30 minutes)

**For Each SQL File in** `ignition-project/named-queries/`:

1. Open Designer
2. Go to: **Project Browser > Data > Named Queries**
3. Right-click > **New Named Query**
4. Set properties:
   - **Name**: (from filename, e.g., "GetScraperStatus")
   - **Database**: `exchange_scraper_db`
   - **Query Type**: Select (or Update for UpdateConfig)
5. Copy SQL from file
6. Add parameters if specified in comments
7. Click **Test** to verify
8. Save

**Named Queries to Create** (9 total):
- GetScraperStatus
- GetRecentJobs
- GetLatestResults
- GetLatestChanges
- GetPreviousResults
- GetRecentLogs
- GetStatistics
- GetConfig
- UpdateConfig

**Test Named Queries**:
```python
# In Script Console
results = system.db.runNamedQuery("GetStatistics")
print results  # Should show 512 total_resources
```

### Step 4: Gateway Timer Script (10 minutes)

**Gateway Config**:
1. Go to: http://localhost:8088/web/config/scripting.gateway-timer
2. Click: **Add New Timer Script**
3. Configure:
   ```
   Name: Exchange Scraper Scheduler
   Enabled: ✓ (checked)
   Rate: Fixed Rate
   Delay: 3600000 (1 hour in milliseconds)
   ```
4. Script:
   ```python
   import exchangeScraper.scheduler as scheduler
   scheduler.checkAndRunSchedule()
   ```
5. Save

**Note**: This will check every hour if a scheduled scrape should run. Actual scraping frequency is configured in the database (default: 7 days).

### Step 5: Configure Scraper Service URL (5 minutes)

**Update Database Config**:
```sql
-- Run in database
UPDATE scraper_config
SET scraper_service_url = 'http://host.docker.internal:5000'
WHERE id = 1;
```

**Note**: Use `host.docker.internal:5000` to access host machine from Ignition Docker container, or the actual host IP address.

### Step 6: Test Manual Scrape (5 minutes)

**Script Console**:
```python
import exchangeScraper.scheduler as scheduler

# Trigger manual scrape
result = scheduler.manualTrigger()
print result

# Monitor progress (run multiple times)
import exchangeScraper.api as api
status = api.getScraperStatus()
print "Status:", status['status']
print "Job ID:", status['job_id']
```

**Expected**: New scrape job starts, you'll see "Status: running"

### Step 7: Configure Notifications (Optional, 15 minutes)

**SMTP Setup** (Gateway Config):
1. Go to: Config > Email > SMTP
2. Create profile named: `default`
3. Configure your SMTP server settings
4. Test email delivery

**ntfy Setup**:
1. Choose unique topic at https://ntfy.sh (e.g., `exchange-scraper-xyz123`)
2. Update database:
   ```sql
   UPDATE scraper_config
   SET notification_ntfy_enabled = true,
       notification_ntfy_topic = 'your-unique-topic'
   WHERE id = 1;
   ```
3. Test:
   ```python
   import exchangeScraper.notifications as notif
   notif.testNtfyNotification()
   ```

## Current System Status

### Services Running
```bash
# Check status
docker compose ps

# Services should show:
✓ PostgreSQL: running (healthy)
✓ Ignition: running
✓ Scraper API: running on host (http://localhost:5000)
```

### Database Contents
- **512 resources** in exchange_resources table
- **1 completed job** (Job #9, 66 minutes duration)
- **512 changes detected** (all new)
- **Activity logs** available

### API Endpoints Available
```bash
# Health check
curl http://localhost:5000/health

# Get statistics
curl http://localhost:5000/api/stats

# Get latest results
curl http://localhost:5000/api/results/latest
```

## Next Steps After Integration

1. **Build Perspective Dashboard** (11 hours)
   - See `docs/PERSPECTIVE_DASHBOARD.md` for complete design
   - All Named Queries ready
   - Gateway scripts ready

2. **Enable Scheduled Scraping**
   ```sql
   UPDATE scraper_config
   SET schedule_enabled = true,
       schedule_interval_days = 7
   WHERE id = 1;
   ```

3. **Monitor and Test**
   - Verify dashboard displays data correctly
   - Test manual scrape triggering
   - Confirm notifications working

## Troubleshooting

### Gateway Scripts Not Found
- Ensure scripts saved in Designer
- Check Script Console for import errors
- Verify package name is exactly `exchangeScraper` (case-sensitive)

### Named Queries Fail
- Verify database connection status (should be green/valid)
- Check SQL syntax in query
- Ensure database contains data (run `SELECT COUNT(*) FROM exchange_resources`)

### Scraper Service Unreachable
- Check service is running: `ps aux | grep "app.api"`
- Verify port 5000 is listening: `netstat -tuln | grep 5000`
- Test API directly: `curl http://localhost:5000/health`

### Timer Script Not Running
- Check Gateway Config > Scripting > Gateway Timer Scripts
- Verify script is enabled (checkbox)
- Check Gateway logs for errors

## Support

- Full setup documentation: `docs/IGNITION_SETUP.md`
- Troubleshooting guide: `docs/TROUBLESHOOTING.md`
- Dashboard design: `docs/PERSPECTIVE_DASHBOARD.md`
- Project status: `docs/PROJECT_STATUS.md`

## Success Criteria

- [ ] Database connection valid
- [ ] Gateway scripts imported and testable
- [ ] Named Queries created and working
- [ ] Timer script created (can be disabled until dashboard ready)
- [ ] Manual scrape can be triggered from Script Console
- [ ] Statistics show 512 resources

**Estimated Time**: 1-2 hours for complete integration
