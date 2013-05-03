from mock import Mock
from nose.tools import istest
from zabby.tests import TestSizeFunction

from zabby.items.system import swap

FREE_SWAP_SIZE, TOTAL_SWAP_SIZE = 10733772800L, 10737414144L
SWAP_DEVICE = 'all'


@istest
class TestFsSize(TestSizeFunction):
    def setup(self):
        self.host_os = Mock()
        self.host_os_function = Mock()
        self.host_os_function.return_value = (FREE_SWAP_SIZE, TOTAL_SWAP_SIZE)
        self.host_os.swap_size = self.host_os_function
        self.function_under_test = swap.size
        self.target = SWAP_DEVICE