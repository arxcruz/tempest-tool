import mock
import unittest

import tempest_mail.bugs as bugs


class TestBugs(unittest.TestCase):

    def setUp(self):
        self.bz_url = 'https://bugzilla.redhat.com/show_bug.cgi?id=1386421'
        self.lp_url = 'https://bugs.launchpad.net/tripleo/+bug/1634824'
        self.error_url = 'https://www.google.com'
        super(TestBugs, self).setUp()

    def test_bug_factory_launchpad(self):
        connector = bugs.bug_factory(self.lp_url)
        self.assertIsInstance(connector, bugs.Launchpad)

    def test_bug_factory_bugzilla(self):
        connector = bugs.bug_factory(self.bz_url)
        self.assertIsInstance(connector, bugs.Bugzilla)

    def test_bug_factory_error(self):
        with self.assertRaises(ValueError):
            bugs.bug_factory(self.error_url)

    @mock.patch('tempest_mail.utils.get_html')
    def test_bug_status_bugzilla(self, get_html_mock):
        title = ('<title>Bug 1386421 &ndash; Tempest fail: tempest.api.'
                 'compute.servers.test_server_actions.ServerActionsTestJSON'
                 '</title>')
        returned_title = (u'Bug 1386421 \u2013 Tempest fail: tempest.api.'
                          'compute.servers.test_server_actions.'
                          'ServerActionsTestJSON')
        expected_return = (returned_title, None)

        get_html_mock.return_value.content.decode.return_value = title
        connector = bugs.connect_to_bug_system(self.bz_url)
        name = connector.bug_status()
        self.assertEquals(name, expected_return)

        get_html_mock.return_value = None
        connector = bugs.connect_to_bug_system(self.bz_url)
        name = connector.bug_status()

        self.assertEquals(name, ('', None))
        get_html_mock.assert_called()

    @mock.patch('tempest_mail.utils.get_html')
    def test_bug_status_launchpad(self, get_html_mock):
        title = ('<title>Bug #1633713 "puppet-ntp is breaking ci" : Bugs : '
                 'tripleo</title>')
        returned_title = ('Bug #1633713 "puppet-ntp is breaking ci" : Bugs : '
                          'tripleo')
        expected_return = (returned_title, None)

        get_html_mock.return_value.content.decode.return_value = title
        connector = bugs.connect_to_bug_system(self.lp_url)
        name = connector.bug_status()

        self.assertEquals(name, expected_return)

        get_html_mock.return_value = None
        connector = bugs.connect_to_bug_system(self.lp_url)
        name = connector.bug_status()

        self.assertEquals(name, ('', None))
        get_html_mock.assert_called()
