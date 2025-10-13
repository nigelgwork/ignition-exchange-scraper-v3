-- Named Query: GetRecentJobs
-- Description: Get recent job history with formatted output
-- Parameters: limit (integer, default 10)
-- Returns: Job history records

SELECT * FROM vw_recent_jobs
LIMIT :limit;
