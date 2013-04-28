from zabby.hostos import detect_host_os

__all__ = ['maxproc', ]


def maxproc(host_os=detect_host_os()):
    """
    Returns maximum number of running processes

    :depends on: [host_os.maximum_number_of_running_processes]
    """
    return host_os.max_number_of_running_processes()
