import logging
import time

LOG = logging.getLogger(__name__)


class Collector:
    """
    Collector continuously runs in the background and collects information
    (usually from host_os) for later aggregation
    """
    def __init__(self, interval, host_os):
        self._host_os = host_os
        self._running = False
        self._interval = interval

    def _collect(self):
        raise NotImplementedError

    def run(self):
        self._running = True
        while self._running:
            self._collect()
            time.sleep(self._interval)

    def stop(self):
        self._running = False
