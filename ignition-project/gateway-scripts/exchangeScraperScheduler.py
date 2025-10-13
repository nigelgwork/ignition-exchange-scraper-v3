"""
Exchange Scraper Scheduler
Gateway script module for managing scheduled scraping

NOTE: This is Jython 2.7 code for Ignition gateway scripts
Uses camelCase naming convention per Ignition style guide

This module should be called by a Gateway Timer Script that runs periodically
"""

# This module will be placed in: Project > Scripts > exchangeScraper > scheduler

import exchangeScraper.api as api
import exchangeScraper.notifications as notifications


def getScheduleConfig():
	"""
	Get schedule configuration from database
	Returns dictionary with interval, enabled status, next run time
	"""
	try:
		query = """
			SELECT
				schedule_interval_days,
				schedule_enabled,
				last_run_time,
				next_run_time
			FROM scraper_config
			WHERE id = 1
		"""
		result = system.db.runQuery(query, database='exchange_scraper_db')

		if result and len(result) > 0:
			row = result[0]
			return {
				'intervalDays': row[0] or 7,
				'enabled': row[1] or False,
				'lastRunTime': row[2],
				'nextRunTime': row[3]
			}
		else:
			return None
	except Exception as e:
		print "Error getting schedule config: %s" % str(e)
		return None


def updateNextRunTime(intervalDays):
	"""
	Calculate and update next run time in database

	Args:
		intervalDays: Number of days until next run
	"""
	try:
		now = system.date.now()
		nextRun = system.date.addDays(now, intervalDays)

		query = """
			UPDATE scraper_config
			SET last_run_time = ?,
			    next_run_time = ?
			WHERE id = 1
		"""
		system.db.runPrepUpdate(query, [now, nextRun], database='exchange_scraper_db')

		print "Next scrape scheduled for: %s" % system.date.format(nextRun, "yyyy-MM-dd HH:mm:ss")
	except Exception as e:
		print "Error updating next run time: %s" % str(e)


def shouldRunScrape():
	"""
	Check if a scrape should be run based on schedule
	Returns True if scrape should run, False otherwise
	"""
	config = getScheduleConfig()

	if not config:
		return False

	if not config['enabled']:
		return False

	# Check if scraper is already running
	status = api.getScraperStatus()
	if status and status.get('status') in ['running', 'paused']:
		print "Scraper already running, skipping scheduled run"
		return False

	# Check if it's time to run
	nextRunTime = config['nextRunTime']
	if nextRunTime:
		now = system.date.now()
		if now >= nextRunTime:
			return True
	else:
		# No next run time set, run now if enabled
		return True

	return False


def checkAndRunSchedule():
	"""
	Main scheduler function - checks if scrape should run and starts it

	This should be called from a Gateway Timer Script that runs every hour
	Example Timer Script:

	import exchangeScraper.scheduler as scheduler
	scheduler.checkAndRunSchedule()
	"""
	if shouldRunScrape():
		print "Starting scheduled scrape..."

		# Start the scrape
		result = api.startScrape(triggeredBy='scheduled')

		if result and result.get('success'):
			print "Scheduled scrape started successfully"

			# Update next run time
			config = getScheduleConfig()
			if config:
				updateNextRunTime(config['intervalDays'])
		else:
			print "Failed to start scheduled scrape: %s" % str(result)
	else:
		# Not time to run yet
		pass


def onScrapeComplete(jobInfo):
	"""
	Callback function to be called when a scrape completes
	Sends notifications

	Args:
		jobInfo: Dictionary with job information from the completed scrape
	"""
	print "Scrape completed, sending notifications..."

	results = notifications.sendAllNotifications(jobInfo)

	if results['email']:
		print "Email notification sent"
	if results['ntfy']:
		print "ntfy notification sent"


def manualTrigger():
	"""
	Manually trigger a scrape (bypasses schedule check)
	Returns result from API call
	"""
	print "Manual scrape trigger initiated"

	# Check if already running
	status = api.getScraperStatus()
	if status and status.get('status') in ['running', 'paused']:
		return {
			'success': False,
			'message': 'Scraper is already running'
		}

	# Start the scrape
	result = api.startScrape(triggeredBy='manual')

	if result and result.get('success'):
		print "Manual scrape started successfully"

	return result


def pauseCurrentScrape():
	"""Pause the currently running scrape"""
	return api.pauseScrape()


def resumeCurrentScrape():
	"""Resume a paused scrape"""
	return api.resumeScrape()


def stopCurrentScrape():
	"""Stop the currently running scrape"""
	return api.stopScrape()


def updateScheduleSettings(intervalDays, enabled):
	"""
	Update schedule settings in database

	Args:
		intervalDays: Number of days between scrapes
		enabled: Boolean, whether scheduling is enabled
	"""
	try:
		query = """
			UPDATE scraper_config
			SET schedule_interval_days = ?,
			    schedule_enabled = ?
			WHERE id = 1
		"""
		system.db.runPrepUpdate(query, [intervalDays, enabled], database='exchange_scraper_db')

		print "Schedule settings updated: interval=%d days, enabled=%s" % (intervalDays, enabled)

		# Recalculate next run time if enabled
		if enabled:
			updateNextRunTime(intervalDays)

		return True
	except Exception as e:
		print "Error updating schedule settings: %s" % str(e)
		return False
