from nose.plugins.attrib import attr

from zabby.core.six import integer_types, string_types
from zabby.hostos import detect_host_os, NetworkInterfaceInfo
from zabby.tests import assert_is_instance, assert_less, assert_in

PRESENT_FILESYSTEM = '/'
PRESENT_INTERFACE = 'lo'


@attr(os='linux')
class TestLinux():
    def setup(self):
        from zabby.hostos.linux import Linux
        self.linux = Linux()

    def test_linux_is_detected_correctly(self):
        detected_os = detect_host_os()
        assert_is_instance(detected_os, self.linux.__class__)

    def test_fs_size_returns_tuple_of_integers_one_less_than_other(self):
        free, total = self.linux.fs_size(PRESENT_FILESYSTEM)

        assert_is_instance(free, integer_types)
        assert_is_instance(total, integer_types)

        assert_less(free, total)

    def test_fs_inodes_returns_tuple_of_integers_one_less_than_other(self):
        free, total = self.linux.fs_inodes(PRESENT_FILESYSTEM)

        assert_is_instance(free, integer_types)
        assert_is_instance(total, integer_types)

        assert_less(free, total)

    def test_net_interface_names_returns_set_of_strings(self):
        interface_names = self.linux.net_interface_names()

        assert_is_instance(interface_names, set)
        for interface_name in interface_names:
            assert_is_instance(interface_name, string_types)
        assert_in(PRESENT_INTERFACE, interface_names)

    def test_net_interface_info_returns_NetworkInterfaceInfo(self):
        interface_names = self.linux.net_interface_names()
        interface_info = self.linux.net_interface_info(interface_names.pop())

        assert_is_instance(interface_info, NetworkInterfaceInfo)
        for key, value in interface_info._asdict().items():
            assert_is_instance(value, integer_types)
