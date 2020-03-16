import os
import urllib
import uuid

from datetime import datetime, timezone
from http.cookies import SimpleCookie
from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class LogEntry(declarative_base()):
	__tablename__ = 'log'

	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime, nullable=False, index=True)
	url = Column(String(512), nullable=False, index=True)
	userid = Column(String(36), nullable=False, index=True)

	def __init__(self, timestamp, url, userid):
		self.timestamp = timestamp
		self.url = url
		self.userid = userid

	def __repr__(self):
		return '<LogEntry: {0}:{1}:{2} - {3}>'.format(
			self.id, formatted_timestamp(self.timestamp), self.userid, self.url)
 
	def serialize(self):
		return {
			'timestamp': formatted_timestamp(self.timestamp), 
			'url': self.url,
			'userid': self.userid
		}


# SQLAlchemy DB definition.
# 'mysql+pymysql://scott:tiger@localhost/foo'
engine = create_engine(os.getenv(
	'LAMBDA_TRACKER_DB',
	'sqlite:///{0}/test.db'.format(os. getcwd())))
LogEntry.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
db = Session()


def formatted_timestamp(timestamp):
    return timestamp.astimezone().isoformat()


def home(event, context):
	response = {
		"statusCode": 200,
		"statusDescription": "200 OK"
	}
	return response


def log(event, context):
	response = {
		"statusCode": 200,
		"statusDescription": "200 OK"
	}
	return response


def report(event, context):
	response = {
		"statusCode": 200,
		"statusDescription": "200 OK"
	}
	return response


def get_tracker_data_from_event(event):
	referrer = userid = None

	if 'referer' in event:
		referrer = urllib.parse.urlparse(event['referer']).path
    
	if 'cookie' in event['headers']:
		cookie = SimpleCookie(event['headers']['cookie'])
		userid = cookie['userid'].value if 'userid' in cookie else None

	return referrer, userid


def track(event, context):
	response = {
		"statusCode": 200,
		"statusDescription": "200 OK",
		"isBase64Encoded": True,
		"headers": {
			"Content-Type": "image/gif"
		},
        "body": 'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
	}

	referer, userid = get_tracker_data_from_event(event)

	if referer is None:
		return response

	if userid is None:
		userid = str(uuid.uuid4())

	log = LogEntry(
		userid = userid,
		url = referer,
		timestamp = datetime.now(timezone.utc).replace(microsecond=0)
	)
	db.add(log)
	db.commit()

	response['headers']['cookie'] = 'userid={0}'.format(userid)

	return response


def lambda_handler(event, context):
	path = event['path']

	if path == '/':
		return home(event, context)
	elif path == '/tracker.gif':
		return track(event, context)
	elif path == '/log':
		return log(event, context)
	elif path == '/report':
		return report(event, context)
	else:
		return {
			"statusCode": 404,
			"statusDescription": "404 Not Found",
		}
