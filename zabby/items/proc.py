import re

from zabby.hostos import detect_host_os
from zabby.core.utils import validate_mode

__all__ = ['num', ]

PROC_NUM_MODES = ['all', 'run', 'sleep', 'zomb']


def num(name=None, user=None, state='all', cmdline=None,
        host_os=detect_host_os()):
    """
    Returns number of userspace processes matching filter

    :depends on: [host_os.process_infos, host_os.uid]
    :raises: WrongArgument if unsupported state is supplied
    :raises: OperatingSystemError if user is invalid
    """
    validate_mode(state, PROC_NUM_MODES)

    uid = None
    if user is not None:
        uid = host_os.uid(user)

    number_of_processes = 0
    for process_info in host_os.process_infos():
        if _matches_filter(process_info, name, uid, state, cmdline):
            number_of_processes += 1

    return number_of_processes


def _matches_filter(process_info, name, uid, state, cmdline):
    matches_name = True if name is None else process_info.name == name
    matches_user = True if uid is None else process_info.uid == uid
    matches_state = True if state == 'all' else process_info.state == state
    matches_cmdline = (True
                       if cmdline is None
                       else re.search(cmdline, process_info.command_line))

    return matches_name and matches_user and matches_state and matches_cmdline
