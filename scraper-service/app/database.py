"""
Database Manager - Handles all PostgreSQL operations
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

ADELAIDE_TZ = ZoneInfo("Australia/Adelaide")


class DatabaseManager:
    """Manages all database operations"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = False  # Use transactions
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def create_job(self, triggered_by: str = "manual") -> int:
        """Create a new scrape job and return its ID"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO scrape_jobs (status, triggered_by, job_start_time)
                    VALUES ('running', %s, %s)
                    RETURNING id
                """, (triggered_by, datetime.now(ADELAIDE_TZ)))
                job_id = cur.fetchone()[0]
                self.conn.commit()
                logger.info(f"Created job #{job_id}")
                return job_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error creating job: {e}")
            raise

    def complete_job(self, job_id: int, resources_found: int, changes_detected: int, elapsed_seconds: int):
        """Mark job as completed"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE scrape_jobs
                    SET status = 'completed',
                        job_end_time = %s,
                        resources_found = %s,
                        changes_detected = %s,
                        elapsed_seconds = %s
                    WHERE id = %s
                """, (datetime.now(ADELAIDE_TZ), resources_found, changes_detected, elapsed_seconds, job_id))
                self.conn.commit()
                logger.info(f"Job #{job_id} completed: {resources_found} resources, {changes_detected} changes")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error completing job: {e}")
            raise

    def fail_job(self, job_id: int, error_message: str, elapsed_seconds: int):
        """Mark job as failed"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE scrape_jobs
                    SET status = 'failed',
                        job_end_time = %s,
                        error_message = %s,
                        elapsed_seconds = %s
                    WHERE id = %s
                """, (datetime.now(ADELAIDE_TZ), error_message, elapsed_seconds, job_id))
                self.conn.commit()
                logger.warning(f"Job #{job_id} failed: {error_message}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error failing job: {e}")
            raise

    def add_log(self, message: str, level: str, job_id: Optional[int] = None):
        """Add entry to activity log"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO activity_log (message, level, job_id, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (message, level, job_id, datetime.now(ADELAIDE_TZ)))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error adding log: {e}")

    def store_scrape_results(self, job_id: int, results: List[Dict]) -> int:
        """
        Store scrape results and detect changes
        Returns number of changes detected
        """
        changes_detected = 0

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get previous resources for comparison
                cur.execute("""
                    SELECT resource_id, version, updated_date, title
                    FROM exchange_resources
                    WHERE is_deleted = FALSE
                """)
                previous_resources = {row['resource_id']: row for row in cur.fetchall()}

                # Track which resources we've seen
                seen_resource_ids = set()

                for resource in results:
                    resource_id = resource.get('resource_id')
                    if not resource_id:
                        continue

                    seen_resource_ids.add(resource_id)

                    # Parse updated_date if it's a string
                    updated_date = resource.get('updated_date')
                    if updated_date and isinstance(updated_date, str):
                        try:
                            # Try to parse ISO format
                            updated_date = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
                        except:
                            updated_date = None

                    # Check if this is new or updated
                    change_type = 'unchanged'
                    if resource_id not in previous_resources:
                        change_type = 'new'
                        changes_detected += 1
                    else:
                        # Check for changes
                        prev = previous_resources[resource_id]
                        if (resource.get('version') != prev['version'] or
                            resource.get('title') != prev['title'] or
                            (updated_date and prev['updated_date'] and updated_date != prev['updated_date'])):
                            change_type = 'updated'
                            changes_detected += 1

                    # Insert or update main resources table
                    cur.execute("""
                        INSERT INTO exchange_resources (
                            resource_id, url, title, developer_id, version,
                            updated_date, tagline, contributor, last_scraped_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (resource_id) DO UPDATE SET
                            url = EXCLUDED.url,
                            title = EXCLUDED.title,
                            developer_id = EXCLUDED.developer_id,
                            version = EXCLUDED.version,
                            updated_date = EXCLUDED.updated_date,
                            tagline = EXCLUDED.tagline,
                            contributor = EXCLUDED.contributor,
                            last_scraped_date = EXCLUDED.last_scraped_date,
                            is_deleted = FALSE
                    """, (
                        resource_id,
                        resource.get('url'),
                        resource.get('title'),
                        resource.get('developer_id'),
                        resource.get('version'),
                        updated_date,
                        resource.get('tagline'),
                        resource.get('contributor'),
                        datetime.now(ADELAIDE_TZ)
                    ))

                    # Insert into history table
                    cur.execute("""
                        INSERT INTO resource_history (
                            resource_id, job_id, url, title, developer_id, version,
                            updated_date, tagline, contributor, scraped_at, change_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        resource_id,
                        job_id,
                        resource.get('url'),
                        resource.get('title'),
                        resource.get('developer_id'),
                        resource.get('version'),
                        updated_date,
                        resource.get('tagline'),
                        resource.get('contributor'),
                        datetime.now(ADELAIDE_TZ),
                        change_type
                    ))

                # Mark resources not seen as deleted
                for resource_id in previous_resources.keys():
                    if resource_id not in seen_resource_ids:
                        cur.execute("""
                            UPDATE exchange_resources
                            SET is_deleted = TRUE
                            WHERE resource_id = %s
                        """, (resource_id,))

                self.conn.commit()
                logger.info(f"Stored {len(results)} resources, detected {changes_detected} changes")
                return changes_detected

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error storing results: {e}")
            raise

    def get_latest_results(self, limit: Optional[int] = None) -> List[Dict]:
        """Get latest scrape results"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM vw_latest_results"
                if limit:
                    query += f" LIMIT {limit}"

                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching latest results: {e}")
            raise

    def get_latest_changes(self) -> List[Dict]:
        """Get changes from most recent scrape"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM vw_latest_changes")
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching changes: {e}")
            raise

    def get_recent_jobs(self, limit: int = 10) -> List[Dict]:
        """Get recent job history"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM vw_recent_jobs LIMIT %s", (limit,))
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching job history: {e}")
            raise

    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent activity logs"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, timestamp, level, message, job_id
                    FROM activity_log
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
            raise

    def clear_old_logs(self) -> int:
        """Clear old log entries (keep last 7 days)"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT cleanup_old_logs()")
                deleted_count = cur.fetchone()[0]
                self.conn.commit()
                logger.info(f"Cleared {deleted_count} old log entries")
                return deleted_count
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error clearing logs: {e}")
            raise

    def get_statistics(self) -> Dict:
        """Get scraper statistics"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM get_scraper_stats()")
                stats = dict(cur.fetchone())
                return stats
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            raise
