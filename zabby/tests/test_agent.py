# coding=utf-8
import struct
from mock import Mock, ANY
from nose.tools import assert_equal
from zabby.core.exceptions import WrongArgumentError

from zabby.tests import assert_is_instance
from zabby.core.six import b, u, string_types
from zabby.agent import (AgentRequestHandler, set_protocol, set_data_source,
                         ZBXDProtocol, DataSource, KeyParser)

KEY = 'unicode/юникод'
KEY_PROCESS_RESULT = 'result/результат'
RETURN_VALUE = 1


class TestAgentRequestHandler():
    def handle(self):
        """
        AgentRequestHandler.handle is called as soon as class is instantiated
        """
        AgentRequestHandler(None, None, None)

    def setup(self):
        self.protocol = Mock()
        self.protocol.receive_value.return_value = KEY
        set_protocol(self.protocol)

        self.data_source = Mock()
        self.data_source.process.return_value = KEY_PROCESS_RESULT
        set_data_source(self.data_source)

    def test_handle_receives_key(self):
        self.handle()
        self.protocol.receive_value.assert_called_with(ANY)

    def test_handle_passes_received_key_to_data_source_for_processing(self):
        self.handle()
        self.data_source.process.assert_called_with(KEY)

    def test_handle_sends_key_process_result_to_client(self):
        self.handle()
        self.protocol.send_value.assert_called_with(ANY, KEY_PROCESS_RESULT)


class TestProtocol():
    def setup(self):
        self.client = Mock()
        self.protocol = ZBXDProtocol()

    def test_receive_key_zbxd(self):
        sent_key = KEY
        self.client.recv.side_effect = [
            self.protocol.HEADER,
            struct.pack('q', len(sent_key)),
            b(sent_key)
        ]
        received_key = self.protocol.receive_value(self.client)
        assert_is_instance(received_key, string_types)
        assert_equal(u(sent_key), received_key)

    def test_send_value(self):
        self.protocol.send_value(self.client, 1)
        self.client.sendall.assert_called_with(ANY)
        assert_is_instance(self.client.sendall.call_args[0][0], bytes)

        self.protocol.send_value(self.client, "1")
        self.client.sendall.assert_called_with(ANY)
        assert_is_instance(self.client.sendall.call_args[0][0], bytes)


class TestDataSource():
    def setup(self):
        self.key_parser = Mock()
        self.key_parser.parse = lambda raw_key: (raw_key, [])

        self.config = Mock()
        self.function = Mock()
        self.function.return_value = RETURN_VALUE
        self.config.items = {
            KEY: self.function
        }

        self.data_source = DataSource(self.key_parser, self.config)

    def test_calls_function(self):
        value = self.data_source.process(KEY)
        assert_equal(RETURN_VALUE, value)
        self.function.assert_any_call()

    def test_passes_arguments_to_function(self):
        argument = 1
        self.key_parser.parse = lambda raw_key: (raw_key, [argument])

        value = self.data_source.process(KEY)
        assert_equal(RETURN_VALUE, value)
        self.function.assert_any_call(argument)

    def test_returns_default_value_for_unknown_key(self):
        value = self.data_source.process('unknown_key')
        assert_equal(self.data_source.DEFAULT_VALUE, value)

    def test_calling_function_that_does_not_need_arguments(self):
        self.config.items[KEY] = lambda x: x
        value = self.data_source.process(KEY)
        assert_equal(self.data_source.DEFAULT_VALUE, value)

    def test_calling_function_with_wrong_arguments(self):
        function = Mock()
        function.side_effect = WrongArgumentError
        self.config.items[KEY] = function
        value = self.data_source.process(KEY)
        assert_equal(self.data_source.DEFAULT_VALUE, value)

    def test_calling_function_that_raises_unexpected_exception(self):
        function = Mock()
        function.side_effect = Exception
        self.config.items[KEY] = function
        value = self.data_source.process(KEY)
        assert_equal(self.data_source.DEFAULT_VALUE, value)


class TestKeyParser():
    def setUp(self):
        self.parser = KeyParser()

    def test_key_without_arguments(self):
        key, arguments = self.parser.parse(KEY)
        assert_equal(0, len(arguments))

    def test_key_with_one_argument(self):
        key, arguments = self.parser.parse(KEY + '[1]')
        assert_equal(1, len(arguments))

    def test_key_with_newline(self):
        key, arguments = self.parser.parse(KEY + '\n')
        assert_equal(KEY, key)