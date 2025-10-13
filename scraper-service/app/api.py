"""
FastAPI application for Exchange scraper service
Provides REST API for Ignition gateway to trigger and monitor scraping
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from .scraper_engine import ScraperEngine
from .database import DatabaseManager
from .config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ignition Exchange Scraper Service",
    description="Web scraping service for the Ignition Exchange platform",
    version="3.0.0"
)

# Global state
scraper_engine: Optional[ScraperEngine] = None
db_manager: Optional[DatabaseManager] = None

# Pydantic models
class ScrapeRequest(BaseModel):
    triggered_by: str = "api"

class ScrapeStatus(BaseModel):
    status: str
    job_id: Optional[int] = None
    progress: Optional[Dict[str, Any]] = None
    elapsed_seconds: Optional[int] = None
    estimated_remaining_seconds: Optional[int] = None

class ControlAction(BaseModel):
    action: str  # 'pause', 'resume', 'stop'

# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize scraper engine and database connection"""
    global scraper_engine, db_manager

    logger.info("Starting Exchange Scraper Service...")

    # Initialize database
    settings = get_settings()
    db_manager = DatabaseManager(settings.database_url)

    # Initialize scraper engine
    scraper_engine = ScraperEngine(
        db_manager=db_manager,
        headless=True
    )

    logger.info("Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scraper_engine, db_manager

    logger.info("Shutting down Exchange Scraper Service...")

    if scraper_engine:
        scraper_engine.stop()

    if db_manager:
        db_manager.close()

    logger.info("Service shutdown complete")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }

# Scraper control endpoints
@app.post("/api/scrape/start")
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start a new scraping job"""
    if not scraper_engine:
        raise HTTPException(status_code=503, detail="Scraper engine not initialized")

    if scraper_engine.is_running():
        raise HTTPException(status_code=409, detail="Scrape already in progress")

    # Start scrape in background
    background_tasks.add_task(
        scraper_engine.scrape_all,
        triggered_by=request.triggered_by
    )

    logger.info(f"Scrape started (triggered by: {request.triggered_by})")

    return {
        "success": True,
        "message": "Scrape started",
        "triggered_by": request.triggered_by
    }

@app.get("/api/scrape/status")
async def get_scrape_status() -> ScrapeStatus:
    """Get current scraping status"""
    if not scraper_engine:
        raise HTTPException(status_code=503, detail="Scraper engine not initialized")

    status_data = scraper_engine.get_status()

    return ScrapeStatus(**status_data)

@app.post("/api/scrape/control")
async def control_scrape(control: ControlAction):
    """Control running scrape (pause, resume, stop)"""
    if not scraper_engine:
        raise HTTPException(status_code=503, detail="Scraper engine not initialized")

    action = control.action.lower()

    if action == "pause":
        scraper_engine.pause()
        return {"success": True, "message": "Scrape paused"}
    elif action == "resume":
        scraper_engine.resume()
        return {"success": True, "message": "Scrape resumed"}
    elif action == "stop":
        scraper_engine.stop()
        return {"success": True, "message": "Scrape stopped"}
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

# Data retrieval endpoints
@app.get("/api/results/latest")
async def get_latest_results(limit: Optional[int] = None):
    """Get latest scrape results"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        results = db_manager.get_latest_results(limit=limit)
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error fetching latest results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/results/changes")
async def get_latest_changes():
    """Get changes from most recent scrape"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        changes = db_manager.get_latest_changes()
        return {
            "success": True,
            "count": len(changes),
            "changes": changes
        }
    except Exception as e:
        logger.error(f"Error fetching changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/recent")
async def get_recent_jobs(limit: int = 10):
    """Get recent job history"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        jobs = db_manager.get_recent_jobs(limit=limit)
        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        logger.error(f"Error fetching job history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/recent")
async def get_recent_logs(limit: int = 50):
    """Get recent activity logs"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        logs = db_manager.get_recent_logs(limit=limit)
        return {
            "success": True,
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/clear")
async def clear_logs():
    """Clear activity logs (keep last 7 days)"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        deleted_count = db_manager.clear_old_logs()
        return {
            "success": True,
            "message": f"Cleared {deleted_count} old log entries"
        }
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    """Get scraper statistics"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        stats = db_manager.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# Run the application
if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.debug,
        log_level="info"
    )
