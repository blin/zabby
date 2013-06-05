import os
from nose.plugins.attrib import attr
from nose.tools import assert_equal
from zabby.core.utils import sh

from zabby.items.vfs import file


@attr(os='linux')
class TestMd5Sum():
    FILE_PATH = '/tmp/zabby_md5_test_file'
    FILE_CONTENT = '''\
    line 1
    '''

    def setup(self):
        with open(self.FILE_PATH, 'w') as f:
            f.write(self.FILE_CONTENT)

    def teardown(self):
        os.remove(self.FILE_PATH)

    def test_result_is_equal_to_coreutils_md5sum(self):
        coreutils_md5sum = sh('md5sum {0}')(self.FILE_PATH).split()[0]
        zabby_md5sum = file.md5sum(self.FILE_PATH)
        assert_equal(coreutils_md5sum, zabby_md5sum)
