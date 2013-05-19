import logging
import re

from zabby.core.utils import validate_mode, tcp_communication


__all__ = ['service', ]

LOG = logging.getLogger(__name__)


def service(service_name, ip='127.0.0.1', port=None, timeout=1.0):
    """
    Returns 1 if service running on port accepts connections and behaves as
    expected, 0 otherwise

    :param service_name: specifies expected behaviour and port
        ssh:
            behavior: should respond with a greeting message upon connection
            port: 22
    :param port: overrides port specified by service_name

    :raises: WrongArgument if unsupported service_name is supplied
    """
    validate_mode(service_name, SERVICES.keys())
    port = int(port) if port else SERVICES[service_name]

    if service_name == 'ssh':
        running = _check_ssh(ip, port, timeout)
    else:
        running = False

    return int(running)


SERVICES = {
    'ssh': 22,
}


def _check_ssh(ip, port, timeout):
    running = False
    try:
        responses = tcp_communication(port, ip, receive_first=True,
                                      timeout=timeout)
        server_message = responses[0].decode('utf-8')
        if re.match('SSH-(?P<version>[0-9-. ]+)-', server_message):
            running = True
        else:
            LOG.debug("Server message does not match expectations {0}".format(
                server_message))
    except IOError as e:
        LOG.debug("SSH service is not running: {0}".format(e))
    return running
