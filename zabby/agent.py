import string
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
    MAX_KEY_LENGTH = 65536
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


class ArgumentParser():
    def __init__(self, quote='"', separator=','):
        self.quote = quote
        self.separator = separator
        self.to_strip = self.quote + string.whitespace

    def parse(self, unparsed_arguments):
        """
        Separates arguments based on separator and strips them of quotes and
        whitespace
        """
        raise NotImplementedError()


class ArgumentParserWithQuoting(ArgumentParser):
    """
    This argument parser allows for separator inside quoted arguments
    To use quote inside argument you should escape it with backslash character

    "ar\",g0","ar\",g1" will be parsed as ['ar",g0', 'ar",g1']

    Empty arguments are(grudgingly) supported
    ,arg0 and "","arg0" will be parsed as ['','arg0']
    , will be parsed as ['']
    """

    def parse(self, unparsed_arguments):
        arguments = list()

        while len(unparsed_arguments) != 0:
            argument_end = self._find_argument_end(unparsed_arguments)

            argument = unparsed_arguments[:argument_end]
            argument = argument.strip(self.to_strip)
            argument = argument.replace('\\' + self.quote, self.quote)
            arguments.append(argument)
            unparsed_arguments = unparsed_arguments[argument_end + 1:]

        return arguments

    def _find_first_comma(self, unparsed_arguments, start):
        first_comma_position = unparsed_arguments.find(self.separator, start)
        return (first_comma_position
                if first_comma_position >= 0
                else len(unparsed_arguments))

    def _find_quoted_argument_end(self, unparsed_arguments):
        argument_end_found = False
        start = 1
        while not argument_end_found:
            quote_position = unparsed_arguments.find(self.quote, start)
            if quote_position == -1:
                raise WrongArgumentError('Missing terminating quote')
            start = quote_position + 1

            quote_escaped = unparsed_arguments[quote_position - 1] == '\\'
            if not quote_escaped:
                argument_end_found = True
        return self._find_first_comma(unparsed_arguments, start)

    def _find_argument_end(self, unparsed_arguments):
        quoted = unparsed_arguments[0] == self.quote
        if quoted:
            return self._find_quoted_argument_end(unparsed_arguments)
        else:
            return self._find_first_comma(unparsed_arguments, 0)


class KeyParser():
    def __init__(self, argument_parser=ArgumentParserWithQuoting()):
        self.argument_parser = argument_parser

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
        has_arguments = opening_bracket_index != -1
        if has_arguments:
            key = raw_key[:opening_bracket_index]
            closing_bracket_index = raw_key.rfind("]")
            if closing_bracket_index == -1:
                raise WrongArgumentError('Missing terminating bracket')
            unparsed_arguments = (raw_key[
                                  opening_bracket_index + 1:
                                  closing_bracket_index])
            arguments = self.argument_parser.parse(unparsed_arguments)
        else:
            key = raw_key
            arguments = []

        return key, arguments
