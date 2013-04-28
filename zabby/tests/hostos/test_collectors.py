from mock import Mock

from zabby.hostos import HostOS


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
