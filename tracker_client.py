import argparse
import http.client
import json

from urllib.parse import urlencode
from urllib.request import urlopen


def params_from_args(args):
    params = {}
    if args['to']:
        params['to'] = args['to']
    if args['from']:
        params['from'] = args['from']
    return params


def log(args):
    res = urlopen("{0}/log?{1}".format(args['base'], urlencode(params_from_args(args))))
    output = json.loads(res.read())

    if output:
        format = "|{0:25}|{1:30}|{2:36}|"
        print(format.format('timestamp', 'url', 'userid'))

        for line in output:
            print(format.format(line['timestamp'], line['url'], line['userid']))


def report(args):
    res = urlopen("{0}/report?{1}".format(args['base'], urlencode(params_from_args(args))))
    output = json.loads(res.read())

    if output:
        format = "|{0:30}|{1:12}|{2:10}|"
        print(format.format('url', 'page views', 'visitors'))
    
        for line in output:
            print(format.format(line['url'], line['page views'], line['visitors']))


def main():
    parser = argparse.ArgumentParser(description='Get tracker log entries or report.')
    parser.add_argument(
        'command',
        help = 'Ouput log entries or abbreviated report', choices=['log', 'report'])
    parser.add_argument(
        '--from',
        help = "Retrieve events from timestamp as ISO 8601 string, e.g. '2020-03-07T08:11:00+01:00'")
    parser.add_argument(
        '--to',
        help = "Retrieve events up to timestamp as ISO 8601 string, e.g. '2020-03-07T08:11:00+01:00'")
    parser.add_argument(
        '--base',
        help = "Optional base url, default 'http://localhost:5000'",
        default = 'http://localhost:5000')

    args = vars(parser.parse_args())

    if args['command'] == 'log':
        log(args)
    elif args['command'] == 'report':
        report(args)
