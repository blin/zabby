import atexit
import optparse
import os
import subprocess
import sys


option_parser = optparse.OptionParser()

option_parser.add_option(
    '-c', '--config',
    help='Absolute path to configuration file',
    default='/etc/zabby/config.py',
)
option_parser.add_option(
    '-d', '--daemonize',
    help='Specifies if zabby should be ran as independent process',
    action='store_true',
)
option_parser.add_option(
    '--pid-file',
    help='Specifies where to store pid',
    default='/var/run/zabby/zabby.pid',
)
option_parser.add_option(
    '--error-log',
    help='Specifies where stdout and stderr will be redirected '
         'if zabby is running as independent process',
    default='/var/log/zabby/zabby.err',
)


def daemonize(pid_file, error_log):
    def fork_exit_parent():
        pid = os.fork()
        if pid > 0:
            os._exit(0)

    def redirect_stream(system_stream, target_stream):
        os.dup2(target_stream.fileno(), system_stream.fileno())

    def close_all_open_files():
        '''Close all file descriptors except for stdin, stdout, stderr'''
        os.closerange(3, subprocess.MAXFD)

    if os.path.exists(pid_file):
        raise RuntimeError("Pid file {0} already exists".format(pid_file))

    fork_exit_parent()
    os.setsid()
    fork_exit_parent()

    close_all_open_files()

    with open(os.devnull) as devnull:
        redirect_stream(sys.stdin, devnull)

    with open(error_log, 'a') as error_log_file:
        redirect_stream(sys.stdout, error_log_file)
        redirect_stream(sys.stderr, error_log_file)

    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    atexit.register(lambda: os.remove(pid_file))
