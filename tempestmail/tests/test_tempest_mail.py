import mock
import os
import unittest

from email.mime.text import MIMEText

import tempestmail.config
import tempestmail.mail

from tempestmail import tests


JOB = 'periodic-tripleo-ci-centos-7-ovb-ha-tempest'


class TestTempestMail(unittest.TestCase):
    def setUp(self):
        self.template_path = os.path.join(os.path.dirname(tests.__file__),
                                          'fixtures', 'mail')
        self.config_file = os.path.join(os.path.dirname(tests.__file__),
                                        'fixtures', 'config_validate',
                                        'good.yaml')
        self.config = tempestmail.config.loadConfig(self.config_file)
        self.config.template_path = self.template_path
        self.job = self.config.jobs[JOB]
        self.fail = [
            ('tempest.scenario.test_volume_boot_pattern.TestVolumeBootPattern.'
             'test_volume_boot_pattern'),
            ('tempest.scenario.test_volume_boot_pattern.TestVolumeBootPattern'
             'V2.test_volume_boot_pattern')
        ]
        self.covered = [
            ('tempest.api.volume.admin.v3.test_user_messages.UserMessagesTest'
             '.test_list_messages'),
            ('tempest.api.identity.v3.test_tokens.TokensV3Test.'
             'test_create_token')
        ]
        self.new = [
            ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.'
             'test_port_security_macspoofing_port'),
            ('tempest.scenario.test_network_advanced_server_ops.TestNetworkA'
             'dvancedServerOps.test_server_connectivity_suspend_resume')
        ]
        self.errors = [
            ('tempest.api.volume.test_volumes_snapshots_negative.VolumesV1S'
             'napshotNegativeTestJSON.test_create_snapshot_with_nonexistent_'
             'volume_id'),
            ('tempest.api.volume.test_volumes_negative.VolumesV2NegativeTest.'
             'test_reserve_volume_with_negative_volume_status')
        ]

    def test_render_template(self):
        _mail = tempestmail.mail.Mail(self.config)

        data = {
            'failed': self.fail,
            'covered': self.covered,
            'new': self.new,
            'errors': self.errors
        }
        render = _mail.render_template('template.html', data)
        self.assertIn('<h2>New failures</h2>', render)

        data.pop('new')
        render = _mail.render_template('template.html', data)
        self.assertIn('<h2>Success</h2>', render)

        data.pop('failed')
        render = _mail.render_template('template.html', data)
        self.assertIn('<h2>unexpected failures</h2>', render)

    @mock.patch('smtplib.SMTP')
    def test_send_mail(self, smtp_mock):
        _mail = tempestmail.mail.Mail(self.config)

        data = {
            'failed': self.fail,
            'covered': self.covered,
            'new': self.new,
            'errors': self.errors
        }
        render = _mail.render_template('template.html', data)
        msg = MIMEText(render)
        msg['Subject'] = self.job.subject
        msg['From'] = ''
        msg['To'] = ",".join(['arxcruz@gmail.com'])
        _mail.send_mail(self.job, data)
        smtp_mock.assert_called_once()
        smtp_mock.return_value.sendmail.assert_called_with(
            '', ['arxcruz@gmail.com'], msg.as_string())

        smtp_mock.reset_mock()

        self.job.is_template = False
        self.job.message = 'Hello World'
        msg = MIMEText(self.job.message)
        msg['Subject'] = self.job.subject
        msg['From'] = ''
        msg['To'] = ",".join(['arxcruz@gmail.com'])

        _mail.send_mail(self.job, data)

        smtp_mock.assert_called_once()
        smtp_mock.return_value.sendmail.assert_called_with(
            '', ['arxcruz@gmail.com'], msg.as_string())
