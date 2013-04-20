from __future__ import division
import sys

from zabby.core.exceptions import WrongArgumentError

PY3 = sys.version_info[0] == 3

if PY3:
    def b(s):
        return s.encode('utf-8')

    def u(s):
        return s

    string_types = str,
    integer_types = int,
else:
    def b(s):
        return s

    def u(s):
        return s.decode('utf-8')

    string_types = basestring,
    integer_types = (int, long)


def write_to_file(file_path, value):
    """ Converts value to string and writes it to file followed by newline"""
    with open(file_path, mode='a') as f:
        f.write(str(value))
        f.write("\n")
        f.flush()


def validate_mode(mode, available_modes):
    """
    Checks if mode is one of available_modes

    :raises: WrongArgumentError if mode is not one of available_modes
    """
    if mode not in available_modes:
        raise WrongArgumentError(
            'Unknown mode "{mode}" should be one of {modes}'.format(
                mode=mode, modes=available_modes))


SIZE_CONVERSION_MODES = ['free', 'total', 'used', 'pfree', 'pused', ]


def convert_size(free, total, mode):
    """
    Takes free and total size and coverts them based on conversion mode

    free - returns free
    total - returns total
    used - returns difference between total and free
    pfree - returns free as percentage of total
    pused - returns used as percentage of total

    :param mode: one of SIZE_CONVERSION_MODES
    """
    if total == 0:
        return 0  # even if free is not 0, it is better to alert authorities
    value = None
    if mode == 'free':
        value = free
    elif mode == 'total':
        value = total
    elif mode == 'used':
        value = total - free
    elif mode == 'pfree':
        value = (free / total) * 100
    elif mode == 'pused':
        used = (total - free)
        value = (used / total) * 100
    return value
