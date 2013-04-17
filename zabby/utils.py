import six

if six.PY3:
    def b(s):
        return s.encode('utf-8')

    def u(s):
        return s
else:
    def b(s):
        return s

    def u(s):
        return s.decode('utf-8')