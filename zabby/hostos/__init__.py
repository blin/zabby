from collections import namedtuple
import sys
import threading
import logging

LOG = logging.getLogger(__name__)

CURRENT_OS = None


def detect_host_os():
    """
    Returns an instance of OperatingSystem that matches given host system

    :raises: NotImplementedError if host operating system is not yet supported
    :rtype: HostOS
    """
    global CURRENT_OS
    if not CURRENT_OS:
        if sys.platform.startswith('linux'):
            from zabby.hostos.linux import Linux

            CURRENT_OS = Linux()
        else:
            raise NotImplementedError

    return CURRENT_OS


NETWORK_INTERFACE_INFO_FIELDS = [
    'in_bytes', 'in_packets', 'in_errors', 'in_dropped',
    'out_bytes', 'out_packets', 'out_errors', 'out_dropped',
    'collisions'
]

NetworkInterfaceInfo = namedtuple(
    'NetworkInterfaceInfo',
    NETWORK_INTERFACE_INFO_FIELDS
)

ProcessInfo = namedtuple(
    'ProcessInfo',
    ['name', 'uid', 'state', 'command_line', 'used_memory', ]
)

DISK_DEVICE_STATS_FIELDS = [
    'read_sectors', 'read_operations', 'read_bytes',
    'write_sectors', 'write_operations', 'write_bytes',
]

DiskDeviceStats = namedtuple('DiskDeviceStats', DISK_DEVICE_STATS_FIELDS)


class HostOS(object):
    """
    Represents abstract operating system

    It contains abstract methods that concrete operating systems may provide
    Different data extraction operations may be enabled by implementing these
    methods
    """

    AVAILABLE_MEMORY_TYPES = set()
    AVAILABLE_DISK_DEVICE_STATS_TYPES = set()

    def __init__(self):
        self._collectors = list()

    def start_collectors(self):
        for collector in self._collectors:
            threading.Thread(target=collector.run).start()

    def stop_collectors(self):
        for collector in self._collectors:
            collector.stop()

    def fs_size(self, filesystem):
        """
        Get information about free and total space on a filesystem in bytes

        :param filesystem: mount point to get size information for
        :type filesystem: str
        :rtype : (int, int)
        """
        raise NotImplementedError

    def fs_inodes(self, filesystem):
        """
        Get information about free and total space on a filesystem in bytes

        :param filesystem: mount point to get inodes information for
        :type filesystem: str
        :rtype : (int, int)
        """
        raise NotImplementedError

    def net_interface_names(self):
        """
        Returns a set that contains all interface names available on this host

        :rtype: set
        """
        raise NotImplementedError

    def net_interface_info(self, net_interface_name):
        """
        Returns named tuple NetworkInterfaceInfo that contains information on
        amount of incoming/outgoing bytes, packets, errors and dropped packets
        """
        raise NotImplementedError

    def process_infos(self):
        """
        Returns an iterable of ProcessInfo
        """
        raise NotImplementedError

    def uid(self, username):
        """
        Returns UID compatible with ProcessInfo.uid
        """
        raise NotImplementedError

    def memory(self):
        """
        Returns a dict containing information about memory usage

        Dict keys are equivalent to AVAILABLE_MEMORY_TYPES
        """
        raise NotImplementedError

    def disk_device_names(self):
        """
        Returns a set that contains all disk device names available on this host

        :rtype: set
        """
        raise NotImplementedError

    def disk_device_stats(self, device):
        """
        Returns DiskDeviceStats for device
        """
        raise NotImplementedError

    def disk_device_stats_shifted(self, device, shift, now):
        """
        Returns DiskDeviceStats for device shifted for shift seconds from now
        and timestamp for when this stats were taken
        """
        raise NotImplementedError
