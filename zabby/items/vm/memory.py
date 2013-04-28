from zabby.core.utils import validate_mode
from zabby.hostos import detect_host_os

__all__ = ['size', ]


def size(mode='total', host_os=detect_host_os()):
    """
    Returns an amount of memory of specified mode

    :param mode: Varies with host_os
    :raises: WrongArgument if unsupported mode is supplied

    :depends on: [host_os.AVAILABLE_MEMORY_TYPES, host_os.memory]
    """
    validate_mode(mode, host_os.AVAILABLE_MEMORY_TYPES)

    return host_os.memory()[mode]