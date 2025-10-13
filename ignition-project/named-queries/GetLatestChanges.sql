-- Named Query: GetLatestChanges
-- Description: Get new and updated resources from most recent scrape
-- Parameters: None
-- Returns: Resources that were new or updated in latest scrape

SELECT * FROM vw_latest_changes
ORDER BY "Resource ID";
