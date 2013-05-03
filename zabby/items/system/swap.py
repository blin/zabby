from zabby.core.utils import convert_size, SIZE_CONVERSION_MODES, validate_mode
from zabby.hostos import detect_host_os

__all__ = ['size', ]


def size(device='all', mode='free', host_os=detect_host_os()):
    """
    Returns free and total swap size converted according to mode

    :param mode: one of free, total, used, pfree, pused

    :raises: WrongArgument if unsupported mode is supplied

    :depends on: [host_os.swap_size]
    """
    validate_mode(mode, SIZE_CONVERSION_MODES)

    free, total = host_os.swap_size(device)

    return convert_size(free, total, mode)
