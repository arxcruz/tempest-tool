import os
import unittest

from httmock import all_requests, HTTMock

import tempestmail.config
import tempestmail.exceptions as exceptions

from tempestmail import tests

JOB = 'periodic-tripleo-ci-centos-7-ovb-ha-tempest'

INDEX_RETURN = (
    """
    <tr>
        <td valign="top"><img src="/icons/back.gif" alt="[PARENTDIR]"></td>
        <td><a href="/periodic/">Parent Directory</a></td>
        <td>&nbsp;</td><td align="right">  - </td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td>
        <td><a href="f0a420d/">f0a420d/</a></td>
        <td align="right">2016-12-05 06:06  </td>
        <td align="right">  - </td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td>
        <td><a href="2cdcdcf/">2cdcdcf/</a></td>
        <td align="right">2016-12-04 09:34  </td>
        <td align="right">  - </td>
        <td>&nbsp;</td>
    </tr>
    <tr>
        <td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td>
        <td><a href="8988e60/">8988e60/</a></td>
        <td align="right">2016-12-04 09:34  </td>
        <td align="right">  - </td>
        <td>&nbsp;</td>
    </tr>
""")


@all_requests
def get_html_request_ok(url, request):
    return {'status_code': 200,
            'content': INDEX_RETURN}


@all_requests
def get_html_request_fail(url, request):
    return {'status_code': 404,
            'content': None}


@all_requests
def get_html_request_none(url, request):
    return {'status_code': 200,
            'content': ''}


class TestConfigJob(unittest.TestCase):
    def setUp(self):
        self.config_file = os.path.join(os.path.dirname(tests.__file__),
                                        'fixtures', 'config_validate',
                                        'good.yaml')
        self.config = tempestmail.config.loadConfig(self.config_file)

    def test_config_job_get_index_ok(self):
        job = self.config.jobs[JOB]
        url = ('http://logs.openstack.org/periodic-tripleo-ci-centos-7-ovb-ha'
               '-tempest')
        expected_return = [
            url + '/f0a420d/',
            url + '/2cdcdcf/',
            url + '/8988e60/'
        ]

        with HTTMock(get_html_request_ok):
            links = job.get_index()
            self.assertEquals(links, expected_return)

    def test_config_job_get_index_fail(self):
        job = self.config.jobs[JOB]
        with HTTMock(get_html_request_fail):
            self.assertRaises(exceptions.FailGetContent, job.get_index)

    def test_config_job_get_index_none(self):
        job = self.config.jobs[JOB]
        with HTTMock(get_html_request_none):
            self.assertRaises(exceptions.ContentNotFound, job.get_index)
