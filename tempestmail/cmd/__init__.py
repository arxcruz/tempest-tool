import logging
import logging.config
import os


class TempestMailApp(object):

    def __init__(self):
        self.args = None

    def setup_logging(self):
        if self.args.logconfig:
            fp = os.path.expanduser(self.args.logconfig)
            if not os.path.exists(fp):
                raise Exception("Unable to read logging config file at %s" %
                                fp)
            logging.config.fileConfig(fp)
        else:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(name)s: '
                                       '%(message)s')
