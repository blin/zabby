from zabby.core.utils import validate_mode
from zabby.hostos import detect_host_os

__all__ = ['read', ]


def read(device='all', stat_type='operations', mode='avg1',
         host_os=detect_host_os()):
    """
    Returns total number of read operations, or bytes or sectors read from
    device.

    :param device: Should be either all or device name
    :param stat_type: Should be one of
        host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES

    :raises: WrongArgumentError if unknown device is supplied
    :raises: WrongArgumentError if unknown stat_type is supplied

    :depends on: [
        host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES,
        host_os.disk_device_names
        host_os.disk_device_stats
    ]
    """
    validate_mode(stat_type, host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES)

    device_names = host_os.disk_device_names()

    if device != 'all':
        validate_mode(device, device_names)
        devices = set([device])
    else:
        devices = device_names

    result = 0
    for device_name in devices:
        stats = host_os.disk_device_stats(device_name)
        result += stats._asdict()['read_{0}'.format(stat_type)]

    return result
