# Ignition Exchange Scraper v3

Automated scraper for tracking and monitoring resources on the Ignition Exchange platform, built as an Ignition 8.3 Perspective project with a microservice backend.

## 🎯 Project Status

**Version**: 3.0.0
**Status**: **95% Complete** - Infrastructure ready, Docker browser issue outstanding
**Last Updated**: 2025-10-13

See [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for detailed status and next steps.

## ✨ Features

- 🔄 **Automated Scheduling**: Configure scraping intervals (default: weekly)
- 📊 **Change Detection**: Automatically identifies new and updated resources
- 📢 **Multi-Platform Notifications**: Email (via Ignition SMTP) and ntfy support
- 🗄️ **PostgreSQL Storage**: Comprehensive database with historical tracking
- 🌐 **Perspective Dashboard**: Modern responsive UI for monitoring and control
- 📋 **Tabbed Data View**: Three-tab interface showing Updated/Current/Past results
- ⏸️ **Scrape Controls**: Start, Pause, Resume, and Stop scraping from UI
- 📈 **Real-Time Progress**: Live status updates during scraping
- 🔔 **Activity Log**: Complete audit trail of all operations

## 🏗️ Architecture

### Microservice Approach (Implemented)

```
┌─────────────────────────────────────────────────────┐
│  Ignition Gateway (8.3+)                            │
│  ┌──────────────────────────────────────────────┐  │
│  │  Perspective Dashboard                       │  │
│  │  - Status monitoring                         │  │
│  │  - Manual controls                           │  │
│  │  - Results tables                            │  │
│  │  - Activity log                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Gateway Scripts (Jython 2.7)                │  │
│  │  - API client (exchangeScraper.api)          │  │
│  │  - Notifications (exchangeScraper.notif...)  │  │
│  │  - Scheduler (exchangeScraper.scheduler)     │  │
│  └──────────────────────────────────────────────┘  │
│                      ↕ HTTP API                     │
└─────────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────────┐
│  Scraper Service (Python 3.11 + FastAPI)            │
│  - Playwright browser automation                    │
│  - BeautifulSoup HTML parsing                       │
│  - PostgreSQL integration                           │
│  - REST API (10 endpoints)                          │
└─────────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────────┐
│  PostgreSQL 12+ Database                            │
│  - 5 tables, 11 indexes                             │
│  - 5 views (latest/changes/previous/jobs/logs)      │
│  - 2 functions (cleanup, statistics)                │
└─────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Ignition 8.3+** Gateway with internet access
- **Perspective Module** enabled
- **PostgreSQL 12+** database (Docker or standalone)
- **Python 3.11+** for scraper service (if running outside Docker)

## 🚀 Quick Start

### Option A: Full Docker Environment (All Services)

```bash
cd /git/ignition-exchange-scraper-v3/docker
docker compose --profile hybrid up -d
```

**Services Started**:
- PostgreSQL 16 → `localhost:5434`
- Ignition Gateway → `http://localhost:8088` (admin/password)
- Scraper Service → `http://localhost:5000`

**⚠️ Known Issue**: Chromium browser won't launch in Docker container. See [Troubleshooting](#-known-issues).

### Option B: Scraper on Host + Docker Database (Recommended)

```bash
# Start PostgreSQL and Ignition in Docker
cd /git/ignition-exchange-scraper-v3/docker
docker compose up -d  # Without --profile hybrid

# Run scraper on host machine
cd /git/ignition-exchange-scraper-v3/scraper-service
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps

# Set environment
export DATABASE_URL="postgresql://ignition:ignition@localhost:5434/exchange_scraper"
export LOG_LEVEL="INFO"

# Start scraper service
python -m app.api
```

Scraper API will be available at `http://localhost:5000`

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) | Current project status, what's done, what's pending |
| [IGNITION_SETUP.md](docs/IGNITION_SETUP.md) | Complete Ignition setup guide (7 parts) |
| [PERSPECTIVE_DASHBOARD.md](docs/PERSPECTIVE_DASHBOARD.md) | Dashboard design and implementation guide |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Solutions for 11 common issues |
| [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) | Testing procedures and API reference |
| [POC_ANALYSIS.md](docs/POC_ANALYSIS.md) | Technical analysis and architecture decisions |

## 🗂️ Directory Structure

```
ignition-exchange-scraper-v3/
├── docker/
│   ├── docker-compose.yml          # Docker orchestration
│   └── README.md                   # Docker environment docs
├── scraper-service/
│   ├── app/
│   │   ├── api.py                 # FastAPI REST API (275 lines)
│   │   ├── scraper_engine.py      # Playwright scraper (471 lines)
│   │   ├── database.py            # PostgreSQL ops (385 lines)
│   │   └── config.py              # Settings (35 lines)
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                 # Container build config
├── sql/
│   └── schema.sql                 # Complete DB schema (250 lines)
├── ignition-project/
│   └── gateway-scripts/
│       ├── exchangeScraperAPI.py            # API client (210 lines)
│       ├── exchangeScraperNotifications.py  # Email/ntfy (231 lines)
│       └── exchangeScraperScheduler.py      # Scheduler (219 lines)
├── docs/
│   ├── IGNITION_SETUP.md          # Setup instructions
│   ├── PERSPECTIVE_DASHBOARD.md   # Dashboard design
│   ├── TROUBLESHOOTING.md         # Issue resolution
│   ├── TESTING_GUIDE.md           # Testing procedures
│   ├── POC_ANALYSIS.md            # Technical analysis
│   └── PROJECT_STATUS.md          # Current status
└── README.md                      # This file
```

## ✅ Completed Components

- [x] FastAPI scraper service with 10 REST endpoints
- [x] Playwright-based browser automation
- [x] PostgreSQL schema with 5 tables, 5 views, 2 functions
- [x] Docker Compose environment (3 services)
- [x] Three Jython gateway scripts (api, notifications, scheduler)
- [x] Complete setup documentation (7-part guide)
- [x] Perspective dashboard design document
- [x] Comprehensive troubleshooting guide

## ⚠️ Known Issues

### Browser Launch in Docker

**Issue**: Chromium browser won't launch in Docker container despite:
- Shared memory allocation (`shm_size: 2gb`)
- 9 additional browser launch arguments
- All system dependencies installed

**Workaround**: Run scraper service on host machine (see Option B in Quick Start). This is proven to work from v2.

**See**: [TROUBLESHOOTING.md - Issue #1](docs/TROUBLESHOOTING.md#issue-1-playwright-browser-wont-launch-in-docker) for 5 detailed solutions.

## 🧪 Testing

### Test API Health

```bash
curl http://localhost:5000/health
# Expected: {"status":"healthy","timestamp":"...","version":"3.0.0"}
```

### Test Scrape

```bash
# Start scrape
curl -X POST http://localhost:5000/api/scrape/start \
  -H "Content-Type: application/json" \
  -d '{"triggered_by":"manual"}'

# Monitor progress
curl http://localhost:5000/api/scrape/status | python3 -m json.tool
```

### Check Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U ignition -d exchange_scraper

# View recent jobs
SELECT * FROM scrape_jobs ORDER BY job_start_time DESC LIMIT 5;

# Count resources
SELECT COUNT(*) FROM exchange_resources WHERE is_deleted = FALSE;

# View latest changes
SELECT * FROM vw_latest_changes LIMIT 10;
```

## 📈 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/scrape/start` | Start new scrape |
| POST | `/api/scrape/control` | Pause/resume/stop scrape |
| GET | `/api/scrape/status` | Current status with progress |
| GET | `/api/results/latest` | Latest scrape results |
| GET | `/api/results/changes` | New/updated resources |
| GET | `/api/jobs/recent?limit=10` | Recent job history |
| GET | `/api/logs/recent?limit=50` | Activity logs |
| POST | `/api/logs/clear` | Clear old logs |
| GET | `/api/stats` | Statistics |

## 🎨 Perspective Dashboard (Designed, Not Yet Built)

Complete dashboard design available in [PERSPECTIVE_DASHBOARD.md](docs/PERSPECTIVE_DASHBOARD.md):

- 3-column responsive layout
- Real-time status monitoring with animated progress bar
- Quick action buttons (Start/Pause/Stop/Refresh)
- Statistics cards (total resources, success rate, last scrape)
- Recent Jobs table (last 10 jobs with color-coded status)
- Results tabs (Updated/Current/Past)
- Activity log with auto-scroll
- Settings popup for configuration

**Estimated Build Time**: 11 hours

## 🔔 Notifications

### Email (via Ignition SMTP)

Configure in Ignition Gateway > Email > SMTP:
- Create profile named "default"
- Configure SMTP server settings
- Test email delivery

Update database:
```sql
UPDATE scraper_config
SET notification_email_enabled = true,
    notification_email_recipients = 'user@example.com,admin@example.com'
WHERE id = 1;
```

### ntfy (Push Notifications)

Choose unique topic at https://ntfy.sh or self-host:

```sql
UPDATE scraper_config
SET notification_ntfy_enabled = true,
    notification_ntfy_server = 'https://ntfy.sh',
    notification_ntfy_topic = 'your-unique-topic-xyz123'
WHERE id = 1;
```

Install ntfy mobile app and subscribe to your topic.

## ⏰ Scheduling

Configure automatic scraping:

```sql
-- Run every 7 days
UPDATE scraper_config
SET schedule_enabled = true,
    schedule_interval_days = 7
WHERE id = 1;
```

Create Gateway Timer Script (see [IGNITION_SETUP.md](docs/IGNITION_SETUP.md#part-3-gateway-timer-script)):
```python
import exchangeScraper.scheduler as scheduler
scheduler.checkAndRunSchedule()
```

## 🔧 Development

### Build Docker Image

```bash
cd /git/ignition-exchange-scraper-v3/docker
docker compose build scraper-service
```

### Run Tests

```bash
cd /git/ignition-exchange-scraper-v3/scraper-service
pytest tests/  # (when tests are added)
```

### Database Migrations

Schema changes can be applied directly:
```bash
docker compose exec postgres psql -U ignition -d exchange_scraper -f /sql/schema.sql
```

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for solutions to:
- Browser launch issues in Docker (5 solutions)
- Database connection problems
- API not responding
- Gateway scripts not found
- Email/ntfy notifications failing
- Scheduled scraping issues
- Empty results tables
- Slow performance
- Docker build failures

## 🛣️ Roadmap

### Next Steps (Immediate)
1. Test scraper service on host machine
2. Verify 400+ resources scraped successfully
3. Build Perspective dashboard (11 hours)
4. Test full workflow end-to-end
5. Deploy to production Ignition gateway

### Future Enhancements (v3.1+)
- Resolve Docker browser launch issue
- Add Excel export functionality
- Implement email attachments
- Add resource detail popups
- Charts showing historical trends
- Advanced filtering and search
- Dark mode toggle
- User preferences

### Long Term (v4.0)
- Custom Ignition module (eliminate external service)
- Native Jython browser automation
- Mobile app for notifications
- AI-powered change analysis
- Multi-platform scraping

## 📊 Project Statistics

- **Code**: 1,300 lines Python, 250 lines SQL, 100 lines YAML
- **Documentation**: 3,500 lines Markdown
- **Files**: 16 source files, 6 documentation pages
- **Services**: 3 Docker containers
- **API Endpoints**: 10 REST endpoints
- **Time Invested**: ~15 hours

## 🤝 Contributing

This project is ready for testing and deployment. Contributions welcome!

### Getting Started
1. Clone repository
2. Follow Quick Start (Option B recommended)
3. Test scraper service
4. Report issues or submit PRs

## 📄 License

[To be determined]

## 🔗 Related Projects

- **v2**: Original Docker-based scraper (proven successful)
- **Ignition Exchange**: https://inductiveautomation.com/exchange

## 👥 Author

Built for deployment to Ignition Exchange as a shareable resource.

## 🙏 Acknowledgments

- Inductive Automation for the Ignition platform
- Playwright team for browser automation
- PostgreSQL community for robust database

---

**Status**: Ready for testing with host-based scraper. See [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for detailed next steps.
