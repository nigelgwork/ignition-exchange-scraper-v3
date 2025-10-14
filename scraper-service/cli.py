#!/usr/bin/env python3
"""
Standalone CLI for running scraper independently of FastAPI
This resolves the Playwright + FastAPI incompatibility issue
"""

import argparse
import sys

from app.config import get_settings
from app.database import DatabaseManager
from app.scraper_engine import ScraperEngine


def main():
    """Run scraper as standalone CLI tool"""
    parser = argparse.ArgumentParser(description="Ignition Exchange Scraper CLI")
    parser.add_argument(
        "--job-id", type=int, required=True, help="Job ID from database"
    )
    parser.add_argument(
        "--triggered-by", type=str, default="cli", help="Who triggered this scrape"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode",
    )

    args = parser.parse_args()

    # Initialize
    settings = get_settings()
    db_manager = DatabaseManager(settings.database_url)
    scraper_engine = ScraperEngine(db_manager=db_manager, headless=args.headless)

    # Set the job ID (already created by API)
    scraper_engine.current_job_id = args.job_id

    print(f"Starting scraper CLI for job #{args.job_id}")

    try:
        # Run the scrape
        scraper_engine.scrape_all(triggered_by=args.triggered_by)
        print("Scrape completed successfully")
        return 0
    except Exception as e:
        print(f"Scrape failed: {e}")
        return 1
    finally:
        db_manager.close()


if __name__ == "__main__":
    sys.exit(main())
