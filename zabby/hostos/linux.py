import os

from zabby.hostos import HostOS


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
