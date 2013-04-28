import os

from nose.tools import assert_true

from zabby.core.utils import write_to_file

# assert_is_instance appeared in python 3.2 and was backported to 2.7
try:
    from nose.tools import assert_is_instance
except ImportError:
    def assert_is_instance(obj, cls, msg=None):
        assert_true(isinstance(obj, cls), msg)

# assert_not_in and assert_less appeared in python 3.1 and was backported to 2.7
try:
    from nose.tools import (assert_not_in, assert_less, assert_less_equal,
                            assert_in, assert_greater)
except ImportError:
    def assert_not_in(member, collection, msg=None):
        assert_true(member not in collection, msg)

    def assert_less(a, b, msg=None):
        assert_true(a < b, msg)

    def assert_less_equal(a, b, msg=None):
        assert_true(a <= b, msg)

    def assert_in(member, collection, msg=None):
        assert_true(member in collection, msg)

    def assert_greater(a, b, msg=None):
        assert_true(a > b, msg)


def ensure_removed(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def ensure_contains_only_formatted_lines(file_path, line_format, n=1):
    ensure_removed(file_path)
    for i in range(n):
        write_to_file(file_path, line_format.format(i))
