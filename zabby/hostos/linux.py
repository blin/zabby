import os
from ctypes import (cdll, Structure, POINTER, c_int, c_char_p)

from zabby.core.exceptions import OperatingSystemError
from zabby.core.six import b
from zabby.core.utils import (lists_from_file, lines_from_file, dict_from_file,
                              to_bytes)
from zabby.hostos import HostOS, NetworkInterfaceInfo, ProcessInfo

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
