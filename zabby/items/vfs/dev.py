from time import time
from zabby.core.utils import validate_mode, AVERAGE_MODE
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
        host_os.disk_device_names,
        host_os.disk_device_stats,
        host_os.disk_device_stats_shifted
    ]
    """
    type_without_per_second = (
        stat_type
        if stat_type not in stat_type_per_second
        else stat_type_per_second[stat_type]
    )
    validate_mode(type_without_per_second,
                  host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES)

    validate_mode(mode, AVERAGE_MODE.keys())
    shift = AVERAGE_MODE[mode]

    device_names = host_os.disk_device_names()

    if device != 'all':
        validate_mode(device, device_names)
        devices = set([device])
    else:
        devices = device_names

    stat_name = 'read_{0}'.format(type_without_per_second)
    now = int(time())
    result = 0.0
    for device_name in devices:
        current_stats = host_os.disk_device_stats(device_name)
        if not stat_type in stat_type_per_second.keys():
            result += current_stats._asdict()[stat_name]
        else:
            shifted_stats, shifted_timestamp = (
                host_os.disk_device_stats_shifted(device_name, shift, now))

            if shifted_stats is not None:
                stat_delta = (current_stats._asdict()[stat_name] -
                              shifted_stats._asdict()[stat_name])
                time_delta = now - shifted_timestamp

                result += stat_delta / time_delta

    return result


stat_type_per_second = {
    'sps': 'sectors',
    'ops': 'operations',
    'bps': 'bytes'
}
