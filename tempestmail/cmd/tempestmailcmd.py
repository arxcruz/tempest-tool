import argparse
import sys

import tempestmail.cmd

from tempestmail.tempest_mail import TempestMail


class TempestMailCmd(tempestmail.cmd.TempestMailApp):
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='tempest-mail')
        parser.add_argument('-c', dest='config',
                            default='/etc/tempest-mail/tempest-mail.yaml',
                            help='Path to config file')
        parser.add_argument('-l', dest='logconfig',
                            help='Path to log config file')
        parser.add_argument('-p', dest='pidfile',
                            help='Path to pid file',
                            default='/var/run/tempest-mail/tempest-mail.pid')
        parser.add_argument('--version', dest='version',
                            help='Show version')
        parser.add_argument('--downstream', dest='downstream',
                            action='store_true',
                            help='Logs are downstream')
        parser.add_argument('--upstream', dest='upstream',
                            action='store_true',
                            help='Logs are upstream',
                            default=True)
        self.args = parser.parse_args()

    def main(self):
        self.setup_logging()
        self.mailcmd = TempestMail(self.args.config,
                                   self.args.upstream,
                                   self.args.downstream)
        config = self.mailcmd.loadConfig()
        self.mailcmd.setConfig(config)
        self.mailcmd.checkJobs()


def main():
    tmc = TempestMailCmd()
    tmc.parse_arguments()
    tmc.setup_logging()
    return tmc.main()

if __name__ == '__main__':
    sys.exit(main())
