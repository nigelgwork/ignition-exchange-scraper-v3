# Decision Required: Implementation Approach

## Summary

The new repository for `ignition-exchange-scraper-v3` has been created with:

✅ PostgreSQL database schema
✅ Docker Compose test environment (Ignition 8.3 + PostgreSQL)
✅ Project structure ready for development
✅ PoC analysis completed

## Critical Finding: Native Jython Won't Work

After analyzing the technical requirements, **native Jython scripting cannot scrape all Exchange resources**.

### Why?

1. **JavaScript-heavy site** - Exchange uses React for client-side rendering
2. **Dynamic loading** - Resources load on-demand (not in initial HTML)
3. **Requires ~100+ button clicks** - "Load more" must be clicked repeatedly
4. **No public API** - Exchange doesn't expose programmatic access
5. **Jsoup limitation** - Can only parse static HTML, cannot execute JavaScript

### Test Results

- **Native Jython**: ~20 resources scraped (5% coverage) ❌
- **Required**: 400+ resources scraped (100% coverage) ✅ (only possible with browser automation)

## Three Options to Proceed

### Option 1: Docker Microservice (RECOMMENDED)

**What it is:**
- Ignition project provides Perspective UI (primary interface)
- External Docker container handles scraping (background service)
- Clean HTTP API communication between them

**Architecture:**
```
┌─────────────────────────────────┐
│   Ignition Gateway             │
│   ┌─────────────────────────┐  │
│   │  Perspective Dashboard   │  │ ← User sees this
│   │  - Status display        │  │
│   │  - Controls              │  │
│   │  - Data tables           │  │
│   └─────────────────────────┘  │
│   ┌─────────────────────────┐  │
│   │  Gateway Scripts        │  │
│   │  - API client           │  │
│   │  - Notifications        │  │
│   │  - Scheduling           │  │
│   └─────────────────────────┘  │
└─────────────────────────────────┘
               ↕ HTTP API
┌─────────────────────────────────┐
│   Scraper Service (Docker)      │
│   - Playwright automation       │
│   - Gets 100% of resources      │
│   - Proven (v2 works)           │
└─────────────────────────────────┘
```

**Pros:**
- ✅ **100% resource coverage guaranteed**
- ✅ **Proven technology** (v2 implementation works perfectly)
- ✅ **Clean separation** of concerns
- ✅ **Easy deployment** (`docker compose up` command)
- ✅ **User experience** is 100% Ignition/Perspective
- ✅ **Maintainable** - separate code paths for UI and scraping
- ✅ **Can submit to Exchange** with documentation of requirement

**Cons:**
- ❌ Requires Docker deployment alongside Ignition
- ❌ Not a pure Ignition solution

**Timeline:** 6-7 weeks

---

### Option 2: Custom Ignition Module

**What it is:**
- Build custom Ignition module (.modl file)
- Bundle Python 3 runtime + Playwright inside module
- Install like any other Ignition module

**Architecture:**
```
┌─────────────────────────────────┐
│   Custom Ignition Module        │
│   ┌─────────────────────────┐  │
│   │  Python 3 Runtime       │  │
│   │  Playwright + Chromium  │  │
│   │  (~200-300 MB)          │  │
│   └─────────────────────────┘  │
│   ┌─────────────────────────┐  │
│   │  Java Bridge            │  │
│   │  Exposes functions to   │  │
│   │  Ignition gateway       │  │
│   └─────────────────────────┘  │
└─────────────────────────────────┘
               ↕
┌─────────────────────────────────┐
│   Ignition Project              │
│   - Calls module functions      │
│   - Perspective dashboard       │
└─────────────────────────────────┘
```

**Pros:**
- ✅ Installed like any module (no Docker needed)
- ✅ Native Ignition experience
- ✅ Self-contained solution

**Cons:**
- ❌ **Complex development** (Ignition SDK + Java + Python bridge)
- ❌ **Large module size** (~200-300 MB with browser)
- ❌ **Module signing** requirements
- ❌ **Resource intensive** on gateway
- ❌ **Maintenance burden** (updates, security patches)
- ❌ **May not pass Exchange review** (unconventional architecture)
- ❌ **3-4 weeks additional development time**

**Technical Challenges:**
1. Bundling Chromium browser in .modl
2. Managing separate Python 3 runtime from Jython
3. Java ↔ Python 3 bridge (JNI or similar)
4. Gateway resource consumption concerns
5. Cross-platform compatibility (Windows, Linux, macOS)

**Timeline:** 10-12 weeks

---

### Option 3: Hybrid with Degraded Fallback

**What it is:**
- Ignition project checks for scraper service
- If available: Use service (100% coverage)
- If not: Fall back to Jython (~5% coverage) with prominent warning

**Architecture:**
```
Ignition Gateway
    ↓
Check: Is scraper service available?
    ↓
   YES → Use Docker service (100% coverage)
    ↓
    NO → Use Jython Jsoup (~5% coverage)
          + Show warning to user
          + Suggest installing service
```

**Pros:**
- ✅ Works in both scenarios
- ✅ User has choice
- ✅ Pure Ignition option (with limitations)

**Cons:**
- ❌ **Poor user experience** with fallback (only 5% coverage)
- ❌ **Dual code paths** to maintain
- ❌ **Confusion** about capabilities
- ❌ **Not recommended** - partial data is misleading

**Timeline:** 7-8 weeks

---

## Recommendation: Option 1 (Docker Microservice)

### Rationale

1. **Only option guaranteeing 100% coverage**
2. **Proven working solution** (v2 is rock-solid)
3. **Best user experience** (full functionality)
4. **Clean architecture** (maintainable)
5. **Reasonable deployment** (Docker is widely adopted)
6. **Can still be on Exchange** with clear documentation

### Deployment for End Users

Users would:

1. **Import Ignition project** (standard .zip import)
2. **Run Docker Compose command:**
   ```bash
   docker compose up -d
   ```
3. **Configure in Perspective** (standard UI)

That's it. The Docker service runs in the background like a database would.

### Exchange Submission Approach

**Title:** "Ignition Exchange Resource Monitor"

**Tagline:** "Track and monitor all Ignition Exchange resources with automated scheduling and change detection"

**Description:**
> Complete monitoring solution for the Ignition Exchange platform. Features a beautiful Perspective dashboard for viewing resources, detecting changes, and configuring notifications.
>
> **Requirements:**
> - Ignition 8.3+ with Perspective
> - PostgreSQL database
> - Docker service for web scraping (included, one-command setup)
>
> The companion Docker service handles web scraping in the background, while the Ignition project provides the complete user interface and control system.

**Category:** Utilities / Monitoring

**Why it will be accepted:**
- Primary interface is 100% Ignition/Perspective
- External dependency is well-documented
- Similar to how projects require databases
- Provides real value to community
- Professional documentation and setup

---

## Next Steps (Pending Your Decision)

### If Option 1 (Docker Microservice):

1. Copy proven scraper from v2 → v3 service
2. Create FastAPI wrapper for HTTP API
3. Build Perspective dashboard (3-column layout)
4. Implement gateway scripts (API client)
5. Add notifications (email + ntfy)
6. Full integration testing
7. Documentation and Exchange prep

**Timeline:** 6-7 weeks

### If Option 2 (Custom Module):

1. Research Ignition SDK module development
2. Design Java ↔ Python 3 bridge architecture
3. Create module scaffolding
4. Bundle Python 3 + Playwright + Chromium
5. Implement gateway-side functions
6. Build Perspective dashboard
7. Module testing and signing
8. Documentation

**Timeline:** 10-12 weeks

### If Option 3 (Hybrid):

Not recommended - creates poor user experience with 95% missing data in fallback mode.

---

## Testing Environment Ready

The Docker test environment is ready to use:

```bash
cd /git/ignition-exchange-scraper-v3/docker
docker compose up -d

# Access:
# Ignition: http://localhost:8088 (admin/password)
# PostgreSQL: localhost:5432 (ignition/ignition)
```

Once you choose an approach, we'll start building immediately!

---

## Files Created

```
/git/ignition-exchange-scraper-v3/
├── README.md                       # Project overview
├── .gitignore                      # Git ignore rules
├── sql/
│   └── schema.sql                  # PostgreSQL schema (ready to use)
├── docker/
│   ├── docker-compose.yml          # Test environment
│   └── README.md                   # Docker documentation
├── scraper-service/                # Ready for Option 1
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── __init__.py
├── docs/
│   ├── POC_ANALYSIS.md            # Technical analysis
│   └── DECISION_REQUIRED.md       # This file
└── tests/
    └── jsoup_test.py              # PoC test script
```

---

## My Strong Recommendation

**Go with Option 1 (Docker Microservice)**

It's the only practical solution that:
- Guarantees all resources are scraped
- Has proven technology behind it
- Provides excellent user experience
- Is maintainable long-term
- Can realistically be completed in 6-7 weeks

Option 2 (custom module) is technically interesting but adds significant complexity, development time, and maintenance burden for questionable benefit.

**What do you think? Ready to proceed with Option 1?**
