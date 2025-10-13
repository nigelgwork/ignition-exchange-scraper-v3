-- Named Query: UpdateConfig
-- Description: Update scraper configuration
-- Query Type: UPDATE
-- Parameters:
--   schedule_enabled (boolean)
--   schedule_interval_days (integer)
--   notification_email_enabled (boolean)
--   notification_email_recipients (string)
--   notification_ntfy_enabled (boolean)
--   notification_ntfy_topic (string)
-- Returns: Number of rows updated

UPDATE scraper_config
SET
    schedule_enabled = :schedule_enabled,
    schedule_interval_days = :schedule_interval_days,
    notification_email_enabled = :notification_email_enabled,
    notification_email_recipients = :notification_email_recipients,
    notification_ntfy_enabled = :notification_ntfy_enabled,
    notification_ntfy_topic = :notification_ntfy_topic,
    updated_at = NOW()
WHERE id = 1;
