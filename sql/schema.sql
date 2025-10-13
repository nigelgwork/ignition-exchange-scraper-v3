-- =====================================================
-- Ignition Exchange Scraper v3 - Database Schema
-- PostgreSQL 12+
-- =====================================================

-- Main resources table
CREATE TABLE IF NOT EXISTS exchange_resources (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL UNIQUE,  -- Extracted from URL (e.g., 2819 from /exchange/2819/overview)
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    developer_id TEXT,
    version TEXT,
    updated_date TIMESTAMP,
    tagline TEXT,
    contributor TEXT,
    first_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Scrape job history
CREATE TABLE IF NOT EXISTS scrape_jobs (
    id SERIAL PRIMARY KEY,
    job_start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    job_end_time TIMESTAMP,
    status TEXT NOT NULL,  -- 'running', 'completed', 'failed', 'stopped', 'paused'
    resources_found INTEGER DEFAULT 0,
    changes_detected INTEGER DEFAULT 0,
    error_message TEXT,
    elapsed_seconds INTEGER,
    triggered_by TEXT DEFAULT 'scheduled'  -- 'scheduled', 'manual', 'api'
);

-- Resource history (tracks all changes over time)
CREATE TABLE IF NOT EXISTS resource_history (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER NOT NULL,
    job_id INTEGER REFERENCES scrape_jobs(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    developer_id TEXT,
    version TEXT,
    updated_date TIMESTAMP,
    tagline TEXT,
    contributor TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_type TEXT  -- 'new', 'updated', 'unchanged'
);

-- Configuration table (singleton)
CREATE TABLE IF NOT EXISTS scraper_config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    schedule_interval_days INTEGER DEFAULT 7,
    schedule_enabled BOOLEAN DEFAULT TRUE,
    last_run_time TIMESTAMP,
    next_run_time TIMESTAMP,
    notification_email_enabled BOOLEAN DEFAULT FALSE,
    notification_email_recipients TEXT,
    notification_ntfy_enabled BOOLEAN DEFAULT FALSE,
    notification_ntfy_server TEXT DEFAULT 'https://ntfy.sh',
    notification_ntfy_topic TEXT,
    scraper_service_url TEXT DEFAULT 'http://scraper-service:5000',
    scraper_mode TEXT DEFAULT 'service',  -- 'service' or 'native'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT single_config CHECK (id = 1)
);

-- Insert default config row
INSERT INTO scraper_config (id) VALUES (1) ON CONFLICT (id) DO NOTHING;

-- Activity log
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level TEXT NOT NULL,  -- 'info', 'warning', 'error'
    message TEXT NOT NULL,
    job_id INTEGER REFERENCES scrape_jobs(id) ON DELETE SET NULL
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_resources_updated ON exchange_resources(updated_date DESC);
CREATE INDEX IF NOT EXISTS idx_resources_resource_id ON exchange_resources(resource_id);
CREATE INDEX IF NOT EXISTS idx_resources_is_deleted ON exchange_resources(is_deleted);
CREATE INDEX IF NOT EXISTS idx_history_job_id ON resource_history(job_id);
CREATE INDEX IF NOT EXISTS idx_history_resource_id ON resource_history(resource_id);
CREATE INDEX IF NOT EXISTS idx_history_change_type ON resource_history(change_type);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON scrape_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_start_time ON scrape_jobs(job_start_time DESC);
CREATE INDEX IF NOT EXISTS idx_log_timestamp ON activity_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_log_job_id ON activity_log(job_id);
CREATE INDEX IF NOT EXISTS idx_log_level ON activity_log(level);

-- =====================================================
-- VIEWS
-- =====================================================

-- Latest results (most recent scrape)
CREATE OR REPLACE VIEW vw_latest_results AS
SELECT
    r.resource_id AS "Resource ID",
    r.title AS "Title",
    r.url AS "URL",
    r.version AS "Version",
    r.updated_date AS "Updated Date",
    r.developer_id AS "Developer ID",
    r.contributor AS "Contributor",
    r.tagline AS "Tagline",
    r.last_scraped_date AS "Last Scraped"
FROM exchange_resources r
WHERE r.is_deleted = FALSE
ORDER BY r.resource_id;

-- Changes from most recent scrape
CREATE OR REPLACE VIEW vw_latest_changes AS
SELECT
    rh.resource_id AS "Resource ID",
    rh.title AS "Title",
    rh.url AS "URL",
    rh.version AS "Version",
    rh.updated_date AS "Updated Date",
    rh.developer_id AS "Developer ID",
    rh.contributor AS "Contributor",
    rh.tagline AS "Tagline",
    rh.change_type AS "Change Type",
    rh.scraped_at AS "Scraped At"
FROM resource_history rh
INNER JOIN (
    SELECT MAX(id) as latest_job_id
    FROM scrape_jobs
    WHERE status = 'completed'
) latest ON rh.job_id = latest.latest_job_id
WHERE rh.change_type IN ('new', 'updated')
ORDER BY rh.resource_id;

-- Previous results (second most recent completed scrape)
CREATE OR REPLACE VIEW vw_previous_results AS
SELECT
    rh.resource_id AS "Resource ID",
    rh.title AS "Title",
    rh.url AS "URL",
    rh.version AS "Version",
    rh.updated_date AS "Updated Date",
    rh.developer_id AS "Developer ID",
    rh.contributor AS "Contributor",
    rh.tagline AS "Tagline",
    rh.scraped_at AS "Scraped At"
FROM resource_history rh
INNER JOIN (
    SELECT id as job_id
    FROM scrape_jobs
    WHERE status = 'completed'
    ORDER BY job_end_time DESC
    LIMIT 1 OFFSET 1
) previous ON rh.job_id = previous.job_id
ORDER BY rh.resource_id;

-- Recent jobs view (last 50 jobs)
CREATE OR REPLACE VIEW vw_recent_jobs AS
SELECT
    j.id AS "Job ID",
    j.job_start_time AS "Start Time",
    j.job_end_time AS "End Time",
    j.status AS "Status",
    j.resources_found AS "Resources Found",
    j.changes_detected AS "Changes Detected",
    j.elapsed_seconds AS "Duration (seconds)",
    j.triggered_by AS "Triggered By",
    CASE
        WHEN j.elapsed_seconds < 60 THEN j.elapsed_seconds || 's'
        WHEN j.elapsed_seconds < 3600 THEN (j.elapsed_seconds / 60) || 'm'
        ELSE (j.elapsed_seconds / 3600) || 'h ' || ((j.elapsed_seconds % 3600) / 60) || 'm'
    END AS "Duration (formatted)"
FROM scrape_jobs j
ORDER BY j.job_start_time DESC
LIMIT 50;

-- Activity log view (last 1000 entries)
CREATE OR REPLACE VIEW vw_activity_log AS
SELECT
    l.id AS "Log ID",
    l.timestamp AS "Timestamp",
    l.level AS "Level",
    l.message AS "Message",
    l.job_id AS "Job ID"
FROM activity_log l
ORDER BY l.timestamp DESC
LIMIT 1000;

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function to clean old logs (keep last 7 days)
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM activity_log
    WHERE timestamp < NOW() - INTERVAL '7 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get statistics
CREATE OR REPLACE FUNCTION get_scraper_stats()
RETURNS TABLE (
    total_resources INTEGER,
    total_jobs INTEGER,
    last_scrape_time TIMESTAMP,
    avg_resources_per_scrape NUMERIC,
    total_changes_detected INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*)::INTEGER FROM exchange_resources WHERE is_deleted = FALSE),
        (SELECT COUNT(*)::INTEGER FROM scrape_jobs),
        (SELECT MAX(job_start_time) FROM scrape_jobs WHERE status = 'completed'),
        (SELECT AVG(resources_found) FROM scrape_jobs WHERE status = 'completed'),
        (SELECT SUM(changes_detected)::INTEGER FROM scrape_jobs WHERE status = 'completed');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE exchange_resources IS 'Main table storing all Exchange resources';
COMMENT ON TABLE scrape_jobs IS 'History of all scraping jobs';
COMMENT ON TABLE resource_history IS 'Historical snapshot of resources for each scrape';
COMMENT ON TABLE scraper_config IS 'Configuration settings (singleton table)';
COMMENT ON TABLE activity_log IS 'Application activity and error logs';

COMMENT ON VIEW vw_latest_results IS 'Most recent scrape results';
COMMENT ON VIEW vw_latest_changes IS 'New or updated resources from latest scrape';
COMMENT ON VIEW vw_previous_results IS 'Previous scrape results for comparison';
COMMENT ON VIEW vw_recent_jobs IS 'Last 50 scraping jobs with formatted output';
COMMENT ON VIEW vw_activity_log IS 'Last 1000 activity log entries';
