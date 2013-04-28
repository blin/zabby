from . import cpu
from zabby.core.utils import validate_mode

from zabby.hostos import detect_host_os

__all__ = ['cpu', 'hostname', 'uname', ]


def hostname(hostname_type='host', host_os=detect_host_os()):
    """
    Returns host name.

    :raises: WrongArgumentError if unknown hostname_type is supplied

    :depends on: [host_os.hostname, host_os.AVAILABLE_HOSTNAME_TYPES]
    """
    validate_mode(hostname_type, host_os.AVAILABLE_HOSTNAME_TYPES)

    return host_os.hostname(hostname_type)


def uname(host_os=detect_host_os()):
    """
    Returns detailed host information.

    :depends on: [host_os.uname]
    """
    return " ".join(host_os.uname())


def uptime(host_os=detect_host_os()):
    """
    Returns system uptime in seconds.

    :depends on: [host_os.uptime]
    """
    return host_os.uptime()
