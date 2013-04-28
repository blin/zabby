from mock import Mock
from nose.tools import assert_raises, assert_equal
from zabby.core.exceptions import WrongArgumentError
from zabby.hostos import CPU_TIMES, CpuTimes, SystemLoad

from zabby.items.system import cpu
from zabby.tests import assert_is_instance, assert_greater, assert_less


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


class TestLoad():
    def setup(self):
        self.host_os = Mock()
        self.host_os.cpu_count.return_value = 4

        self.host_os.system_load.return_value = SystemLoad(1, 1, 1)

    def test_raises_exception_for_unknown_cpu(self):
        assert_raises(WrongArgumentError, cpu.load, cpu='wrong',
                      host_os=self.host_os)

    def test_raises_exception_for_unknown_mode(self):
        assert_raises(WrongArgumentError, cpu.load, mode='wrong',
                      host_os=self.host_os)

    def test_per_cpu_load_is_smaller_than_total_load(self):
        total_load = cpu.load('all', host_os=self.host_os)
        per_cpu_load = cpu.load('percpu', host_os=self.host_os)

        assert_less(per_cpu_load, total_load)
