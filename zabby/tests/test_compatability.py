from zabby.compatability import userparameter_to_key_and_command
from nose.tools import assert_equal


class TestUserparameterToKeyAndCommand():
    def test_separates_key_and_command(self):
        userparam = 'UserParameter=my_echo,echo 1'
        key, command = userparameter_to_key_and_command(userparam)
        assert_equal(key, 'my_echo')
        assert_equal(command, 'echo 1')

    def test_command_with_arguments(self):
        userparam = 'UserParameter=my_echo[*],echo $1'
        key, command = userparameter_to_key_and_command(userparam)
        assert_equal(key, 'my_echo')
        assert_equal(command, 'echo {0}')

    def test_escaped_dollars_are_not_converted(self):
        userparam = "UserParameter=my_echo,echo '$$1'"
        key, command = userparameter_to_key_and_command(userparam)
        assert_equal(command, "echo '$1'")
