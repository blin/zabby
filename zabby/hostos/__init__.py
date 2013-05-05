from collections import namedtuple
import sys
import threading
import logging

from zabby.core.utils import AVERAGE_MODE

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

CPU_TIMES = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', ]
CpuTimes = namedtuple('CpuTimes', CPU_TIMES)

SystemLoad = namedtuple('SystemLoad', list(AVERAGE_MODE.keys()))

SwapInfo = namedtuple('SwapInfo', ['read', 'write', ])


class HostOS(object):
    """
    Represents abstract operating system

    It contains abstract methods that concrete operating systems may provide
    Different data extraction operations may be enabled by implementing these
    methods
    """

    def __init__(self):
        self._collectors = list()

    def start_collectors(self):
        for collector in self._collectors:
            threading.Thread(target=collector.run).start()

    def stop_collectors(self):
        for collector in self._collectors:
            collector.stop()

    AVAILABLE_MEMORY_TYPES = set()
    AVAILABLE_DISK_DEVICE_STATS_TYPES = set()
    AVAILABLE_HOSTNAME_TYPES = set(['host'])

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

    def cpu_count(self):
        """
        Returns count of cpu on this host
        """
        raise NotImplementedError

    def cpu_times(self, cpu_id):
        """
        Returns CpuTimes for cpu
        """
        raise NotImplementedError

    def cpu_times_shifted(self, cpu_id, shift):
        """
        Returns CpuTimes for cpu shifted for shift second from latest collected
        CpuTimes
        """
        raise NotImplementedError

    def hostname(self, hostname_type):
        """
        Returns hostname conforming to hostname_type

        :param hostname_type: should be one of AVAILABLE_HOSTNAME_TYPES
        """
        raise NotImplementedError

    def uname(self):
        """
        Returns information about system running on this host
        """
        raise NotImplementedError

    def uptime(self):
        """
        Returns system uptime in seconds.
        """
        raise NotImplementedError

    def max_number_of_running_processes(self):
        """
        Returns maximum number of running processes
        """
        raise NotImplementedError

    def system_load(self):
        """
        Returns SystemLoad
        """
        raise NotImplementedError

    def swap_size(self, device):
        """
        Get information about free and total swap space on a device

        :param device:
        :rtype : (int, int)
        """
        raise NotImplementedError

    def swap_info(self):
        """
        Returns SwapInfo
        """
        raise NotImplementedError

    def swap_device_names(self):
        """
        Returns a set that contains all swap device names available on this host

        Returned set should be a subset of a set returned by disk_device_names

        :rtype: set
        """
        raise NotImplementedError
