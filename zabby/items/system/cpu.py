from __future__ import division

from zabby.core.utils import validate_mode, AVERAGE_MODE
from zabby.hostos import detect_host_os, CPU_TIMES

__all__ = ['util', ]


def util(cpu='all', state='user', mode='avg1', host_os=detect_host_os()):
    """
    Returns average percentage of time spent by cpu in a state over a period
    of time

    :raises: WrongArgumentError if unknown cpu is supplied
    :raises: WrongArgumentError if unknown state is supplied
    :raises: WrongArgumentError if unknown mode is supplied

    :depends on: [host_os.cpu_count, host_os.cpu_times_shifted,
                  host_os.cpu_times]
    """
    validate_mode(state, CPU_TIMES)

    available_cpus = list(range(host_os.cpu_count()))
    if cpu == 'all':
        cpus = available_cpus
    else:
        cpu = int(cpu)
        validate_mode(cpu, available_cpus)
        cpus = [cpu]

    validate_mode(mode, AVERAGE_MODE.keys())

    time_in_state = 0
    time_total = 0
    for cpu in cpus:
        shifted_cpu_times = host_os.cpu_times_shifted(cpu, AVERAGE_MODE[mode])
        if shifted_cpu_times is not None:
            current_cpu_times = host_os.cpu_times(cpu)

            cpu_time_in_state = (current_cpu_times._asdict()[state] -
                                 shifted_cpu_times._asdict()[state])
            cpu_time_total = (sum(current_cpu_times) - sum(shifted_cpu_times))

            time_in_state += cpu_time_in_state
            time_total += cpu_time_total
    return (((time_in_state * 100) / time_total)
            if time_total != 0
            else 0.0)


def load(cpu='all', mode='avg1', host_os=detect_host_os()):
    """
    Returns average number of processes that are either in a runnable or
    uninterruptable state.

    :raises: WrongArgumentError if unknown cpu is supplied
    :raises: WrongArgumentError if unknown mode is supplied

    :depends on: [host_os.system_load, host_os.cpu_count]
    """
    validate_mode(cpu, ['all', 'percpu'])
    validate_mode(mode, AVERAGE_MODE.keys())

    system_load = host_os.system_load()

    value = system_load._asdict()[mode]

    if cpu == 'percpu':
        value /= host_os.cpu_count()

    return value
