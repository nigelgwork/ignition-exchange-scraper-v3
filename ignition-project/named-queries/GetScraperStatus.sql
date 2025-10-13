-- Named Query: GetScraperStatus
-- Description: Get current scraper status from most recent running/paused job
-- Parameters: None
-- Returns: job_id, status, elapsed_seconds

SELECT
    id as job_id,
    status,
    job_start_time,
    EXTRACT(EPOCH FROM (NOW() - job_start_time))::integer as elapsed_seconds,
    resources_found
FROM scrape_jobs
WHERE status IN ('running', 'paused')
ORDER BY job_start_time DESC
LIMIT 1;
