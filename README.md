# Ignition Exchange Scraper v3

Automated scraper for tracking and monitoring resources on the Ignition Exchange platform, built as a native Ignition 8.3 project.

## Features

- 🔄 **Automated Scheduling**: Configure scraping intervals (default: weekly)
- 📊 **Change Detection**: Automatically compares new results with previous scrapes
- 📢 **Multi-Platform Notifications**: Email (via Ignition SMTP) and ntfy support
- 🗄️ **PostgreSQL Storage**: Efficient database storage with historical tracking
- 🌐 **Perspective Dashboard**: Modern responsive UI for monitoring and control
- 🎨 **Dark Mode**: Toggle between light and dark themes
- 📋 **Tabbed Data View**: Three-tab interface showing Updated/Current/Past results

## Architecture

This project explores three possible implementation approaches:

1. **Native Jython** (Current PoC) - Pure Ignition scripting with Jsoup
2. **Docker Microservice** (Fallback) - External scraper service with Perspective UI
3. **Custom Ignition Module** (Advanced) - Python 3 wrapper as Ignition module

## Prerequisites

- Ignition 8.3+ Gateway with internet access
- Perspective module enabled
- PostgreSQL 12+ database

## Quick Start (Development)

### Docker Test Environment

```bash
# Start test environment (Ignition + PostgreSQL)
cd docker
docker compose up -d

# Access Ignition Gateway
# URL: http://localhost:8088
# Username: admin
# Password: password

# PostgreSQL is available at localhost:5432
# Database: exchange_scraper
# Username: ignition
# Password: ignition
```

### Database Setup

The database schema is automatically initialized when using Docker Compose. For manual setup:

```bash
psql -U postgres -d exchange_scraper -f sql/schema.sql
```

## Project Status

**Phase 1: Proof of Concept** - Testing native Jython approach to determine feasibility.

## Directory Structure

```
ignition-exchange-scraper-v3/
├── sql/                        # Database schemas and migrations
├── docker/                     # Docker Compose test environment
├── ignition-project/          # Exportable Ignition project (when ready)
├── scraper-service/           # External scraper service (if needed)
├── docs/                      # Documentation
└── tests/                     # Test scripts
```

## Development Roadmap

- [x] Create repository structure
- [x] Design PostgreSQL schema
- [x] Set up Docker test environment
- [ ] Build native Jython PoC scraper
- [ ] Test PoC coverage (target: 100% of Exchange resources)
- [ ] Decide on final architecture approach
- [ ] Build Perspective dashboard
- [ ] Implement gateway scripting
- [ ] Add notification support
- [ ] Complete testing
- [ ] Prepare Exchange submission

## Contributing

This project is in active development. Contributions and suggestions welcome!

## License

[To be determined]

## Related Projects

This is a complete rewrite of [ignition-exchange-scraper-v2](https://github.com/[your-repo]/ignition-exchange-scraper-v2) designed to work as a native Ignition Exchange resource.
