import os
from ctypes import (cdll, Structure, POINTER, c_int, c_char_p, c_long, c_ulong,
                    c_ushort, c_uint, c_char, byref)
import socket

from zabby.core.exceptions import OperatingSystemError
from zabby.core.six import b
from zabby.core.utils import (lists_from_file, lines_from_file, dict_from_file,
                              to_bytes)
from zabby.hostos import (HostOS, NetworkInterfaceInfo, ProcessInfo,
                          DiskDeviceStats, CpuTimes, SystemLoad, SwapInfo)
from zabby.hostos.collectors import DiskDeviceStatsCollector, CpuTimesCollector

_libc = cdll.LoadLibrary("libc.so.6")


class StructPasswd(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("passwd", c_char_p),
        ("uid", c_int),
        ("gid", c_int),
        ("gecos", c_char_p),
        ("dir", c_char_p),
        ("shell", c_char_p),
    ]


_libc.getpwnam.argtypes = [c_char_p]
_libc.getpwnam.restype = POINTER(StructPasswd)


class StructSysinfo(Structure):
    _fields_ = [
        ("uptime", c_long),
        ("loads", c_ulong * 3),
        ("totalram", c_ulong),
        ("freeram", c_ulong),
        ("sharedram", c_ulong),
        ("bufferram", c_ulong),
        ("totalswap", c_ulong),
        ("freeswap", c_ulong),
        ("procs", c_ushort),
        ("totalhigh", c_ulong),
        ("freehigh", c_ulong),
        ("mem_unit", c_uint),
        ('__padding', c_char * 64),
    ]

_libc.sysinfo.argtypes = [POINTER(StructSysinfo)]

PROCESS_STATE_MAP = {
    "R (running)": "run",
    "S (sleeping)": "sleep",
    "Z (zombie)": "zomb",
}


class Linux(HostOS):
    AVAILABLE_MEMORY_TYPES = set([
        'total',
        'free',
        'buffers',
        'cached',
        'available',
        'pavailable',
        'used',
        'pused',
    ])
    AVAILABLE_DISK_DEVICE_STATS_TYPES = set(['sectors', 'operations'])

    def __init__(self):
        super(Linux, self).__init__()

        self._disk_device_stats_collector = DiskDeviceStatsCollector(900, self)
        self._collectors.append(self._disk_device_stats_collector)

        self._cpu_times_collector = CpuTimesCollector(900, self)
        self._collectors.append(self._cpu_times_collector)

    def fs_size(self, filesystem):
        """
        Uses statvfs system call to obtain information about filesystem

        See `man 3 statvfs` for more information
        """
        statvfs_struct = os.statvfs(filesystem)
        total = statvfs_struct.f_blocks * statvfs_struct.f_bsize
        free = statvfs_struct.f_bavail * statvfs_struct.f_bsize
        return free, total

    def fs_inodes(self, filesystem):
        """
        Uses statvfs system call to obtain information about filesystem

        See `man 3 statvfs` for more information
        """
        statvfs_struct = os.statvfs(filesystem)
        total = statvfs_struct.f_files
        free = statvfs_struct.f_ffree
        return free, total

    def net_interface_names(self):
        """
        Uses /proc/net/dev to obtain device names

        See `man 5 proc` for more information
        """
        interface_infos = self._net_interface_infos()

        return set(interface_infos.keys())

    def net_interface_info(self, net_interface_name):
        """
        Uses /proc/net/dev to obtain device names

        See `man 5 proc` for more information
        """
        interface_infos = self._net_interface_infos()

        return interface_infos[net_interface_name]

    def _net_interface_infos(self):
        lists = lists_from_file("/proc/net/dev")
        interface_infos = lists[2:]

        interface_stats = dict()
        for interface_info in interface_infos:
            interface_name = interface_info[0].rstrip(':')
            incoming = [int(value) for value in interface_info[1:5]]
            outgoing = [int(value) for value in interface_info[9:13]]
            collisions = [int(interface_info[15])]
            interface_stats[interface_name] = NetworkInterfaceInfo(
                *(incoming + outgoing + collisions))

        return interface_stats

    def process_infos(self):
        """
        Uses /proc/{pid}/status to obtain information about process name,
        effective UID, state and used memory
        Uses /proc/{pid}/cmdline to obtain information about command line

        {pid} directories are obtained ones by listing all files containing only
        digits in /proc

        See `man 5 proc` for more information
        """
        for process_id in self._process_ids():
            try:
                command_line = self._process_command_line(process_id)
            except OperatingSystemError:
                # kernel threads do not contain command line
                # we are not interested in them
                continue

            status = self._process_status(process_id)

            yield ProcessInfo(
                name=status['Name'],
                uid=status['Uid'],
                state=status['State'],
                command_line=command_line,
                used_memory=status['VmSize']
            )

    def _process_ids(self):
        return [dir_name
                for dir_name in os.listdir('/proc')
                if dir_name.isdigit()]

    def _process_command_line(self, process_id):
        proc_cmd_line = os.path.join('/proc', process_id, 'cmdline')
        proc_cmd_line = lines_from_file(proc_cmd_line)[0]

        return proc_cmd_line.replace('\0', ' ').rstrip()

    def _process_status(self, process_id):
        process_status_file_path = os.path.join('/proc', process_id, 'status')
        process_status = dict_from_file(process_status_file_path, ':\t')

        process_status['Uid'] = int(
            process_status['Uid'].split('\t')[0]
        )  # only effective UID is needed
        process_status['State'] = PROCESS_STATE_MAP.get(
            process_status['State'], 'sleep'
        )
        process_status['VmSize'] = to_bytes(*process_status['VmSize'].split())

        return process_status

    def uid(self, username):
        """
        Uses getpwnam system call to obtain UID

        See `man 3 getpwnam` for more information
        """
        return self._passwd(username).uid

    def _passwd(self, username):
        pointer_to_passwd = _libc.getpwnam(b(username))
        if pointer_to_passwd:
            return pointer_to_passwd[0]
        else:
            raise OperatingSystemError('Invalid name: {0}'.format(username))

    def memory(self):
        """
        Uses /proc/meminfo to obtain information on memory usage

        See `man 5 proc` for more information
        """
        mem_info = dict_from_file('/proc/meminfo')
        total = to_bytes(*mem_info['MemTotal:'].split())
        free = to_bytes(*mem_info['MemFree:'].split())
        buffers = to_bytes(*mem_info['Buffers:'].split())
        cached = to_bytes(*mem_info['Cached:'].split())

        available = free + buffers + cached
        pavailable = (available * 100) / total

        used = total - available
        pused = (used * 100) / total

        return {
            'total': total,
            'free': free,
            'buffers': buffers,
            'cached': cached,
            'available': available,
            'pavailable': pavailable,
            'used': used,
            'pused': pused,
        }

    def disk_device_names(self):
        """
        Obtains information from '/proc/diskstats'

        See `man 5 proc` for more information
        """
        return set(self._disk_devices_stats().keys())

    def disk_device_stats(self, device):
        """
        Obtains information from '/proc/diskstats'

        See `man 5 proc` for more information
        """
        return self._disk_devices_stats()[device]

    def _disk_devices_stats(self):
        diskstats = dict()
        disks = lists_from_file('/proc/diskstats')
        for disk in disks:
            device = disk[2]
            diskstat = DiskDeviceStats(
                read_sectors=int(disk[5]),
                read_operations=int(disk[3]),
                read_bytes=0,
                write_sectors=int(disk[9]),
                write_operations=int(disk[7]),
                write_bytes=0
            )
            diskstats[device] = diskstat
        return diskstats

    def disk_device_stats_shifted(self, device, shift, now):
        """
        Obtains information from DiskDeviceStatsCollector
        """
        return self._disk_device_stats_collector.get_stats(device, shift, now)

    def cpu_count(self):
        """
        Obtains information from /proc/stat

        See `man 5 proc` for more information
        """
        return len(self._cpus_times())

    def cpu_times(self, cpu_id):
        """
        Obtains information from /proc/stat

        See `man 5 proc` for more information
        """
        return self._cpus_times()[cpu_id]

    def _cpus_times(self):
        stats = lists_from_file('/proc/stat')
        cpus_times = []
        for stat in stats:
            key, values = stat[0], stat[1:]
            if key.startswith('cpu') and key != 'cpu':
                cpu_times = [int(cpu_time) for cpu_time in values[:7]]
                cpus_times.append(CpuTimes(*cpu_times))

        return cpus_times

    def cpu_times_shifted(self, cpu_id, shift):
        """
        Obtains information from CpuTimesCollector
        """
        return self._cpu_times_collector.get_times(cpu_id, shift)

    def hostname(self, hostname_type):
        """
        Obtains information from python socket.gethostname()

        :param hostname_type: is ignored
        """
        return socket.gethostname()

    def uname(self):
        """
        Obtains information from python os.uname()
        """
        return os.uname()

    def uptime(self):
        """
        Obtains information from /proc/uptime

        See `man 5 proc` for more information
        """
        return int(float(lists_from_file('/proc/uptime')[0][0]))

    def max_number_of_running_processes(self):
        """
        Obtains information from /proc/sys/kernel/pid_max

        See `man 5 proc` for more information
        """
        return int(lines_from_file("/proc/sys/kernel/pid_max")[0])

    def system_load(self):
        """
        Obtains information from python os.getloadavg()
        """
        return SystemLoad(*os.getloadavg())

    def swap_size(self, device):
        """
        Obtains information from sysinfo system call

        See `man 2 sysinfo` for more information

        :param device: ignored, always returns system wide information
        """
        sysinfo_struct = StructSysinfo()
        _libc.sysinfo(byref(sysinfo_struct))

        return (sysinfo_struct.freeswap * sysinfo_struct.mem_unit,
                sysinfo_struct.totalswap * sysinfo_struct.mem_unit)

    def swap_info(self):
        """
        Obtains information from /proc/vmstat

        See `man 5 proc` for more information
        """
        vmstat = dict_from_file('/proc/vmstat')

        return SwapInfo(read=int(vmstat['pswpin']),
                        write=int(vmstat['pswpout']))
