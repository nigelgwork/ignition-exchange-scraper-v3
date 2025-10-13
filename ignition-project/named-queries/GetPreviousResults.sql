-- Named Query: GetPreviousResults
-- Description: Get results from previous (second most recent) scrape
-- Parameters: None
-- Returns: Resource records from previous scrape for comparison

SELECT * FROM vw_previous_results
ORDER BY "Resource ID";
