from mock import patch
from nose.tools import assert_true, assert_false

from zabby.core.six import b
from zabby.items.net import tcp


class TestServiceSSH():
    def setup(self):
        self._patcher_tcp_communication = patch(
            'zabby.items.net.tcp.tcp_communication')
        self.mock_tcp_communication = self._patcher_tcp_communication.start()

        self.service_name = 'ssh'

    def teardown(self):
        self._patcher_tcp_communication.stop()

    def test_running_if_server_message_matches_expectations(self):
        self.mock_tcp_communication.return_value = [
            b('SSH-2.0-OpenSSH_6.0p1 Debian-4\n')]
        running = bool(tcp.service(self.service_name))
        assert_true(running)

    def test_not_running_if_server_message_does_not_match_expectations(self):
        self.mock_tcp_communication.return_value = [b('SSH\n')]
        running = bool(tcp.service(self.service_name))
        assert_false(running)

    def test_not_running_if_exception_occurs(self):
        self.mock_tcp_communication.side_effect = IOError
        running = bool(tcp.service(self.service_name))
        assert_false(running)
