import uuid

from http.cookies import SimpleCookie
from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# SQLAlchemy DB definition.
db = create_engine('mysql+pymysql://scott:tiger@localhost/foo')


class LogEntry(declarative_base()):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    userid = Column(String, nullable=False, index=True)

    def __repr__(self):
        return '<LogEntry: {0}:{1}:{2} - {3}>'.format(
            self.id, formatted_timestamp(self.timestamp), self.userid, self.url)

    def serialize(self):
        return {
            'timestamp': formatted_timestamp(self.timestamp), 
            'url': self.url,
            'userid': self.userid
        }


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

	if 'cookie' in event['headers']:
		cookie = SimpleCookie(event['headers']['cookie'])
		userid = cookie['userid'].value if 'userid' in cookie else uuid.uuid4()
	else:
		userid = uuid.uuid4()

	if 'referer' in event:
	    # Log entry in database.
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

