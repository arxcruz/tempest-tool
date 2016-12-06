import argparse

import tempestmail.cmd


class TempestMailDaemon(tempestmail.cmd.TempestMailApp):
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='tempest-mail')
        parser.add_argument('-c', dest='config',
                            default='/etc/tempest-mail/tempest-mail.yaml',
                            help='Path to config file')
        parser.add_argument('-d', dest='nodaemon', action='store_true',
                            help='Do not run as a daemon')
        parser.add_argument('-l', dest='logconfig',
                            help='Path to log config file')
        parser.add_argument('-p', dest='pidfile',
                            help='Path to pid file',
                            default='/var/run/tempest-mail/tempest-mail.pid')
        parser.add_argument('--version', dest='version',
                            help='Show version')
        parser.add_argument('--downstream', dest='downstream',
                            action='store_true',
                            help='Logs is downstream')
        self.args = parser.parse_args()

    def main(self):
        self.setup_logging()
