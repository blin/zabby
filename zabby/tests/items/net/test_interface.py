from mock import Mock
from nose.tools import assert_raises, nottest, istest
from zabby.core.six import integer_types
from zabby.hostos import NetworkInterfaceInfo
from zabby.tests import assert_is_instance

from zabby.core.exceptions import WrongArgumentError
from zabby.items.net import interface
from zabby.items.net.interface import NET_MODES

INTERFACE_NAME = 'lo'


@nottest
class TestNetDirection():
    def setup_host_os(self):
        self.host_os = Mock()
        self.host_os.net_interface_names.return_value = set([INTERFACE_NAME])
        self.host_os.net_interface_info.return_value = NetworkInterfaceInfo(
            in_bytes=1, in_packets=1, in_errors=1, in_dropped=1,
            out_bytes=1, out_packets=1, out_errors=1, out_dropped=1,
            collisions=1
        )

    def test_raises_exception_if_wrong_mode_is_provided(self):
        assert_raises(WrongArgumentError, self.function_under_test,
                      INTERFACE_NAME, 'wrong')

    def test_raises_exception_if_interface_name_is_not_available(self):
        self.host_os.net_interface_names.return_value = set()
        assert_raises(WrongArgumentError, self.function_under_test,
                      INTERFACE_NAME, self.host_os)

    def test_returns_integer(self):
        for mode in NET_MODES:
            value = self.function_under_test(INTERFACE_NAME, mode, self.host_os)
            assert_is_instance(value, integer_types)


@istest
class TestIncoming(TestNetDirection):
    def setup(self):
        self.setup_host_os()
        self.function_under_test = interface.incoming


@istest
class TestOutgoing(TestNetDirection):
    def setup(self):
        self.setup_host_os()
        self.function_under_test = interface.outgoing
