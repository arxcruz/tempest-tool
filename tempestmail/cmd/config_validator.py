import logging
import voluptuous as v
import yaml

log = logging.getLogger(__name__)


class ConfigValidator(object):
    def __init__(self, config_file):
        self.config_file = config_file

    def validate(self):
        cron = {
            'check': str,
            'clean': str,
        }

        emails = {
            'mail': str,
            'name': str
        }

        jobs = {
            'name': str,
            'log_url': str,
            'tempest_results': str,
            'message': str,
            'is_template': bool,
            'emails': v.Required([emails]),
            'subject': str
        }

        top_level = {
            'mail_username': str,
            'mail_password': str,
            'smtp_server': str,
            'cron': cron,
            'jobs': [jobs]
        }

        log.info('Validating %s' % self.config_file)
        config = yaml.load(open(self.config_file))

        schema = v.Schema(top_level)
        schema(config)
