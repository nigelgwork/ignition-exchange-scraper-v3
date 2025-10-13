# Docker Test Environment

Complete test environment for Ignition Exchange Scraper v3 development.

## Services

- **postgres**: PostgreSQL 16 database (port 5432)
- **ignition**: Ignition 8.3 Gateway (port 8088)
- **scraper-service**: Optional external scraper (port 5000, only if hybrid approach needed)

## Quick Start

### Start Core Services (Ignition + PostgreSQL)

```bash
cd docker
docker compose up -d
```

This starts:
- PostgreSQL with `exchange_scraper` database initialized
- Ignition 8.3 Gateway with admin/password credentials

### Access Services

**Ignition Gateway:**
- URL: http://localhost:8088
- Username: `admin`
- Password: `password`

**PostgreSQL:**
- Host: `localhost`
- Port: `5432`
- Database: `exchange_scraper`
- Username: `ignition`
- Password: `ignition`

### Start with Scraper Service (Hybrid Approach)

If the native Jython approach doesn't work and you need the external scraper:

```bash
docker compose --profile hybrid up -d
```

## Useful Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ignition
docker compose logs -f postgres
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific
docker compose restart ignition
```

### Stop Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

### Database Access

```bash
# Connect to PostgreSQL CLI
docker compose exec postgres psql -U ignition -d exchange_scraper

# Run queries
docker compose exec postgres psql -U ignition -d exchange_scraper -c "SELECT * FROM scraper_config;"

# Import updated schema
docker compose exec -T postgres psql -U ignition -d exchange_scraper < ../sql/schema.sql
```

### Ignition Gateway

```bash
# View Ignition logs
docker compose exec ignition tail -f /usr/local/bin/ignition/logs/wrapper.log

# Backup Ignition gateway
docker compose exec ignition /usr/local/bin/ignition/gwcmd.sh --backup gateway-backup.gwbk

# Restore Ignition gateway
docker compose exec ignition /usr/local/bin/ignition/gwcmd.sh --restore gateway-backup.gwbk
```

## Initial Setup

After starting services for the first time:

1. **Access Ignition Gateway** at http://localhost:8088
2. **Complete Quick Start wizard** (if prompted)
3. **Configure database connection:**
   - Go to Config > Databases > Connections
   - Add new connection:
     - Name: `exchange_scraper_db`
     - Driver: PostgreSQL
     - Server: `postgres` (Docker service name) or `localhost` (from host)
     - Port: `5432`
     - Database: `exchange_scraper`
     - Username: `ignition`
     - Password: `ignition`
   - Test connection
   - Save

4. **Import project** (when ready):
   - Go to Config > Projects
   - Import project from `/restore` directory

## Troubleshooting

### PostgreSQL won't start

```bash
# Check logs
docker compose logs postgres

# Remove volume and restart
docker compose down -v
docker compose up -d
```

### Ignition won't start

```bash
# Check logs
docker compose logs ignition

# Check health
docker compose ps

# Restart
docker compose restart ignition
```

### Can't connect to database from Ignition

Make sure you're using the Docker service name `postgres` as the host (not `localhost`) when configuring the database connection within Ignition.

From your host machine (e.g., DBeaver), use `localhost:5432`.

### Ports already in use

If ports 8088 or 5432 are already in use, edit `docker-compose.yml` and change the port mappings:

```yaml
ports:
  - "8089:8088"  # Change host port to 8089
```

## Network Architecture

```
Host Machine
    │
    ├─ localhost:8088 ──→ Ignition Gateway (container)
    │                         │
    ├─ localhost:5432 ──→ PostgreSQL (container)
    │                         │
    └─ localhost:5000 ──→ Scraper Service (container, optional)
                              │
    All containers communicate via: exchange-scraper-net
```

## Data Persistence

All data is persisted in Docker volumes:
- `postgres-data`: PostgreSQL database files
- `ignition-data`: Ignition gateway configuration and projects
- `scraper-data`: Scraper service output files (if using hybrid)

These volumes persist even after `docker compose down`.

## Clean Slate

To completely reset the environment:

```bash
docker compose down -v
docker compose up -d
```

This removes all volumes and starts fresh.
