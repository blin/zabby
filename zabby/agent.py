import struct
import logging
import sys
from zabby.core.exceptions import WrongArgumentError

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver
from zabby.core.six import b

LOG = logging.getLogger(__name__)

__PROTOCOL__ = None
__DATA_SOURCE__ = None


def set_protocol(protocol):
    """
    Sets the protocol that will be used by request handler
    """
    global __PROTOCOL__
    __PROTOCOL__ = protocol


def set_data_source(data_source):
    """
    Sets the data_source that will be used by request handler
    """
    global __DATA_SOURCE__
    __DATA_SOURCE__ = data_source


def get_protocol():
    """
    Returns protocol set by set_protocol
    """
    return __PROTOCOL__


def get_data_source():
    """
    Returns data_source set by set_data_source
    """
    return __DATA_SOURCE__


class AgentServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        _, value, _ = sys.exc_info()
        exception_message = str(value)
        LOG.warn(exception_message)


class AgentRequestHandler(socketserver.BaseRequestHandler):
    """
    This class is a proxy for protocol interaction and data retrieval
    It should be used with socketserver.TCPServer
    """

    def setup(self):
        self.protocol = get_protocol()
        self.data_source = get_data_source()

    def handle(self):
        key = self.protocol.receive_value(self.request)
        response = self.data_source.process(key)
        self.protocol.send_value(self.request, response)


class ZBXDProtocol():
    MAX_KEY_LENGTH = 1024
    HEADER = b'ZBXD\1'
    HEADER_LENGTH = 5
    EXPECTED_LENGTH_SIZE = 8
    RESPONSE_FORMAT = "<5sq{data_length}s"

    def receive_value(self, client):
        """
        Receives key and returns it

        Expects to receive header followed by the length of the key
        followed by the key.
        """
        received = client.recv(self.HEADER_LENGTH)
        if received == self.HEADER:
            expected_length = struct.unpack(
                'q', client.recv(self.EXPECTED_LENGTH_SIZE)
            )[0]
            key = client.recv(expected_length)
        else:
            if '\n' in received:
                key = received
            else:
                key = received + client.recv(self.MAX_KEY_LENGTH)
        return key.decode('utf-8')

    def send_value(self, client, value):
        """
        Formats value according to protocol and sends it to client
        """
        message = self._calculate_message(value)
        client.sendall(message)

    def _calculate_message(self, value):
        formatted_value = self._format(value)
        data_length = len(formatted_value)
        response = struct.pack(
            self.RESPONSE_FORMAT.format(data_length=data_length),
            self.HEADER,
            data_length,
            b(formatted_value)
        )
        return response

    def _format(self, value):
        if isinstance(value, float):
            formatted_value = '{0:.4f}'.format(value)
        else:
            formatted_value = str(value)
        return formatted_value


class DataSource:
    DEFAULT_VALUE = "ZBX_NOTSUPPORTED"

    def __init__(self, key_parser, config):
        self.key_parser = key_parser
        self.config = config

    def process(self, raw_key):
        """
        Calls function associated with raw_key and returns its result

        If function for raw_key is not present or wrong number of arguments
        is passed to it returns ZBX_NOTSUPPORTED
        """
        key, arguments = self.key_parser.parse(raw_key)
        LOG.debug("Received request for '{0}' with arguments {1}".format(
            key, arguments))

        function = None
        try:
            function = self.config.items[key]
        except KeyError:
            LOG.warning("Unknown key: {key}".format(key=key))

        value = self.DEFAULT_VALUE
        try:
            if function:
                value = function(*arguments)
        except (TypeError, WrongArgumentError) as e:
            LOG.warning(
                "Wrong arguments for key '{key}': {arguments}".format(
                    key=key, arguments=arguments))
            LOG.warning(e)
        except Exception as e:
            LOG.error(
                "When calling function for '{key}' with {arguments}".format(
                    key=key, arguments=arguments))
            LOG.error("Unexpected exception occurred: {0}".format(e))

        LOG.debug("Responding with {0}".format(value))
        return value


class KeyParser():
    def parse(self, raw_key):
        """
        Separates key from arguments

        :returns: Tuple containing key and a list of arguments

        >>> KeyParser().parse('key')
        ('key', [])
        >>> KeyParser().parse('key[1]')
        ('key', ['1'])
        >>> KeyParser().parse('key[1,2]')
        ('key', ['1', '2'])
        """
        raw_key = raw_key.rstrip()

        opening_bracket_index = raw_key.find("[")
        if opening_bracket_index != -1:
            key = raw_key[:opening_bracket_index]
            unparsed_arguments = raw_key[opening_bracket_index + 1:-1]
            arguments = unparsed_arguments.split(",")
        else:
            key = raw_key
            arguments = []

        return key, arguments
