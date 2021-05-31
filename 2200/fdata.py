
# This is a Fieldata to printable ASCII converter. It's just a string of ASCII
# characters in Fieldata order. Index it with the 6-bit Fieldata
# character code.

fd = '@[]#. ' + \
     'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
     ')-+<=>&$*(%:?!,\\' + \
     '0123456789' + \
     "';/..."


if __name__ == '__main__':
    assert '@' == fd[0]
    assert '#' == fd[3]
    assert 'A' == fd[6]
    assert 'E' == fd[0o12]
    assert 'M' == fd[0o22]
    assert 'T' == fd[0o31]
    assert '+' == fd[0o42]
    assert '$' == fd[0o47]
    assert '\\' == fd[0o57]
    assert '0' == fd[0o60]
    assert '9' == fd[0o71]
    assert '.' == fd[0o75]
    assert '.' == fd[0o77]
