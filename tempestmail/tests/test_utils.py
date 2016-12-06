import datetime
import os
import unittest

from httmock import all_requests, HTTMock
from six.moves.urllib.parse import urljoin

from tempestmail import tests

import tempestmail.utils as utils


def _get_console_content(filename='console.html'):
    console_log = os.path.join(os.path.dirname(tests.__file__),
                               'fixtures', 'console',
                               filename)
    with open(console_log, 'r') as console_file:
        return console_file.read()


@all_requests
def get_html_request_ok(url, request):
    return {'status_code': 200,
            'content': b'Feeling lucky?'}


@all_requests
def get_console_log(url, request):
    if url.path == '/console.html.gz' and url.netloc == 'www.found.com':
        return {'status_code': 200,
                'content': _get_console_content()}

    if url.path == '/console.html.gz' and url.netloc == 'www.google.com':
        return {'status_code': 403,
                'content': None}

    if url.path == '/console.html.gz' and url.netloc == 'www.notfound.com':
        return {'status_code': 404,
                'content': 'Page not found'}

    if url.path == '/console.html' and url.netloc == 'www.notfound.com':
        return {'status_code': 403,
                'content': None}


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.url = 'https://www.google.com'
        super(TestUtils, self).setUp()

    def test_get_html_ok(self):
        with HTTMock(get_html_request_ok):
            html = utils.get_html(self.url)
            self.assertEquals(html.content, b'Feeling lucky?')
            self.assertEquals(html.status_code, 200)

    def test_get_console(self):
        with HTTMock(get_console_log):
            console, date, url = utils.get_console('https://www.found.com')
            self.assertEquals(url, urljoin('https://www.found.com',
                                           'console.html.gz'))
            self.assertIsInstance(date, datetime.datetime)
            self.assertIsNotNone(console)

        with HTTMock(get_console_log):
            console, date, url = utils.get_console(self.url)
            self.assertEquals(console, None)
            self.assertEquals(date, None)
            self.assertEquals(url, None)

        with HTTMock(get_console_log):
            console, date, url = utils.get_console('https://www.notfound.com')
            self.assertEquals(console, None)
            self.assertEquals(date, None)
            self.assertEquals(url, None)

    def test_get_tests_results(self):
        console_error_failure = _get_console_content()
        failed, ok, errors = utils.get_tests_results(console_error_failure)
        self.assertTrue(len(failed))
        self.assertTrue(len(errors))
        self.assertTrue(len(ok))
        self.assertIn(('tempest.tests.lib.test_rest_client.'
                       'TestResponseBodyList.test_str'), failed)
        self.assertIn(('tempest.tests.test_wrappers.TestWrappers.'
                       'test_pretty_tox_serial'), errors)
