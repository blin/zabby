from six.moves import socketserver

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


class AgentRequestHandler(socketserver.BaseRequestHandler):
    """
    This class is a proxy for protocol interaction and data retrieval
    It should be used with socketserver.TCPServer
    """

    def setup(self):
        self.protocol = get_protocol()
        self.data_source = get_data_source()

    def handle(self):
        key = self.protocol.receive_key(self.request)
        response = self.data_source.process(key)
        self.protocol.send_response(self.request, response)
