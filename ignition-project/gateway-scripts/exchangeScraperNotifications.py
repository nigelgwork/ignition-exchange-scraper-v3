"""
Exchange Scraper Notifications
Gateway script module for sending notifications

NOTE: This is Jython 2.7 code for Ignition gateway scripts
Uses camelCase naming convention per Ignition style guide
"""

# This module will be placed in: Project > Scripts > exchangeScraper > notifications


def getNotificationConfig():
	"""
	Get notification configuration from database
	Returns dictionary with email and ntfy settings
	"""
	try:
		query = """
			SELECT
				notification_email_enabled,
				notification_email_recipients,
				notification_ntfy_enabled,
				notification_ntfy_server,
				notification_ntfy_topic
			FROM scraper_config
			WHERE id = 1
		"""
		result = system.db.runQuery(query, database='exchange_scraper_db')

		if result and len(result) > 0:
			row = result[0]
			return {
				'email': {
					'enabled': row[0] or False,
					'recipients': row[1] or ''
				},
				'ntfy': {
					'enabled': row[2] or False,
					'server': row[3] or 'https://ntfy.sh',
					'topic': row[4] or ''
				}
			}
		else:
			return None
	except Exception as e:
		print "Error getting notification config: %s" % str(e)
		return None


def sendEmailNotification(jobInfo):
	"""
	Send email notification using Ignition SMTP

	Args:
		jobInfo: Dictionary with job information (resources_found, changes_detected, etc.)

	Returns:
		True if sent successfully, False otherwise
	"""
	config = getNotificationConfig()

	if not config or not config['email']['enabled']:
		return False

	recipients = config['email']['recipients']
	if not recipients:
		return False

	# Split recipients by comma
	recipientList = [r.strip() for r in recipients.split(',')]

	# Build email content
	subject = "Exchange Scrape Complete - %d Resources Found" % jobInfo.get('resources_found', 0)

	htmlBody = """
	<html>
	<head>
		<style>
			body { font-family: Arial, sans-serif; }
			.header { background-color: #0066cc; color: white; padding: 15px; }
			.content { padding: 20px; }
			.stats { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
			.stat-item { margin: 10px 0; }
			.label { font-weight: bold; }
		</style>
	</head>
	<body>
		<div class="header">
			<h2>Ignition Exchange Scraper</h2>
		</div>
		<div class="content">
			<h3>Scrape Job Completed</h3>
			<div class="stats">
				<div class="stat-item">
					<span class="label">Resources Found:</span> %d
				</div>
				<div class="stat-item">
					<span class="label">Changes Detected:</span> %d
				</div>
				<div class="stat-item">
					<span class="label">Duration:</span> %s
				</div>
				<div class="stat-item">
					<span class="label">Job ID:</span> %d
				</div>
			</div>
			<p>View the results in your Ignition Perspective dashboard.</p>
		</div>
	</body>
	</html>
	""" % (
		jobInfo.get('resources_found', 0),
		jobInfo.get('changes_detected', 0),
		jobInfo.get('duration_formatted', 'N/A'),
		jobInfo.get('job_id', 0)
	)

	try:
		# Use Ignition's built-in SMTP
		system.net.sendEmail(
			smtp='default',  # Uses gateway SMTP configuration
			fromAddr='noreply@ignition.local',
			subject=subject,
			body=htmlBody,
			to=recipientList,
			html=True
		)
		print "Email notification sent to: %s" % recipients
		return True
	except Exception as e:
		print "Error sending email notification: %s" % str(e)
		return False


def sendNtfyNotification(jobInfo):
	"""
	Send ntfy notification

	Args:
		jobInfo: Dictionary with job information

	Returns:
		True if sent successfully, False otherwise
	"""
	config = getNotificationConfig()

	if not config or not config['ntfy']['enabled']:
		return False

	server = config['ntfy']['server']
	topic = config['ntfy']['topic']

	if not server or not topic:
		return False

	url = "%s/%s" % (server, topic)

	# Build notification message
	message = "Exchange Scrape Complete!\n\n"
	message += "Resources: %d\n" % jobInfo.get('resources_found', 0)
	message += "Changes: %d\n" % jobInfo.get('changes_detected', 0)
	message += "Duration: %s" % jobInfo.get('duration_formatted', 'N/A')

	# Build headers
	headers = {
		'Title': 'Ignition Exchange Scraper',
		'Priority': '3',  # Medium priority
		'Tags': 'white_check_mark'
	}

	try:
		response = system.net.httpPost(
			url,
			contentType='text/plain',
			postData=message,
			headerValues=headers
		)
		print "ntfy notification sent to: %s" % url
		return True
	except Exception as e:
		print "Error sending ntfy notification: %s" % str(e)
		return False


def sendAllNotifications(jobInfo):
	"""
	Send all enabled notifications

	Args:
		jobInfo: Dictionary with job information

	Returns:
		Dictionary with results for each notification type
	"""
	results = {
		'email': sendEmailNotification(jobInfo),
		'ntfy': sendNtfyNotification(jobInfo)
	}

	return results


def testEmailNotification():
	"""
	Send a test email notification
	Returns True if successful
	"""
	testJobInfo = {
		'resources_found': 425,
		'changes_detected': 12,
		'duration_formatted': '18m 32s',
		'job_id': 999
	}

	return sendEmailNotification(testJobInfo)


def testNtfyNotification():
	"""
	Send a test ntfy notification
	Returns True if successful
	"""
	testJobInfo = {
		'resources_found': 425,
		'changes_detected': 12,
		'duration_formatted': '18m 32s',
		'job_id': 999
	}

	return sendNtfyNotification(testJobInfo)
