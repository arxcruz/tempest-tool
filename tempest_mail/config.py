import yaml

class Config(object):
    pass


class Job(Config):
    pass

class Cron(Config):
    pass


class Email(Config):
    pass


def loadConfig(path_config):
    config = yaml.load(open(path_config))

    newconfig = Config()

    newconfig.username = config.get('mail_username')
    newconfig.password = config.get('mail_password')
    newconfig.smtp = config.get('smtp_server')

    for name, default in [('check', '*'), ('clean', '*')]:
        c = Cron()
        c.name = name
        newconfig.crons[c.name] = c
        c.timespec = config.get('cron', {}).get(name, default)

    for job in config.get('jobs', []):
        j = Job()
        j.name = job['name']
        newconfig.jobs[j.name] = j
        j.log_url = job.get('log_url', 'http://logs.openstack.org/periodic')
        j.tempest_results = job.get('tempest_results', 'console.html')
        j.subject = job.get('subject', 'Job fails')
        j.is_template = job.get('is_template', False)
        j.message = job.get('message')
        j.emails = {}
        for email in job['emails']:
            e = Email()
            e.name = email['name']
            j.emails[e.name] = e
            e.mail = email['mail']
        
