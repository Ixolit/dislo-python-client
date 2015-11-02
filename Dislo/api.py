#!/usr/bin/python

import json, urllib, httplib, time, hmac, hashlib, pprint


class HTTPQueryHandler:
    """
    This class is the abstract query handler for raw HTTP queries.
    """
    endpoint = ''
    api_key = ''
    api_secret = ''

    def __init__(self, endpoint, api_key, api_secret):
        """
        Initialize the QueryHandler with authentication information.
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.password = api_secret

    def call(self, uri, parameters):
        """
        Perform the raw API call with signing.
        """
        url = self.endpoint + uri
        url = url.split('/', 3)
        if self.endpoint.startswith('https'):
            conn = httplib.HTTPSConnection(url[2])
        else:
            conn = httplib.HTTPConnection(url[2])
        body = json.dumps(parameters)
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(body)
        }
        uri = '/' + url[3] + '?timestamp=' + str(int(time.time())) + \
              '&api_key=' + self.api_key + '&signature_algorithm=sha512'
        hm = hmac.new(self.api_secret, uri + body, hashlib.sha512)
        signature = hm.hexdigest()
        uri += '&signature=' + signature

        conn.request('POST', uri, body, headers)
        response = conn.getresponse()

        body = response.read()
        conn.close()

        signature = response.getheader('X-Signature')
        signature_algorithm = response.getheader('X-Signature-Algorithm')
        timestamp = response.getheader('X-Signature-Timestamp')

        if signature_algorithm != 'sha512':
            raise Exception(
                'Response signature algorithm ' + signature_algorithm + ' does not match request algorithm!')

        hm = hmac.new(self.api_secret, body + '\n\n' + timestamp + '\n' + signature_algorithm, hashlib.sha512)
        expected_signature = hm.digest()

        if expected_signature != signature:
            raise Exception(
                'Response signature ' + signature + ' does not match expected signature ' + expected_signature)

        if timestamp < time.time() - 300 or timestamp > time.time() + 300:
            raise Exception('Response timestamp is out of bounds: ' + timestamp + '. Expected ' +
                            str(time.time() - 300) + ' to ' + str(time.time() + 300))

        return body

    def custom_report(self, report_id, parameters=None, limit=None, offset=None, order=None):
        """
        Run a custom report by ID. Only works on expert-mode queries, results for simple editor queries are undefined
        due to how parameters are handled.
        """
        if not order:
            order = {}
        if not parameters:
            parameters = {}
        response = self.call('/export/v2/report/' + urllib.quote(report_id), {
            'parameters': parameters,
            'limit': limit,
            'offset': offset,
            'order': order
        })

    def custom_query(self, sql, parameters=None, limit=None, offset=None, order=None):
        """
        Run a custom report by explicitly specifying the SQL query to run, much like in the web interface. Parameters
        are optional, but recommended if unsafe data must be inserted into SQL queries.
        """
        if not order:
            order = {}
        if not parameters:
            parameters = {}
        response = self.call('/export/v2/query', {
            'query': sql,
            'parameters': parameters,
            'limit': limit,
            'offset': offset,
            'order': order
        })
