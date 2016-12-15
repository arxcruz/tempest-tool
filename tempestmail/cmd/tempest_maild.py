import argparse
import daemon
import errno
import extras
import logging
import os
import signal
import sys
import threading
import traceback

import tempestmail
import tempestmail.cmd

from tempestmail.tempest_mail import TempestMail

pid_file_module = extras.try_imports(['daemon.pidlockfile', 'daemon.pidfile'])


def stack_dump_handler(signum, frame):
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)
    log_str = ""
    threads = {}
    for t in threading.enumerate():
        threads[t.ident] = t
    for thread_id, stack_frame in sys._current_frames().items():
        thread = threads.get(thread_id)
        if thread:
            thread_name = thread.name
        else:
            thread_name = 'Unknown'
        label = '%s (%s)' % (thread_name, thread_id)
        log_str += "Thread: %s\n" % label
        log_str += "".join(traceback.format_stack(stack_frame))
    log = logging.getLogger("tempestmail.stack_dump")
    log.debug(log_str)
    signal.signal(signal.SIGUSR2, stack_dump_handler)


def is_pidfile_stale(pidfile):
    """ Determine whether a PID file is stale.

        Return 'True' ("stale") if the contents of the PID file are
        valid but do not match the PID of a currently-running process;
        otherwise return 'False'.

        """
    result = False

    pidfile_pid = pidfile.read_pid()
    if pidfile_pid is not None:
        try:
            os.kill(pidfile_pid, 0)
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                # The specified PID does not exist
                result = True

    return result


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
                            help='Logs are downstream')
        parser.add_argument('--upstream', dest='upstream',
                            action='store_true',
                            help='Logs are upstream',
                            default=True)
        self.args = parser.parse_args()

    def exit_handler(self, signum, frame):
        self.maild.stop()
        sys.exit(0)

    def term_handler(self, signum, frame):
        os._exit(0)

    def main(self):
        self.setup_logging()
        self.maild = TempestMail(self.args.config,
                                 self.args.upstream,
                                 self.args.downstream)

        signal.signal(signal.SIGINT, self.exit_handler)
        # For back compatibility:
        signal.signal(signal.SIGUSR1, self.exit_handler)

        signal.signal(signal.SIGUSR2, stack_dump_handler)
        signal.signal(signal.SIGTERM, self.term_handler)

        self.maild.start()

        while True:
            signal.pause()


def main():
    tmd = TempestMailDaemon()
    tmd.parse_arguments()
    pid = pid_file_module.TimeoutPIDLockFile(tmd.args.pidfile, 10)
    if is_pidfile_stale(pid):
        pid.break_lock()

    if tmd.args.nodaemon:
        tmd.main()
    else:
        with daemon.DaemonContext(pidfile=pid):
            tmd.main()

if __name__ == '__main__':
    sys.exit(main())
