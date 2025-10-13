# Ignition Exchange Scraper v3 - Setup Guide

## Prerequisites

- Ignition 8.3+ Gateway with internet access
- PostgreSQL 12+ database (accessible from Ignition)
- Scraper service running (see [Docker Setup](../docker/README.md))

## Part 1: Database Connection

### 1.1 Configure Database Connection in Ignition

1. Open Ignition Gateway Config: `http://your-gateway:8088`
2. Login with admin credentials
3. Navigate to: **Config > Databases > Connections**
4. Click **Create new Database Connection**
5. Configure connection:
   - **Name**: `exchange_scraper_db`
   - **Connect URL**: `jdbc:postgresql://your-postgres-host:5432/exchange_scraper`
   - **Username**: `ignition`
   - **Password**: `ignition`
   - **Driver**: PostgreSQL (select from dropdown)
6. Click **Test Connection** - should show success
7. Click **Save Changes**

**Docker Environment Note**: If Ignition is running in Docker on the same network, use host `postgres` instead of IP address.

### 1.2 Verify Database Tables

From Gateway Config > Databases > Connections > exchange_scraper_db > Query Browser, run:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

You should see:
- `exchange_resources`
- `scrape_jobs`
- `resource_history`
- `scraper_config`
- `activity_log`

## Part 2: Gateway Scripts

### 2.1 Import Gateway Script Modules

1. Open **Designer**
2. Navigate to: **Project Browser > Scripts**
3. Create new script package: **Right-click Scripts > New Script Package**
   - Name: `exchangeScraper`
4. Create three script modules inside `exchangeScraper`:

#### Module 1: api

**Path**: `Project > Scripts > exchangeScraper > api`

Copy contents from: [`ignition-project/gateway-scripts/exchangeScraperAPI.py`](../ignition-project/gateway-scripts/exchangeScraperAPI.py)

**Key Functions**:
- `getScraperStatus()` - Get current scraper status
- `startScrape(triggeredBy)` - Start a scrape job
- `pauseScrape()` - Pause current job
- `resumeScrape()` - Resume paused job
- `stopScrape()` - Stop current job
- `getLatestResults(limit)` - Get latest results
- `getLatestChanges()` - Get changes from latest scrape
- `getRecentJobs(limit)` - Get job history
- `testConnection()` - Test API health

#### Module 2: notifications

**Path**: `Project > Scripts > exchangeScraper > notifications`

Copy contents from: [`ignition-project/gateway-scripts/exchangeScraperNotifications.py`](../ignition-project/gateway-scripts/exchangeScraperNotifications.py)

**Key Functions**:
- `sendEmailNotification(jobInfo)` - Send email notification
- `sendNtfyNotification(jobInfo)` - Send ntfy notification
- `sendAllNotifications(jobInfo)` - Send all enabled notifications
- `testEmailNotification()` - Test email setup
- `testNtfyNotification()` - Test ntfy setup

#### Module 3: scheduler

**Path**: `Project > Scripts > exchangeScraper > scheduler`

Copy contents from: [`ignition-project/gateway-scripts/exchangeScraperScheduler.py`](../ignition-project/gateway-scripts/exchangeScraperScheduler.py)

**Key Functions**:
- `checkAndRunSchedule()` - Main scheduler function (call from Timer Script)
- `manualTrigger()` - Manually trigger a scrape
- `pauseCurrentScrape()` - Pause scraper
- `resumeCurrentScrape()` - Resume scraper
- `stopCurrentScrape()` - Stop scraper
- `updateScheduleSettings(intervalDays, enabled)` - Update schedule config

### 2.2 Save Project

1. Click **Save Project** in Designer
2. Verify scripts are saved by reopening them

## Part 3: Gateway Timer Script

### 3.1 Create Scheduled Script

1. In **Gateway Config**: Navigate to **Config > Scripting > Gateway Timer Scripts**
2. Click **Add New** timer script
3. Configure:
   - **Name**: `Exchange Scraper Scheduler`
   - **Execution Mode**: Fixed Rate
   - **Rate**: `3600000` (1 hour in milliseconds)
   - **Initial Delay**: `60000` (1 minute)
   - **Enabled**: ✓ (checked)

4. **Script Code**:

```python
"""
Exchange Scraper Scheduler Timer Script
Runs every hour to check if a scheduled scrape should start
"""

import exchangeScraper.scheduler as scheduler

# Check if it's time to run a scrape and start it if needed
scheduler.checkAndRunSchedule()
```

5. Click **Save Changes**

### 3.2 Test Timer Script

From Gateway Config > Scripting > Gateway Timer Scripts:
1. Find "Exchange Scraper Scheduler"
2. Click **Test** button
3. Check **Gateway > Status > Diagnostics > Logs** for output

Expected log messages:
- "Not time to run yet" (if schedule not due)
- OR "Starting scheduled scrape..." (if schedule is due)

## Part 4: SMTP Configuration (for Email Notifications)

### 4.1 Configure SMTP Settings

1. In **Gateway Config**: Navigate to **Config > Email > SMTP**
2. Click **Create new SMTP profile**
3. Configure:
   - **Name**: `default`
   - **SMTP Host**: Your mail server (e.g., `smtp.gmail.com`)
   - **Port**: `587` (TLS) or `465` (SSL)
   - **Use SSL/TLS**: ✓
   - **Username**: Your email username
   - **Password**: Your email password
   - **From Address**: Sender email address
4. Click **Test SMTP** - should send test email
5. Click **Save Changes**

### 4.2 Enable Email Notifications

Update database configuration:

```sql
UPDATE scraper_config
SET notification_email_enabled = true,
    notification_email_recipients = 'user@example.com,admin@example.com'
WHERE id = 1;
```

### 4.3 Test Email Notification

In **Designer > Script Console** (Gateway scope):

```python
import exchangeScraper.notifications as notifications
result = notifications.testEmailNotification()
print "Email sent:" if result else "Email failed!"
```

## Part 5: ntfy Configuration (for Push Notifications)

### 5.1 Set Up ntfy

Option A: Use public ntfy.sh service
- Go to https://ntfy.sh
- Choose a unique topic name (e.g., `ignition-exchange-alerts-xyz123`)

Option B: Self-host ntfy server
- See https://docs.ntfy.sh/install/

### 5.2 Enable ntfy Notifications

Update database configuration:

```sql
UPDATE scraper_config
SET notification_ntfy_enabled = true,
    notification_ntfy_server = 'https://ntfy.sh',
    notification_ntfy_topic = 'your-unique-topic-name'
WHERE id = 1;
```

### 5.3 Subscribe to Topic

On your mobile device:
1. Install ntfy app (iOS/Android)
2. Subscribe to your topic name
3. Test notification

### 5.4 Test ntfy Notification

In **Designer > Script Console** (Gateway scope):

```python
import exchangeScraper.notifications as notifications
result = notifications.testNtfyNotification()
print "ntfy sent:" if result else "ntfy failed!"
```

## Part 6: Configure Schedule

### 6.1 Set Scrape Interval

Update database configuration:

```sql
-- Set to run every 7 days
UPDATE scraper_config
SET schedule_interval_days = 7,
    schedule_enabled = true
WHERE id = 1;
```

### 6.2 Schedule Options

Common intervals:
- Daily: `schedule_interval_days = 1`
- Weekly: `schedule_interval_days = 7`
- Bi-weekly: `schedule_interval_days = 14`
- Monthly: `schedule_interval_days = 30`

### 6.3 Disable Scheduling

To disable automatic scraping (manual only):

```sql
UPDATE scraper_config
SET schedule_enabled = false
WHERE id = 1;
```

## Part 7: Manual Testing

### 7.1 Test API Connection

In **Designer > Script Console** (Gateway scope):

```python
import exchangeScraper.api as api

# Test connection
healthy = api.testConnection()
print "Connection OK" if healthy else "Connection FAILED"

# Get status
status = api.getScraperStatus()
print status
```

Expected output:
```
Connection OK
{u'status': u'idle', u'job_id': None, u'progress': {...}}
```

### 7.2 Trigger Manual Scrape

**Option A**: From Script Console

```python
import exchangeScraper.scheduler as scheduler

result = scheduler.manualTrigger()
print result
```

**Option B**: From Perspective dashboard (see Part 8)

### 7.3 Monitor Progress

```python
import exchangeScraper.api as api
import time

# Monitor for 5 minutes
for i in range(60):
    status = api.getScraperStatus()
    print "Status:", status['status']
    print "Progress:", status['progress']['percentage'], "%"
    print "Current:", status['progress']['current_item']
    print "---"
    time.sleep(5)
```

## Part 8: Perspective Dashboard (Coming Soon)

The Perspective dashboard will provide:
- Real-time status monitoring
- Manual scrape controls (Start/Pause/Stop)
- Results tables with 3-tab view (Updated/Current/Past)
- Job history
- Activity logs
- Configuration interface

Dashboard setup instructions will be added after dashboard is built.

## Troubleshooting

### Database Connection Fails

**Error**: "Connection refused" or "Could not connect"

**Solution**:
1. Verify PostgreSQL is running
2. Check host/port are correct
3. Ensure firewall allows connection
4. Test with `psql` command line:
   ```bash
   psql -h postgres-host -p 5432 -U ignition -d exchange_scraper
   ```

### API Connection Fails

**Error**: `api.testConnection()` returns `False`

**Solution**:
1. Verify scraper service is running:
   ```bash
   curl http://scraper-host:5000/health
   ```
2. Check `scraper_service_url` in database:
   ```sql
   SELECT scraper_service_url FROM scraper_config WHERE id = 1;
   ```
3. Update if needed:
   ```sql
   UPDATE scraper_config
   SET scraper_service_url = 'http://correct-host:5000'
   WHERE id = 1;
   ```

### Gateway Scripts Not Found

**Error**: "Module exchangeScraper not found"

**Solution**:
1. Verify scripts are saved in correct location:
   - Project > Scripts > exchangeScraper > api
   - Project > Scripts > exchangeScraper > notifications
   - Project > Scripts > exchangeScraper > scheduler
2. Save project and restart Designer
3. Check project is published to gateway

### Email Notifications Not Sending

**Error**: Email notification fails silently

**Solution**:
1. Test SMTP profile in Gateway Config
2. Check Gateway logs for errors:
   - Gateway > Status > Diagnostics > Logs
   - Filter by "email" or "smtp"
3. Verify recipients in database:
   ```sql
   SELECT notification_email_recipients FROM scraper_config WHERE id = 1;
   ```

### Scrape Takes Too Long

**Issue**: Scrape runs for over 30 minutes

**Explanation**: First scrape takes 15-20 minutes for ~400 resources. This is normal.

**Factors**:
- Network speed
- Exchange website response time
- Number of "Load more" clicks needed (~100)
- Processing time per resource

**Monitor Progress**:
```python
import exchangeScraper.api as api
status = api.getScraperStatus()
print "Elapsed:", status['elapsed_seconds'], "seconds"
print "Progress:", status['progress']['percentage'], "%"
```

### Scrape Fails to Start

**Error**: "Scraper is already running"

**Solution**:
```python
import exchangeScraper.api as api

# Check current status
status = api.getScraperStatus()
print status['status']

# If stuck in "running", stop it
if status['status'] == 'running':
    api.stopScrape()
```

## Next Steps

1. ✅ Complete Part 1-7 of this setup guide
2. ⏳ Wait for Perspective dashboard to be built
3. ⏳ Import Perspective views
4. ⏳ Configure dashboard permissions
5. ✅ Run first test scrape
6. ✅ Verify 400+ resources are scraped
7. ✅ Test notifications
8. ✅ Enable scheduling

## Support

- Check logs: Gateway > Status > Diagnostics > Logs
- Review database: Use Query Browser in Gateway Config
- Test API: Use Script Console in Designer
- Monitor scrape: `docker compose logs -f scraper-service`

## References

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures
- [POC_ANALYSIS.md](POC_ANALYSIS.md) - Technical analysis
- [Docker README](../docker/README.md) - Docker environment setup
