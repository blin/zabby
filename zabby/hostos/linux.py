import os

from zabby.core.utils import lists_from_file
from zabby.hostos import HostOS, NetworkInterfaceInfo


class Linux(HostOS):
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
