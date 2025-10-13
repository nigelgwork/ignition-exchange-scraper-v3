# Named Queries for Exchange Scraper Dashboard

This directory contains all the Named Queries needed for the Perspective dashboard.

## Setup Instructions

### Step 1: Create Database Connection

1. Open Ignition Gateway Config: http://localhost:8088
2. Login with credentials: **admin** / **password**
3. Navigate to: **Config > Databases > Connections**
4. Click **Create new Database Connection...**
5. Configure:
   - **Name**: `exchange_scraper_db`
   - **Connect URL**: `jdbc:postgresql://postgres:5432/exchange_scraper`
   - **Username**: `ignition`
   - **Password**: `ignition`
6. Click **Create New Database Connection**
7. Test the connection - should show "Valid"

### Step 2: Import Named Queries

Navigate to each SQL file in this directory and create the Named Queries in Designer:

1. Open Ignition Designer
2. Go to: **Project Browser > Data > Named Queries**
3. Right-click > **New Named Query**
4. For each query file:
   - Set the **Name** as specified in the filename
   - Set **Database** to `exchange_scraper_db`
   - Copy the SQL from the file
   - Save

## Named Queries List

1. **GetScraperStatus** - Get current scraper status
2. **GetRecentJobs** - Get recent job history (last 10)
3. **GetLatestResults** - Get all resources from latest scrape
4. **GetLatestChanges** - Get new/updated resources from latest scrape
5. **GetPreviousResults** - Get results from previous scrape
6. **GetRecentLogs** - Get recent activity logs
7. **GetStatistics** - Get scraper statistics
8. **GetConfig** - Get scraper configuration
9. **UpdateConfig** - Update scraper configuration

## Quick Import Script

Alternatively, you can use the Ignition scripting console to create these programmatically.
See `create_named_queries.py` for the script.
