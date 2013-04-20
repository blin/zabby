import sys
PY3 = sys.version_info[0] == 3

if PY3:
    def b(s):
        return s.encode('utf-8')

    def u(s):
        return s

    string_types = str,
    integer_types = int,
else:
    def b(s):
        return s

    def u(s):
        return s.decode('utf-8')

    string_types = basestring,
    integer_types = (int, long)


def write_to_file(file_path, value):
    """ Converts value to string and writes it to file followed by newline"""
    with open(file_path, mode='a') as f:
        f.write(str(value))
        f.write("\n")
        f.flush()
