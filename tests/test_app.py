import json
import os
import sys
import uuid
from datetime import datetime

import pytest
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Hack to add top directory to python path to find tracker_server.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from track import LogEntry, lambda_handler


start_time = datetime.now().replace(microsecond=0)


@pytest.fixture(scope="module")
def setup():
    yield
    os.remove("test.db")


def test_bad_path_gives_404(setup):
    request = {
        "path": "/random-path",
        "headers": {}
    }
    response = lambda_handler(request, None)

    assert 'statusCode' in response 
    assert response['statusCode'] == 404


def test_tracker_with_no_referer_gives_no_cookie(setup):
    request = {
        "path": "/tracker.gif",
        "headers": {}
    }
    response = lambda_handler(request, None)

    assert 'statusCode' in response 
    assert response['statusCode'] == 200
    assert 'Content-Type' in response['headers']
    assert response['headers']['Content-Type'] == 'image/gif'
    assert response['isBase64Encoded'] == True
    assert 'body' in response
    assert 'cookies' not in response['headers']


def test_tracker_with_referer_gives_cookie(setup):
    request = {
        "path": "/tracker.gif",
        "referer": "http://localhost/random_url",
        "headers": {}
    }
    response = lambda_handler(request, None)

    assert 'statusCode' in response 
    assert response['statusCode'] == 200
    assert 'Content-Type' in response['headers']
    assert response['headers']['Content-Type'] == 'image/gif'
    assert response['isBase64Encoded'] == True
    assert 'body' in response
    assert 'cookie' in response['headers']


def test_tracker_with_cookie_returns_same_cookie(setup):
    request = {
        "path": "/tracker.gif",
        "referer": "http://localhost/random_url",
        "headers": {
            "cookie": "userid=foobar"
        }
    }
    response = lambda_handler(request, None)

    assert 'statusCode' in response 
    assert response['statusCode'] == 200
    assert 'Content-Type' in response['headers']
    assert response['headers']['Content-Type'] == 'image/gif'
    assert response['isBase64Encoded'] == True
    assert 'body' in response
    print(response)
    assert 'cookie' in response['headers']
    assert response['headers']['cookie'] == 'userid=foobar'


def test_tracker_with_bad_cookie_returns_new_cookie(setup):
    request = {
        "path": "/tracker.gif",
        "referer": "http://localhost/random_url",
        "headers": {
            "cookie": "xxx=foobar"
        }
    }
    response = lambda_handler(request, None)

    assert 'statusCode' in response 
    assert response['statusCode'] == 200
    assert 'Content-Type' in response['headers']
    assert response['headers']['Content-Type'] == 'image/gif'
    assert response['isBase64Encoded'] == True
    assert 'body' in response
    print(response)
    assert 'cookie' in response['headers']
    assert response['headers']['cookie'] != 'userid=foobar'
