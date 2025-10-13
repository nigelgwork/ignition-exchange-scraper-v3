-- Named Query: GetConfig
-- Description: Get current scraper configuration
-- Parameters: None
-- Returns: Configuration record

SELECT
    schedule_enabled,
    schedule_interval_days,
    last_run_time,
    next_run_time,
    notification_email_enabled,
    notification_email_recipients,
    notification_ntfy_enabled,
    notification_ntfy_server,
    notification_ntfy_topic,
    scraper_service_url
FROM scraper_config
WHERE id = 1;
