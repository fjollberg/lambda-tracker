import json
import os
import uuid
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from urllib.parse import unquote, urlparse

from sqlalchemy import Column, DateTime, Integer, String, create_engine, distinct, func
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
Session = sessionmaker(bind=engine)
db = Session()


def formatted_timestamp(timestamp):
    return timestamp.astimezone().isoformat()


def home(event, context):
    response = {
        "statusCode": 200,
        "statusDescription": "200 OK"
    }
    return response


def extract_datetime_parameters(event):
    from_datetime = to_datetime = None

    from_timestamp = event['queryStringParameters'].get('from', None)
    if from_timestamp is not None:
        from_datetime = datetime.fromisoformat(
            unquote(from_timestamp)).astimezone(timezone.utc)

    to_timestamp = event['queryStringParameters'].get('to', None)
    if to_timestamp is not None:
        to_datetime = datetime.fromisoformat(
            unquote(to_timestamp)).astimezone(timezone.utc)

    return from_datetime, to_datetime


def log(event, context):
    response = {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "headers": {
            "Content-Type": "application/json"
        }
    }

    from_datetime, to_datetime = extract_datetime_parameters(event)

    if (from_datetime, to_datetime) == (None, None):
        logs = db.query(LogEntry).all()

    elif to_datetime is None:
        logs = db.query(LogEntry).filter(
            LogEntry.timestamp >= from_datetime).all()

    elif from_datetime is None:
        logs = db.query(LogEntry).filter(
            LogEntry.timestamp <= to_datetime).all()

    else:
        from sqlalchemy import and_
        logs = db.query(LogEntry).filter(
            and_(
                LogEntry.timestamp >= from_datetime,
                LogEntry.timestamp <= to_datetime)).all()

    response['body'] = json.dumps([l.serialize() for l in logs])

    return response


def report(event, context):
    response = {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "headers": {
            "Content-Type": "application/json"
        }
    }

    from_datetime, to_datetime = extract_datetime_parameters(event)

    if (from_datetime, to_datetime) == (None, None):
        res = db.query(LogEntry.url,
                       func.count(LogEntry.url), func.count(distinct(LogEntry.userid))).group_by(LogEntry.url).all()

    elif to_datetime is None:
        res = db.query(LogEntry.url,
                       func.count(LogEntry.url),
                       func.count(distinct(LogEntry.userid))
                       ).filter(LogEntry.timestamp >= from_datetime).group_by(LogEntry.url).all()

    elif from_datetime is None:
        res = db.query(LogEntry.url,
                       func.count(LogEntry.url),
                       func.count(distinct(LogEntry.userid))
                       ).filter(LogEntry.timestamp <= to_datetime).group_by(LogEntry.url).all()

    else:
        from sqlalchemy import and_
        res = db.query(LogEntry.url,
                       func.count(LogEntry.url),
                       func.count(distinct(LogEntry.userid))
                       ).filter(
            and_(
                LogEntry.timestamp >= from_datetime,
                LogEntry.timestamp <= to_datetime)
        ).group_by(LogEntry.url).all()

    response['body'] = json.dumps(
        [{'url': r[0], 'page views': r[1], 'visitors': r[2]} for r in res])

    return response


def get_tracker_data_from_event(event):
    referrer = userid = None

    if 'referer' in event['headers']:
        referrer = urlparse(event['headers']['referer']).path

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
        userid=userid,
        url=referer,
        timestamp=datetime.now(timezone.utc).replace(microsecond=0)
    )
    db.add(log)
    db.commit()

    response['headers']['set-cookie'] = 'userid={0};domain={1}'.format(
        userid, ".fjollberg.se")

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
