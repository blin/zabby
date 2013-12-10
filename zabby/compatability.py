import re


def userparameter_to_key_and_command(line):
    """
    Converts UserParameter line[1] to key and command that is accepted by
    zabby.core.utils.sh

    [1] https://www.zabbix.com/documentation/2.0/manual/config/items/userparameters
    """
    def format_index(m):
        zero_based_index = str(int(m.group(1)) - 1)
        return '{' + zero_based_index + '}'

    comma_position = line.find(',')
    key = line[line.find('=') + 1:comma_position]
    command = line[comma_position + 1:].strip()

    # python formatted strings should escape { and }
    command = command.replace('{', '{{').replace('}', '}}')

    has_arguments = key.endswith('[*]')
    if has_arguments:
        key = key[0:-3]
        command = re.sub('(?<!\$)\$(\d)', format_index, command)

    # $ is not a special symbol in python strings, remove escape
    command = command.replace('$$', '$')

    return key, command
