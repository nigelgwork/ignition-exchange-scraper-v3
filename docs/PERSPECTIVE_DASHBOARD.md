# Perspective Dashboard Design - Exchange Scraper v3

## Overview

The Perspective dashboard provides a web-based interface for monitoring and controlling the Exchange scraper. It follows a 3-column responsive layout similar to the v2 Docker dashboard.

## Dashboard Layout

### Main View: `/ExchangeScraper/Main`

```
┌─────────────────────────────────────────────────────────────────┐
│  Exchange Scraper Dashboard                        [Settings ⚙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   STATUS      │  │ QUICK ACTIONS │  │  STATISTICS   │       │
│  │               │  │               │  │               │       │
│  │ • Current:    │  │ [▶ Start]     │  │ Total: 425    │       │
│  │   Idle        │  │ [⏸ Pause]     │  │ Updated: 12   │       │
│  │               │  │ [⏹ Stop]      │  │ Last: 2h ago  │       │
│  │ • Progress:   │  │               │  │               │       │
│  │   [████░░] 45%│  │ [🔄 Refresh]  │  │ Jobs: 15      │       │
│  │               │  │               │  │ Success: 98%  │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  RECENT JOBS                                             │   │
│  │  ┌────┬───────────┬────────┬───────────┬─────────┐     │   │
│  │  │ ID │ Start Time│ Status │ Resources │ Changes │     │   │
│  │  ├────┼───────────┼────────┼───────────┼─────────┤     │   │
│  │  │ 15 │ 10:30 AM  │ ✓ Done │ 425       │ 12      │     │   │
│  │  │ 14 │ 08:15 AM  │ ✓ Done │ 423       │ 8       │     │   │
│  │  └────┴───────────┴────────┴───────────┴─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SCRAPE RESULTS              [Updated] [Current] [Past]  │   │
│  │  ┌─────┬──────────────┬─────────┬──────────┬──────────┐ │   │
│  │  │ ID  │ Title        │ Version │ Updated  │ Author   │ │   │
│  │  ├─────┼──────────────┼─────────┼──────────┼──────────┤ │   │
│  │  │2819 │ Vision Utils │ 2.1.0   │ 2d ago   │ Inductive│ │   │
│  │  │2754 │ Tag Manager  │ 1.8.3   │ 1w ago   │ PGE      │ │   │
│  │  └─────┴──────────────┴─────────┴──────────┴──────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ACTIVITY LOG                                    [Clear] │   │
│  │  • 10:30 AM - Scrape completed: 425 resources, 12 new   │   │
│  │  • 10:15 AM - Started scheduled scrape                   │   │
│  │  • 08:20 AM - Scrape completed: 423 resources, 8 new    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Views Structure

### 1. Main Container View

**Path**: `ExchangeScraper/Main`
**Type**: Coordinate Container (responsive)
**Size**: 100% width × 100% height

**Components**:
- Header bar with title and settings button
- Status panel (top-left)
- Actions panel (top-center)
- Statistics panel (top-right)
- Recent Jobs table (middle)
- Results tabs container (lower-middle)
- Activity log (bottom)

### 2. Status Panel

**Component**: Flex Container (vertical)
**Bindings**: Tag bindings to scraper status

**Elements**:
- **Current Status Label**
  - Binding: `{view.custom.currentStatus}`
  - Expression: Query `scraper_status` tag or script binding
  - Style: Dynamic color based on status
    - `idle` → Gray
    - `running` → Blue (animated pulse)
    - `paused` → Orange
    - `failed` → Red
    - `completed` → Green

- **Progress Bar**
  - Component: Progress Bar
  - Binding: `{view.custom.progress.percentage}`
  - Visible: Only when status = 'running' or 'paused'
  - Animation: Indeterminate when percentage = 0

- **Current Item Label**
  - Binding: `{view.custom.progress.currentItem}`
  - Shows: Currently scraping resource title
  - Truncate: max 40 characters

- **Elapsed Time**
  - Binding: `{view.custom.elapsedSeconds}`
  - Transform: Expression to format as "HH:MM:SS"

### 3. Quick Actions Panel

**Component**: Flex Container (vertical)
**Button Configuration**:

**Start Button**:
```python
# On Click Event Handler
import exchangeScraper.scheduler as scheduler

result = scheduler.manualTrigger()
if result.get('success'):
    system.perspective.print("Scrape started successfully")
else:
    system.perspective.openPopup('error', 'Error', result.get('message'))
```

**Pause Button**:
```python
# On Click Event Handler
import exchangeScraper.scheduler as scheduler

result = scheduler.pauseCurrentScrape()
if result.get('success'):
    system.perspective.print("Scrape paused")
```

**Stop Button**:
```python
# On Click Event Handler
import exchangeScraper.scheduler as scheduler

result = scheduler.stopCurrentScrape()
if result.get('success'):
    system.perspective.print("Scrape stopped")
```

**Refresh Button**:
```python
# On Click Event Handler
self.getSibling("RecentJobsTable").refreshBinding("data")
self.getSibling("ResultsTable").refreshBinding("data")
self.getSibling("ActivityLog").refreshBinding("data")
```

**Button States**:
- Start: Enabled only when status = 'idle'
- Pause: Enabled only when status = 'running'
- Stop: Enabled only when status = 'running' or 'paused'
- Refresh: Always enabled

### 4. Statistics Panel

**Component**: Flex Container (horizontal wrap)
**Data Source**: Named Query binding

**Named Query**: `ExchangeScraper/GetStatistics`
```sql
SELECT
    (SELECT COUNT(*) FROM exchange_resources WHERE is_deleted = FALSE) as total_resources,
    (SELECT COUNT(*) FROM exchange_resources WHERE last_scraped_date >= NOW() - INTERVAL '7 days') as recently_updated,
    (SELECT MAX(job_start_time) FROM scrape_jobs WHERE status = 'completed') as last_scrape_time,
    (SELECT COUNT(*) FROM scrape_jobs) as total_jobs,
    (SELECT COUNT(*) FROM scrape_jobs WHERE status = 'completed') as completed_jobs,
    (SELECT COUNT(*) FROM scrape_jobs WHERE status = 'failed') as failed_jobs
```

**Display Cards**:
- Total Resources (large number)
- Recently Updated (last 7 days)
- Last Scrape (relative time, e.g., "2 hours ago")
- Total Jobs
- Success Rate (percentage)

### 5. Recent Jobs Table

**Component**: Table (Power Table or Perspective Table)
**Query**: Named Query binding

**Named Query**: `ExchangeScraper/GetRecentJobs`
```sql
SELECT
    j.id AS "Job ID",
    j.job_start_time AS "Start Time",
    j.status AS "Status",
    j.resources_found AS "Resources",
    j.changes_detected AS "Changes",
    CASE
        WHEN j.elapsed_seconds < 60 THEN j.elapsed_seconds || 's'
        WHEN j.elapsed_seconds < 3600 THEN FLOOR(j.elapsed_seconds / 60) || 'm'
        ELSE FLOOR(j.elapsed_seconds / 3600) || 'h ' || FLOOR((j.elapsed_seconds % 3600) / 60) || 'm'
    END AS "Duration",
    j.triggered_by AS "Triggered By"
FROM scrape_jobs j
ORDER BY j.job_start_time DESC
LIMIT 10
```

**Table Configuration**:
- Columns: Job ID, Start Time, Status, Resources, Changes, Duration, Triggered By
- Row Height: 40px
- Selection Mode: Single row
- Status Column: Use style class for color coding
  - `completed` → green background
  - `failed` → red background
  - `running` → blue background
  - `paused` → orange background

**Column Styles**:
```json
{
  "Status": {
    "render": "auto",
    "styles": {
      "completed": {
        "backgroundColor": "#4caf50",
        "color": "#ffffff"
      },
      "failed": {
        "backgroundColor": "#f44336",
        "color": "#ffffff"
      },
      "running": {
        "backgroundColor": "#2196f3",
        "color": "#ffffff"
      }
    }
  }
}
```

### 6. Results Tabs Container

**Component**: Tab Container
**Tabs**: Updated | Current | Past

**Tab 1: Updated (Changes)**
- **Named Query**: `ExchangeScraper/GetLatestChanges`
```sql
SELECT * FROM vw_latest_changes
ORDER BY "Scraped At" DESC
```

**Tab 2: Current (Latest Results)**
- **Named Query**: `ExchangeScraper/GetLatestResults`
```sql
SELECT * FROM vw_latest_results
ORDER BY "Resource ID"
```

**Tab 3: Past (Previous Results)**
- **Named Query**: `ExchangeScraper/GetPreviousResults`
```sql
SELECT * FROM vw_previous_results
ORDER BY "Resource ID"
```

**Table Configuration** (all tabs):
- Columns: Resource ID, Title, Version, Updated Date, Developer ID, Contributor, Tagline
- Filters: Enable column filters
- Export: Enable CSV export
- Pagination: 25 rows per page
- URL Column: Make "Title" clickable, opens resource URL in new tab

### 7. Activity Log

**Component**: Flex Repeater or Label List
**Query**: Named Query binding with polling (every 5 seconds when scraping)

**Named Query**: `ExchangeScraper/GetActivityLog`
```sql
SELECT
    timestamp,
    level,
    message
FROM activity_log
ORDER BY timestamp DESC
LIMIT 50
```

**Display Format**:
```
[HH:MM:SS] MESSAGE
```

**Styling**:
- `error` level → Red text
- `warning` level → Orange text
- `info` level → Default text
- Auto-scroll to bottom when new entries added
- Max height: 200px with scroll

## Custom Properties (View Level)

Define these at the Main view level:

```json
{
  "currentStatus": "idle",
  "elapsedSeconds": 0,
  "progress": {
    "current": 0,
    "total": 0,
    "currentItem": "",
    "percentage": 0
  },
  "statistics": {
    "totalResources": 0,
    "recentlyUpdated": 0,
    "lastScrapeTime": null,
    "totalJobs": 0,
    "successRate": 0
  }
}
```

## Script Bindings

### Status Polling Script

**Property**: `custom.currentStatus`
**Type**: Script Transform on Polling
**Poll Rate**: 2000ms (2 seconds)

```python
import exchangeScraper.api as api

status = api.getScraperStatus()
if status:
    # Update multiple properties
    self.custom.currentStatus = status.get('status', 'idle')
    self.custom.elapsedSeconds = status.get('elapsed_seconds', 0)
    self.custom.progress = status.get('progress', {
        "current": 0,
        "total": 0,
        "currentItem": "",
        "percentage": 0
    })

    return status.get('status', 'idle')
else:
    return 'error'
```

### Statistics Polling Script

**Property**: `custom.statistics`
**Type**: Named Query binding with polling
**Poll Rate**: 30000ms (30 seconds)

## Responsive Design

### Breakpoints

**Desktop (> 1200px)**:
- 3-column layout for status/actions/statistics
- Full-width tables
- All elements visible

**Tablet (768px - 1200px)**:
- 2-column layout for status/actions/statistics
- Compact tables (hide tagline column)
- Smaller fonts

**Mobile (< 768px)**:
- Single column stack
- Collapsed tables (show only Title, Version, Updated)
- Hamburger menu for actions
- Tabs instead of columns for statistics

## Color Scheme

### Primary Colors
- Primary: `#0066cc` (Inductive Automation blue)
- Success: `#4caf50`
- Warning: `#ff9800`
- Error: `#f44336`
- Info: `#2196f3`

### Background Colors
- Main Background: `#f5f5f5`
- Card Background: `#ffffff`
- Header Background: `#333333`

### Text Colors
- Primary Text: `#212121`
- Secondary Text: `#757575`
- Disabled Text: `#bdbdbd`

## Named Queries to Create

Create these in Designer under **Project Browser > Named Queries > ExchangeScraper**:

1. `GetStatistics` - Dashboard statistics
2. `GetRecentJobs` - Last 10 jobs
3. `GetLatestResults` - Current scrape results (uses view)
4. `GetLatestChanges` - New/updated resources (uses view)
5. `GetPreviousResults` - Previous scrape results (uses view)
6. `GetActivityLog` - Recent log entries
7. `GetScraperConfig` - Configuration settings
8. `UpdateScheduleSettings` - Update schedule (used by settings popup)
9. `UpdateNotificationSettings` - Update notification config

## Settings Popup

**Path**: `ExchangeScraper/Popups/Settings`
**Size**: 600px × 800px

**Tabs**:
1. **Schedule** - Configure scrape interval and enable/disable
2. **Notifications** - Configure email and ntfy settings
3. **Advanced** - Service URL, mode selection

## Implementation Steps

### Phase 1: Basic Structure
1. Create Main view with Coordinate Container
2. Add header bar with title
3. Create 3 panels (Status, Actions, Statistics) as Flex Containers
4. Test layout responsiveness

### Phase 2: Status & Control
1. Add status labels and progress bar
2. Implement action buttons with gateway scripts
3. Add button state logic (enabled/disabled based on status)
4. Test manual scrape trigger

### Phase 3: Data Tables
1. Create all Named Queries
2. Add Recent Jobs table with binding
3. Create Results tab container with 3 tabs
4. Add tables to each tab with appropriate queries
5. Style status column with colors

### Phase 4: Activity Log
1. Add activity log component at bottom
2. Configure polling for real-time updates
3. Add auto-scroll behavior
4. Style by log level (error/warning/info)

### Phase 5: Statistics
1. Bind statistics query to view custom property
2. Create statistic cards/labels
3. Add relative time formatting for "Last Scrape"
4. Calculate and display success rate

### Phase 6: Settings Popup
1. Create Settings popup view
2. Add form inputs for schedule configuration
3. Add notification configuration forms
4. Wire up save button to named queries
5. Add validation

### Phase 7: Polish
1. Add loading spinners during queries
2. Add error handling popups
3. Implement refresh button
4. Add tooltips to buttons
5. Test on mobile devices

## Testing Checklist

- [ ] Start button triggers scrape
- [ ] Pause button pauses running scrape
- [ ] Stop button stops running scrape
- [ ] Status updates in real-time while scraping
- [ ] Progress bar animates during scrape
- [ ] Recent Jobs table updates after scrape completes
- [ ] Results tabs show correct data
- [ ] Activity log shows real-time messages
- [ ] Statistics update after scrape
- [ ] Settings popup saves changes to database
- [ ] Responsive layout works on tablet
- [ ] Responsive layout works on mobile
- [ ] Error messages display when API fails
- [ ] Refresh button updates all data

## Future Enhancements

- **Charts**: Add chart showing scrape history (resources over time)
- **Export**: Add "Export to Excel" button for results
- **Filters**: Add advanced filtering for results tables
- **Search**: Add search box to filter resources by title
- **Notifications UI**: Show notification history
- **User Preferences**: Save user's preferred tab, sort order
- **Dark Mode**: Toggle for dark theme
- **Job Details**: Click job row to see detailed log
- **Manual Entry**: Add form to manually add resources

## Notes

- All gateway scripts are already created in the `exchangeScraper` package
- Database views (`vw_latest_results`, etc.) are already defined in schema
- Color scheme matches Ignition's default Perspective theme
- Design is similar to v2 Docker dashboard for familiarity
- All queries use the `exchange_scraper_db` database connection

## Installation

See [IGNITION_SETUP.md](IGNITION_SETUP.md) for complete setup instructions including:
- Database connection configuration
- Gateway script installation
- Named query creation
- Perspective view import
