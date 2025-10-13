"""
Exchange Scraper API Client
Gateway script module for communicating with the scraper service

NOTE: This is Jython 2.7 code for Ignition gateway scripts
Uses camelCase naming convention per Ignition style guide
"""

# This module will be placed in: Project > Scripts > exchangeScraper > api


def getScraperServiceUrl():
	"""
	Get the scraper service URL from configuration
	Returns the base URL for the scraper API
	"""
	try:
		# Query config from database
		query = "SELECT scraper_service_url FROM scraper_config WHERE id = 1"
		result = system.db.runNamedQuery("ExchangeScraper/GetConfig")

		if result:
			return result[0]['scraper_service_url']
		else:
			# Default to Docker service name
			return "http://scraper-service:5000"
	except:
		# Fallback default
		return "http://localhost:5000"


def makeApiCall(endpoint, method='GET', body=None):
	"""
	Make HTTP call to scraper service API

	Args:
		endpoint: API endpoint path (e.g., '/api/scrape/status')
		method: HTTP method ('GET', 'POST', 'DELETE')
		body: Dictionary to send as JSON body (for POST)

	Returns:
		Dictionary with response data, or None on error
	"""
	baseUrl = getScraperServiceUrl()
	url = baseUrl + endpoint

	try:
		if method == 'GET':
			response = system.net.httpGet(url, headerValues={'Accept': 'application/json'})
			if response:
				return system.util.jsonDecode(response)
			else:
				return None

		elif method == 'POST':
			headers = {
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			}

			if body:
				jsonBody = system.util.jsonEncode(body)
			else:
				jsonBody = '{}'

			response = system.net.httpPost(url, contentType='application/json',
			                                postData=jsonBody, headerValues=headers)
			if response:
				return system.util.jsonDecode(response)
			else:
				return None

		elif method == 'DELETE':
			# Use httpClient for DELETE
			response = system.net.httpClient().delete(url)
			if response:
				return system.util.jsonDecode(response)
			else:
				return None
		else:
			print "Invalid HTTP method: %s" % method
			return None

	except Exception as e:
		print "Error making API call to %s: %s" % (url, str(e))
		return None


def getScraperStatus():
	"""
	Get current scraper status
	Returns dictionary with status, progress, job_id, etc.
	"""
	return makeApiCall('/api/scrape/status', method='GET')


def startScrape(triggeredBy='manual'):
	"""
	Start a new scraping job

	Args:
		triggeredBy: String indicating who/what triggered the scrape

	Returns:
		Dictionary with success status
	"""
	body = {'triggered_by': triggeredBy}
	return makeApiCall('/api/scrape/start', method='POST', body=body)


def pauseScrape():
	"""Pause the current scraping job"""
	body = {'action': 'pause'}
	return makeApiCall('/api/scrape/control', method='POST', body=body)


def resumeScrape():
	"""Resume a paused scraping job"""
	body = {'action': 'resume'}
	return makeApiCall('/api/scrape/control', method='POST', body=body)


def stopScrape():
	"""Stop the current scraping job"""
	body = {'action': 'stop'}
	return makeApiCall('/api/scrape/control', method='POST', body=body)


def getLatestResults(limit=None):
	"""
	Get latest scrape results

	Args:
		limit: Optional limit on number of results

	Returns:
		Dictionary with results array
	"""
	endpoint = '/api/results/latest'
	if limit:
		endpoint += '?limit=%d' % limit
	return makeApiCall(endpoint, method='GET')


def getLatestChanges():
	"""
	Get changes from most recent scrape
	Returns dictionary with changes array
	"""
	return makeApiCall('/api/results/changes', method='GET')


def getRecentJobs(limit=10):
	"""
	Get recent job history

	Args:
		limit: Number of jobs to retrieve (default 10)

	Returns:
		Dictionary with jobs array
	"""
	endpoint = '/api/jobs/recent?limit=%d' % limit
	return makeApiCall(endpoint, method='GET')


def getRecentLogs(limit=50):
	"""
	Get recent activity logs

	Args:
		limit: Number of log entries to retrieve (default 50)

	Returns:
		Dictionary with logs array
	"""
	endpoint = '/api/logs/recent?limit=%d' % limit
	return makeApiCall(endpoint, method='GET')


def clearOldLogs():
	"""
	Clear old activity logs (keeps last 7 days)
	Returns dictionary with success status
	"""
	return makeApiCall('/api/logs/clear', method='POST')


def getStatistics():
	"""
	Get scraper statistics
	Returns dictionary with statistics
	"""
	return makeApiCall('/api/stats', method='GET')


def testConnection():
	"""
	Test connection to scraper service
	Returns True if healthy, False otherwise
	"""
	try:
		response = makeApiCall('/health', method='GET')
		if response and response.get('status') == 'healthy':
			return True
		else:
			return False
	except:
		return False
