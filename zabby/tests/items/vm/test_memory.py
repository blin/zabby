from mock import Mock
from nose.tools import assert_raises
from zabby.core.exceptions import WrongArgumentError

from zabby.items.vm import memory


class TestSize():
    def setup(self):
        self.host_os = Mock()
        self.host_os.AVAILABLE_MEMORY_TYPES = set(['total', 'free', 'pfree'])

    def test_size_raises_exception_if_wrong_mode_is_supplied(self):
        assert_raises(WrongArgumentError, memory.size, 'wrong', self.host_os)

    def test_obtains_information_from_host_os(self):
        self.host_os.memory.assert_called_once()
