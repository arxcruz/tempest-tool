import unittest

from httmock import all_requests, HTTMock

import tempestmail.utils as utils


@all_requests
def get_html_request_ok(url, request):
    return {'status_code': 200,
            'content': b'Feeling lucky?'}


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.url = 'https://www.google.com'
        super(TestUtils, self).setUp()

    def test_get_html_ok(self):
        with HTTMock(get_html_request_ok):
            html = utils.get_html(self.url)
            self.assertEquals(html.content, b'Feeling lucky?')
            self.assertEquals(html.status_code, 200)
