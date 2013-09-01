import atexit
import optparse
import os


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


def daemonize(pid_file):
    def fork_exit_parent():
        pid = os.fork()
        if pid > 0:
            os._exit(0)

    if os.path.exists(pid_file):
        raise RuntimeError("Pid file {0} already exists".format(pid_file))

    fork_exit_parent()
    os.setsid()
    fork_exit_parent()

    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    atexit.register(lambda: os.remove(pid_file))
