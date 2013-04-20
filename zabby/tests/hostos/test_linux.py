from nose.plugins.attrib import attr

from zabby.core.utils import integer_types
from zabby.hostos import detect_host_os
from zabby.tests import assert_is_instance, assert_less

PRESENT_FILESYSTEM = '/'


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
