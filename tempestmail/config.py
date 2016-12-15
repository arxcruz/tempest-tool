import yaml

import tempestmail.constants as constants
import tempestmail.exceptions as exceptions
import tempestmail.utils as utils

from six.moves.urllib.parse import urljoin


class Config(object):
    pass


class Job(Config):
    def get_index(self):
        ''' Get index page of periodic job and returns all links to jobs'''
        url = urljoin(self.log_url, self.name)
        res = utils.get_html(url)
        if res is None or not res.ok:
            raise exceptions.FailGetContent('Failed to get job URL %s' % url)

        body = res.content.decode() if res.content else ''
        if not body:
            raise exceptions.ContentNotFound('No content in index')

        with open("/tmp/mytest", "w") as f:
            f.write(body)
        hrefs = [constants.HREF.search(l).group(1)
                 for l in body.splitlines() if constants.HREF.search(l)]
        links = ["/".join((url, link))
                 for link in hrefs if constants.JOBRE.match(link)]
        if links:
            return links
        else:
            raise exceptions.JobNotFound('No periodic job link were '
                                         'found in %s' % url)


class Cron(Config):
    pass


class Email(Config):
    pass


def loadConfig(path_config):
    config = yaml.load(open(path_config))

    newconfig = Config()

    newconfig.crons = {}
    newconfig.jobs = {}

    newconfig.username = config.get('mail_username')
    newconfig.password = config.get('mail_password')
    newconfig.mail_from = config.get('mail_from', '')
    newconfig.smtp = config.get('smtp_server')
    newconfig.template_path = config.get('template_path')

    for name, default in [('check', '* 10 * * *')]:
        c = Cron()
        c.name = name
        newconfig.crons[c.name] = c
        c.timespec = config.get('cron', {}).get(name, default)

    for job in config.get('jobs', []):
        j = Job()
        j.name = job['name']
        newconfig.jobs[j.name] = j
        j.log_url = job.get('log_url', 'http://logs.openstack.org/periodic/')
        j.tempest_results = job.get('tempest_results', 'console.html')
        j.subject = job.get('subject', 'Job fails')
        j.is_template = job.get('is_template', False)
        j.message = job.get('message')
        j.emails = []
        for email in job['emails']:
            e = Email()
            e.name = email['name']
            e.mail = email['mail']
            j.emails.append(e)

    return newconfig
