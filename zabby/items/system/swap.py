from zabby.core.exceptions import WrongArgumentError
from zabby.core.utils import convert_size, SIZE_CONVERSION_MODES, validate_mode
from zabby.hostos import detect_host_os

__all__ = ['size', 'into_memory', ]


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


def into_memory(device='all', mode='count', host_os=detect_host_os()):
    """
    Returns total number of pages read from swap into memory or total number of
    read operations or sectors read from swap device

    :param mode: should be one of {'count', 'pages', 'sectors'}

    :raises: WrongArgumentError if mode is pages and device is not 'all'
    :raises: WrongArgumentError if mode is unknown
    :raises: WrongArgumentError if mode is unavailable on this host_os

    :depends on: [
        host_os.swap_info,
        host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES,
        host_os.swap_device_names,
        host_os.disk_device_stats,
    ]
    """
    if mode == 'pages':
        if device != 'all':
            raise WrongArgumentError(
                'Swapped pages info per device is not available')
        swap_info = host_os.swap_info()
        result = swap_info._asdict()['read']
    else:
        validate_mode(mode, SWAP_TO_DISK_DEVICE_STAT.keys())
        disk_device_stat_type = SWAP_TO_DISK_DEVICE_STAT[mode]
        validate_mode(disk_device_stat_type,
                      host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES)
        disk_device_stat = "{0}_{1}".format('read',
                                            disk_device_stat_type)
        device_names = host_os.swap_device_names()
        if device != 'all':
            validate_mode(device, device_names)
            devices = set([device])
        else:
            devices = device_names

        result = 0
        for device_name in devices:
            stats = host_os.disk_device_stats(device_name)
            result += stats._asdict()[disk_device_stat]

    return result


SWAP_TO_DISK_DEVICE_STAT = {
    'count': 'operations',
    'sectors': 'sectors',
}
