from zabby.core.utils import validate_mode, SIZE_CONVERSION_MODES, convert_size
from zabby.hostos import detect_host_os

__all__ = ['size', ]


def size(filesystem, mode="total", host_os=detect_host_os()):
    """
    Returns free and total fs size converted according to mode

    :param filesystem: what filesystem to check
    :type filesystem: str

    :param mode: one of free, total, used, pfree, pused

    :raises: WrongArgument if unsupported mode is supplied

    :depends on: [host_os.fs_size]
    """
    validate_mode(mode, SIZE_CONVERSION_MODES)

    free, total = host_os.fs_size(filesystem)

    return convert_size(free, total, mode)
