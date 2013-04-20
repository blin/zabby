import os

from zabby.hostos import HostOS


class Linux(HostOS):
    def fs_size(self, filesystem):
        """
        Uses statvfs system call to obtain information about filesystem
        """
        statvfs_struct = os.statvfs(filesystem)
        total = statvfs_struct.f_blocks * statvfs_struct.f_bsize
        free = statvfs_struct.f_bavail * statvfs_struct.f_bsize
        return free, total
