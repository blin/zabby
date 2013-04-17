from mock import Mock, ANY

from zabby.agent import AgentRequestHandler, set_protocol, set_data_source

RECEIVED_KEY = "key"
KEY_PROCESS_RESULT = "result"


class TestAgentRequestHandler():
    def handle(self):
        """
        AgentRequestHandler.handle is called as soon as class is instantiated
        """
        AgentRequestHandler(None, None, None)

    def setup(self):
        self.protocol = Mock()
        self.protocol.receive_key.return_value = RECEIVED_KEY
        set_protocol(self.protocol)

        self.data_source = Mock()
        self.data_source.process.return_value = KEY_PROCESS_RESULT
        set_data_source(self.data_source)

    def test_handle_receives_key(self):
        self.handle()
        self.protocol.receive_key.assert_called_with(ANY)

    def test_handle_passes_received_key_to_data_source_for_processing(self):
        self.handle()
        self.data_source.process.assert_called_with(RECEIVED_KEY)

    def test_handle_sends_key_process_result_to_client(self):
        self.handle()
        self.protocol.send_response.assert_called_with(ANY, KEY_PROCESS_RESULT)
