import sys

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


class HostOS(object):
    """
    Represents abstract operating system

    It contains abstract methods that concrete operating systems may provide
    Different data extraction operations may be enabled by implementing these
    methods
    """

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
