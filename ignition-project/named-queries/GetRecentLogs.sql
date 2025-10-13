-- Named Query: GetRecentLogs
-- Description: Get recent activity logs
-- Parameters: limit (integer, default 50)
-- Returns: Recent log entries

SELECT
    id,
    timestamp,
    level,
    message,
    job_id
FROM activity_log
ORDER BY timestamp DESC
LIMIT :limit;
