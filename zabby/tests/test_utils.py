from nose.tools import assert_raises, assert_equal

from zabby.tests import (assert_is_instance, ensure_removed,
                         ensure_contains_only_formatted_lines,
                         assert_less_equal, assert_less)
from zabby.core import utils
from zabby.core.exceptions import WrongArgumentError, OperatingSystemError
from zabby.core.six import integer_types, string_types
from zabby.core.utils import (SIZE_CONVERSION_MODES, validate_mode,
                              convert_size, lines_from_file, lists_from_file, dict_from_file, to_bytes)


def test_validate_mode_raises_exception_if_mode_is_not_available():
    assert_raises(WrongArgumentError, utils.validate_mode, 'mode', [])


def test_validate_mode_does_not_raise_exception_if_mode_is_available():
    validate_mode('mode', ['mode'])


def test_convert_size_returns_integers_or_floats():
    free, total = 50, 100
    for conversion_mode in SIZE_CONVERSION_MODES:
        converted_size = convert_size(free, total, conversion_mode)
        assert_is_instance(converted_size, (float, integer_types))


def test_convert_size_returns_zero_if_total_size_is_zero():
    assert_equal(0, convert_size(1, 0, SIZE_CONVERSION_MODES[0]))


FILE_PATH = '/tmp/zabby_test_file'


class TestLinesFromFile():
    def test_raises_exception_if_file_is_not_found(self):
        ensure_removed(FILE_PATH)
        assert_raises(IOError, lines_from_file, FILE_PATH)

    def test_raises_exception_if_file_is_empty(self):
        ensure_removed(FILE_PATH)
        open(FILE_PATH, mode='w').close()
        assert_raises(OperatingSystemError, lines_from_file, FILE_PATH)

    def test_returns_list_of_strings(self):
        ensure_contains_only_formatted_lines(FILE_PATH, 'line')

        found_lines = lines_from_file(FILE_PATH)
        assert_is_instance(found_lines, list)
        for found_line in found_lines:
            assert_is_instance(found_line, string_types)

    def test_returns_up_to_maximum_number_of_lines(self):
        ensure_contains_only_formatted_lines(FILE_PATH, 'line', 3)

        maximum_number_of_lines = 2
        found_lines = lines_from_file(FILE_PATH, maximum_number_of_lines)

        assert_less_equal(maximum_number_of_lines, len(found_lines))


class TestListsFromFile():
    def test_returns_list_of_lists(self):
        ensure_contains_only_formatted_lines(FILE_PATH, '1 2')

        found_lists = lists_from_file(FILE_PATH)

        assert_is_instance(found_lists, list)

        for found_list in found_lists:
            assert_is_instance(found_list, list)


class TestDictFromFile():
    def test_returns_dict(self):
        ensure_contains_only_formatted_lines(FILE_PATH, 'key value')

        d = dict_from_file(FILE_PATH)

        assert_is_instance(d, dict)

        assert_less(0, len(d))

    def test_lines_without_value_are_not_included(self):
        ensure_contains_only_formatted_lines(FILE_PATH, 'key')

        d = dict_from_file(FILE_PATH)

        assert_equal(0, len(d))


class TestToBytes():
    def test_raises_exception_if_wrong_factor_is_passed(self):
        assert_raises(WrongArgumentError, to_bytes, 1, 'wrong')

    def test_raises_exception_if_value_is_not_convertible_to_int(self):
        assert_raises(ValueError, to_bytes, 'wrong', 'kB')

    def test_returns_integer(self):
        value = to_bytes(1, 'kB')
        assert_is_instance(value, integer_types)
