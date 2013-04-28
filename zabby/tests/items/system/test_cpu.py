from mock import Mock
from nose.tools import assert_raises, assert_equal
from zabby.core.exceptions import WrongArgumentError
from zabby.hostos import CPU_TIMES, CpuTimes

from zabby.items.system import cpu
from zabby.tests import assert_is_instance, assert_greater


class TestUtil():
    def setup(self):
        self.host_os = Mock()
        self.host_os.cpu_count.return_value = 4

        self.host_os.cpu_times.return_value = CpuTimes(*[1 for _ in CPU_TIMES])
        self.host_os.cpu_times_shifted.return_value = CpuTimes(
            *[2 for _ in CPU_TIMES])

    def test_raises_exception_for_unknown_state(self):
        assert_raises(WrongArgumentError, cpu.util, state='wrong',
                      host_os=self.host_os)

    def test_raises_exception_for_unknown_cpu(self):
        assert_raises(WrongArgumentError, cpu.util, self.host_os.cpu_count(),
                      host_os=self.host_os)

    def test_does_not_raise_exception_for_cpu_all(self):
        cpu.util('all', host_os=self.host_os)

    def test_raises_exception_for_unknown_mode(self):
        assert_raises(WrongArgumentError, cpu.util, mode='wrong',
                      host_os=self.host_os)

    def test_returns_float_less_than_hundred(self):
        for state in CPU_TIMES:
            percent = cpu.util('all', state=state, host_os=self.host_os)
            assert_is_instance(percent, float)
            assert_greater(100, percent)

    def test_returns_zero_for_empty_history(self):
        self.host_os.cpu_times_shifted.return_value = None
        for state in CPU_TIMES:
            percent = cpu.util('all', state=state, host_os=self.host_os)
            assert_is_instance(percent, float)
            assert_equal(0, percent)
