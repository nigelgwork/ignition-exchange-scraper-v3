-- Named Query: GetLatestResults
-- Description: Get all resources from most recent scrape
-- Parameters: None
-- Returns: All resource records from latest scrape

SELECT * FROM vw_latest_results
ORDER BY "Resource ID";
