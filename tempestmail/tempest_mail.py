import logging
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.triggers.cron

import config as tempest_config
import mail
import utils


class TempestMail(threading.Thread):
    log = logging.getLogger('tempestmail.TempestMail')

    def __init__(self, config_file, upstream=True, downstream=False):
        threading.Thread.__init__(self, name='TempestMail')
        self.config_file = config_file
        self.downstream = downstream
        self.upstream = upstream
        self.config = None
        self._stopped = False
        self._wake_condition = threading.Condition()
        self.apsched = None

    def stop(self):
        self._stopped = True
        self._wake_condition.acquire()
        self._wake_condition.notify()
        self._wake_condition.release()
        self.log.debug('Finished stopping')

    def startup(self):
        self.updateConfig()

    def reconfigureCron(self, config):
        cron_map = {
            'check': self.checkJobs,
        }
        if not self.apsched:
            self.apsched = BackgroundScheduler()
            self.apsched.start()
            self.log.debug('Scheduler started')

        for c in config.crons.values():
            if ((not self.config) or
               c.timespec != self.config.crons[c.name].timespec):
                if self.config and self.config.crons[c.name].job:
                    self.config.crons[c.name].job.remove()
                parts = c.timespec.split()
                if len(parts) > 5:
                    second = parts[5]
                else:
                    second = None
                minute, hour, dom, month, dow = parts[:5]
                trigger = apscheduler.triggers.cron.CronTrigger(
                    month=month, day=dom, day_of_week=dow,
                    hour=hour, minute=minute, second=second)
                c.job = self.apsched.add_job(
                    cron_map[c.name], trigger=trigger)
                self.log.debug('Cron job ')
            else:
                c.job = self.config.crons[c.name].job

    def run(self):
        try:
            self.startup()
        except Exception:
            self.log.exception("Exception in startup:")

        while not self._stopped:
            try:
                self.log.debug('Calling updateConfig from while loop')
                self.updateConfig()
            except Exception:
                self.log.exception("Exception in main loop:")
            self._wake_condition.acquire()
            self._wake_condition.wait(10)
            self._wake_condition.release()

    def checkJobs(self):
        if(self.upstream):
            for job in self.config.jobs:
                data = []
                index = self.config.jobs[job].get_index()
                for run in index:
                    console, date, link = utils.get_console(run)
                    if not console or not date:
                        continue

                    fails, ok, errors = utils.get_tests_results(console)
                    d = {
                        'run': True,
                        'date': date,
                        'link': link
                    }

                    if fails or errors:
                        covered, new = utils.compare_tests(fails)
                        d.update({
                            'failed': fails,
                            'covered': covered,
                            'new': new,
                            'errors': errors,
                        })
                    elif ok:
                        d['ok'] = ok
                    elif not fails and not ok and not errors:
                        d['run'] = False
                    data.append(d)

                data = sorted(data, key=lambda x: x['date'])
                last = data[-1]
                send_mail = mail.Mail(self.config)
                send_mail.send_mail(self.config.jobs[job], last)

    def updateConfig(self):
        self.log.debug('Updating configuration from file')
        config = self.loadConfig()
        self.reconfigureCron(config)
        self.setConfig(config)

    def setConfig(self, config):
        self.config = config
        self.log.debug('Config changed')

    def loadConfig(self):
        self.log.debug("Loading configuration")
        config = tempest_config.loadConfig(self.config_file)
        return config
