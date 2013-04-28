from mock import Mock, patch
from nose.tools import assert_equal
from zabby.tests import assert_less_equal

from zabby.hostos import HostOS, DiskDeviceStats
from zabby.hostos.collectors import DiskDeviceStatsCollector


class TestHostOSCollectors():
    def setup(self):
        self.host_os = HostOS()
        self.collectors = list()
        for i in range(2):
            collector = Mock()
            self.collectors.append(collector)
            self.host_os._collectors.append(collector)

    def test_start_collectors_runs_every_collector(self):
        self.host_os.start_collectors()
        for collector in self.collectors:
            collector.run.assert_called_once_with()

    def test_stop_collectors_stops_every_collector(self):
        self.host_os.stop_collectors()
        for collector in self.collectors:
            collector.stop.assert_called_once_with()


DEVICE_NAME = 'dev0'


class TestDiskDeviceStatsCollector():
    def setup(self):
        self._patcher = patch('zabby.hostos.collectors.time')
        self.mock_time = self._patcher.start()

        self.now = 0

        def increment_and_return_now():
            self.now += 1
            return self.now

        self.mock_time.side_effect = increment_and_return_now

        self.host_os = Mock()

        self.stat = 0

        def increment_and_return_stats(device):
            self.stat += 1
            return DiskDeviceStats(
                read_sectors=0, read_operations=self.stat, read_bytes=0,
                write_sectors=0, write_operations=0, write_bytes=0
            )

        self.host_os.disk_device_stats.side_effect = increment_and_return_stats
        self.host_os.disk_device_names.return_value = set([DEVICE_NAME])

        interval = 1
        self.shift = 5
        self.current_time = self.shift + 1
        self.collector = DiskDeviceStatsCollector(self.shift, interval,
                                                  self.host_os)

    def teardown(self):
        self._patcher.stop()

    def test_returns_none_if_history_is_empty(self):
        stats, timestamp = self.collector.get_stats(DEVICE_NAME, self.shift,
                                                    self.current_time)
        assert_equal((None, None), (stats, timestamp))

    def test_returns_not_completely_shifted_stats_for_unfilled_history(self):
        self.collector._collect()

        stats, timestamp = self.collector.get_stats(DEVICE_NAME, self.shift,
                                                    self.current_time)
        assert_less_equal(self.shift, self.current_time - timestamp)

    def test_returns_completely_shifted_stats_for_filled_history(self):
        for i in range(self.shift + 1):
            self.collector._collect()

        stats, timestamp = self.collector.get_stats(DEVICE_NAME, self.shift,
                                                    self.current_time)
        assert_equal(self.shift, self.current_time - timestamp)
