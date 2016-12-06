import logging
import threading

import config as tempest_config
import utils


class TempestMail(threading.Thread):
    log = logging.getLogger('tempestmail.TempestMail')

    def __init__(self, config_file, upstream=True, downstream=False):
        threading.Thread.__init__(self, name='TempestMail')
        self.config_file = config_file
        self.downstream = downstream
        self.upstream = upstream
        self.config = self.loadConfig()

    def run(self):
        self._run()

    def _run(self):
        data = []
        if(self.upstream):
            for job in self.config.jobs:
                index = job.get_index()
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
        if last.get('new') or not last.get('run'):
            # some_stats = stats(d)
            # send_report_with_failures(last)
            pass
        elif last.get('failed') and not last.get('new'):
            # send_successful_report(last=last)
            pass
        elif (last.get('ok') and not last.get('failed')
              and not last.get('errors')):
            # send_successful_report(last=last, nofail=True)
            pass
        else:
            # send_unexpected_failure(last)
            pass

    def loadConfig(self):
        self.log.debug("Loading configuration")
        config = tempest_config.loadConfig(self.config_file)
        return config
