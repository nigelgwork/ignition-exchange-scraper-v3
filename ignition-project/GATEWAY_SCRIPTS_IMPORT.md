# Gateway Scripts Import Guide

## Overview

Three Jython 2.7 gateway script modules need to be imported into Ignition Designer:
1. **api** - API client for scraper service
2. **notifications** - Email and ntfy notifications
3. **scheduler** - Scheduling and manual control

## Prerequisites

- Ignition Designer installed and connected to gateway
- Project opened in Designer
- Database connection created (`exchange_scraper_db`)

## Step-by-Step Import

### 1. Create Script Package

1. Open **Project Browser** in Designer
2. Locate **Scripts** folder in project tree
3. Right-click **Scripts**
4. Select: **New** > **Script Package**
5. Name: `exchangeScraper`
6. Click **OK**

### 2. Import api Module

**Purpose**: Communicate with scraper service REST API

**Steps**:
1. Right-click `exchangeScraper` package
2. Select: **New** > **Script Module**
3. Name: `api`
4. Open file: `gateway-scripts/exchangeScraperAPI.py`
5. Copy entire contents (210 lines)
6. Paste into Designer script editor
7. Save (Ctrl+S or File > Save)

**Functions Provided**:
- `testConnection()` - Test API connectivity
- `getScraperStatus()` - Get current status
- `startScrape(triggeredBy)` - Start new scrape
- `pauseScrape()` - Pause running scrape
- `resumeScrape()` - Resume paused scrape
- `stopScrape()` - Stop running scrape
- `getLatestResults(limit)` - Get latest results
- `getLatestChanges()` - Get new/updated resources
- `getRecentJobs(limit)` - Get job history
- `getRecentLogs(limit)` - Get activity logs
- `getStatistics()` - Get statistics

**Test**:
```python
# In Script Console
import exchangeScraper.api as api

# Should return True
connected = api.testConnection()
print connected

# Should return dictionary with status
status = api.getScraperStatus()
print status
```

### 3. Import notifications Module

**Purpose**: Send email and ntfy notifications

**Steps**:
1. Right-click `exchangeScraper` package
2. Select: **New** > **Script Module**
3. Name: `notifications`
4. Open file: `gateway-scripts/exchangeScraperNotifications.py`
5. Copy entire contents (231 lines)
6. Paste into Designer
7. Save

**Functions Provided**:
- `sendEmailNotification(subject, body)` - Send email
- `sendNtfyNotification(title, message, priority)` - Send ntfy push
- `notifyScrapeComplete(jobId)` - Auto-notification on completion
- `testEmailNotification()` - Test email setup
- `testNtfyNotification()` - Test ntfy setup

**Configuration Required**:
- SMTP profile named "default" (Gateway Config > Email > SMTP)
- Database configuration (notification settings in `scraper_config` table)

**Test**:
```python
# In Script Console
import exchangeScraper.notifications as notif

# Test ntfy (no SMTP required)
notif.testNtfyNotification()
# Check ntfy.sh or your ntfy app for message

# Test email (requires SMTP configuration)
notif.testEmailNotification()
```

### 4. Import scheduler Module

**Purpose**: Scheduling, automation, and manual control

**Steps**:
1. Right-click `exchangeScraper` package
2. Select: **New** > **Script Module**
3. Name: `scheduler`
4. Open file: `gateway-scripts/exchangeScraperScheduler.py`
5. Copy entire contents (219 lines)
6. Paste into Designer
7. Save

**Functions Provided**:
- `checkAndRunSchedule()` - Check if scheduled scrape should run (call from Timer Script)
- `manualTrigger()` - Trigger scrape manually
- `pauseCurrentScrape()` - Pause current scrape
- `resumeCurrentScrape()` - Resume paused scrape
- `stopCurrentScrape()` - Stop current scrape
- `updateScheduleSettings(enabled, intervalDays)` - Update schedule
- `onScrapeComplete(jobId)` - Callback when scrape completes (sends notifications)

**Test**:
```python
# In Script Console
import exchangeScraper.scheduler as scheduler

# Get current configuration
from exchangeScraper import api
config = api.getScraperServiceUrl()
print config

# Trigger manual scrape (this will start a real scrape!)
result = scheduler.manualTrigger()
print result

# Check status
status = api.getScraperStatus()
print "Job ID:", status.get('job_id')
print "Status:", status.get('status')
```

## Verification Checklist

After importing all three modules:

### Visual Check in Designer
- [ ] `Scripts` folder contains `exchangeScraper` package
- [ ] `exchangeScraper` contains 3 modules: `api`, `notifications`, `scheduler`
- [ ] Each module shows green icon (no compile errors)
- [ ] Each module has code content (not empty)

### Functional Tests

Run these in Script Console:

```python
# Test 1: API connectivity
import exchangeScraper.api as api
assert api.testConnection() == True, "API connection failed"
print "✓ API connected"

# Test 2: Get statistics (should show 512 resources)
stats = api.getStatistics()
assert stats['statistics']['total_resources'] == 512, "Wrong resource count"
print "✓ Database accessible:", stats['statistics']['total_resources'], "resources"

# Test 3: Get status
status = api.getScraperStatus()
print "✓ Status retrieved:", status.get('status', 'idle')

# Test 4: Notifications module loads
import exchangeScraper.notifications as notif
print "✓ Notifications module loaded"

# Test 5: Scheduler module loads
import exchangeScraper.scheduler as scheduler
print "✓ Scheduler module loaded"

print "\n✓✓✓ All modules imported successfully! ✓✓✓"
```

Expected output:
```
✓ API connected
✓ Database accessible: 512 resources
✓ Status retrieved: idle
✓ Notifications module loaded
✓ Scheduler module loaded

✓✓✓ All modules imported successfully! ✓✓✓
```

## Common Issues

### Import Error: "No module named exchangeScraper"
**Cause**: Package not created or wrong name
**Fix**:
- Verify package exists in Scripts folder
- Check spelling: `exchangeScraper` (exact case)
- Restart Designer

### Script Has Compile Errors (Red Icon)
**Cause**: Copy/paste issue or Jython 2.7 syntax error
**Fix**:
- Check for hidden characters
- Verify entire file copied (check line count)
- Look for Python 3 syntax (should be Python 2.7)

### api.testConnection() Returns False
**Cause**: Scraper service not running or wrong URL
**Fix**:
- Check service: `curl http://localhost:5000/health`
- Verify database config: `SELECT scraper_service_url FROM scraper_config WHERE id = 1`
- Update URL if needed: Use `host.docker.internal:5000` for Docker-to-host

### Database Connection Errors
**Cause**: Named query database connection not created
**Fix**:
- Gateway Config > Databases > Connections
- Create connection named `exchange_scraper_db`
- Use JDBC URL: `jdbc:postgresql://postgres:5432/exchange_scraper`

## Next Steps

After successful import:

1. **Create Named Queries** (see `named-queries/README.md`)
2. **Set up Gateway Timer Script** (see QUICK_START.md Step 4)
3. **Test Manual Scrape** (see QUICK_START.md Step 6)
4. **Build Perspective Dashboard** (see `docs/PERSPECTIVE_DASHBOARD.md`)

## Reference

- Source files: `ignition-project/gateway-scripts/`
- Full setup guide: `docs/IGNITION_SETUP.md`
- API documentation: `docs/TESTING_GUIDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
