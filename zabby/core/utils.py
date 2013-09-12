from __future__ import division
import socket
import logging
from subprocess import Popen, PIPE

from itertools import islice
import time
from zabby.core.exceptions import WrongArgumentError, OperatingSystemError
from zabby.core.six import binary_type


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
            "Unknown mode '{mode}' should be one of {modes}".format(
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


def lines_from_file(file_path, n=None):
    """
    Returns list of lines read from file

    :param n: Number of lines to read from file
    :raises: OperatingSystemError if file is empty
    :raises: IOError if unable to read lines from file
    """
    with open(file_path, "r") as f:
        lines = list(islice((line.rstrip() for line in f), n))

    if len(lines) == 0:
        raise OperatingSystemError("{file} is empty".format(file=file_path))

    return lines


def lists_from_file(file_path, sep=None, maxsplit=-1):
    """
    Returns list of lists read from file

    List is constructed by splitting every line with line.split(sep, maxsplit)
    """
    lines = lines_from_file(file_path)
    return [line.split(sep, maxsplit) for line in lines]


def dict_from_file(file_path, sep=None):
    """
    Returns dict read from file

    Dict is constructed by making first element a key and the rest a value
    """
    lists = lists_from_file(file_path, sep, 1)
    d = dict()
    for l in lists:
        if len(l) == 2:  # exclude lines without value
            key, value = l
            d[key] = value
    return d


BYTE_SCALE = {
    'kB': 1024,
    'mB': 1024 * 1024,
    'GB': 1024 * 1024 * 1024,
    'TB': 1024 * 1024 * 1024 * 1024,
}


def to_bytes(value, factor):
    """
    Converts value with a factor, such as '10 kB' to bytes

    :raises: ValueError if value is not convertible to int
    :raises: WrongArgumentError if factor is not known
    """
    validate_mode(factor, BYTE_SCALE.keys())

    return int(value) * BYTE_SCALE[factor]


AVERAGE_MODE = {
    'avg1': 60,
    'avg5': 300,
    'avg15': 900,
}


def sh(command, timeout=1.0, wait_step=0.01, raise_on_empty_out=True,
       raise_on_nonempty_err=False):
    """
    Creates and returns a function that when called will run command with shell
    and return it's output.

    Command can contain replacement fields as described in python documentation
    http://docs.python.org/library/string.html?highlight=formatter#format-string-syntax

    sh('command {0}')('argument') will call 'command argument'

    :param timeout: if command does not terminate in it will be killed and
        OperatingSystemError will be raised
    :param wait_step: poll interval for process running command
    :param raise_on_empty_out: whether exception should be raised if command
        does not write anything to stdout
    :param raise_on_nonempty_err: whether exception should be raised if command
        writes to stderr

    :raises: WrongArgumentError if command contains replacement fields and
        resulting function is called without arguments
    :raises: OperatingSystemError if command does not terminate until timeout
    """

    def call_command(*args):
        try:
            formatted_command = command.format(*args)
        except IndexError:
            raise WrongArgumentError(
                "'{0}' not enough arguments. Called with {1}".format(command,
                                                                     args))
        process = Popen(formatted_command, stdout=PIPE, stderr=PIPE, shell=True,
                        universal_newlines=True)

        if timeout:
            wait_time_remaining = timeout
            while process.poll() is None and wait_time_remaining > 0:
                time.sleep(wait_step)
                wait_time_remaining -= wait_step

            if wait_time_remaining <= 0:
                process.kill()
                raise OperatingSystemError(
                    "{0} have not completed in {1} seconds".format(
                        formatted_command, timeout))

        (out, err) = process.communicate()
        (out, err) = (out.rstrip(), err.rstrip())

        if out == '' and raise_on_empty_out:
            raise OperatingSystemError(
                "'{0}' has not written to stdout".format(formatted_command))

        if err != '':
            message = "'{0}' has written to stderr: {1}".format(
                formatted_command, err)

            if raise_on_nonempty_err:
                raise OperatingSystemError(message)
            else:
                log = logging.getLogger('sh')
                log.warn(message)

        return out

    return call_command


def tcp_communication(port, host='localhost', requests=list(),
                      receive_first=False, timeout=1.0):
    """
    Connects to port, optionally sending requests and returns any responses

    :param requests: list of binary objects that will be sent in order
        it is expected that there will be a response for every request
    :param receive_first: if true will try to receive data before sending any
        requests

    :raises: IOError, no exception handling is done in this function, most
        exceptions will be socket exceptions
    """
    if any([not isinstance(request, binary_type) for request in requests]):
        raise WrongArgumentError("Every request should be in binary. "
                                 "Requests: '{0}'".format(requests))

    conn = None
    responses = list()
    try:
        conn = socket.create_connection((host, port), timeout=timeout)
        if receive_first:
            responses.append(conn.recv(4096))

        for request in requests:
            conn.sendall(request)
            responses.append(conn.recv(4096))

    finally:
        if conn is not None:
            conn.close()

    return responses


def exception_guard(function, exception_class=Exception, sentinel=0):
    """
    Returns a wrapper over function that calls function in a try block
    if exception_class is raised sentinel value will be returned
    """
    def wrapper(*args):
        try:
            return function(*args)
        except exception_class:
            return sentinel

    return wrapper
