
"""
Functions to manipulate 2200 words in various ways.
I haven't thought about how to do the ones that sign extend yet.
"""


import util


# Half words

def h1(n: int) -> int:
    return (n >> 18) & 0o777777


def h2(n: int) -> int:
    return n & 0o777777


# Quarter words
def q1(n: int) -> int:
    return (n >> 27) & 0o777


def q2(n: int) -> int:
    return (n >> 18) & 0o777


def q3(n: int) -> int:
    return (n >> 9) & 0o777


def q4(n: int) -> int:
    return n & 0o777


# Sixth words

def s1(n: int) -> int:
    return (n >> 30) & 0o77


def s2(n: int) -> int:
    return (n >> 24) & 0o77


def s3(n: int) -> int:
    return (n >> 18) & 0o77


def s4(n: int) -> int:
    return (n >> 12) & 0o77


def s5(n: int) -> int:
    return (n >> 6) & 0o77


def s6(n: int) -> int:
    return n & 0o77


# ----------


def w2ascii(n: int) -> str:
    "Convert 36-bit word to 4 ASCII characters."
    c1 = util.toprint(q1(n))
    c2 = util.toprint(q2(n))
    c3 = util.toprint(q3(n))
    c4 = util.toprint(q4(n))
    return c1 + c2 + c3 + c4


if __name__ == '__main__':
    n = 0o001000002000
    assert h1(n) == 0o001000
    assert h2(n) == 0o002000

    n = 0o001002003004
    # print(f'{q1(n) = }')
    # print(f'{q2(n) = }')
    # print(f'{q3(n) = }')
    # print(f'{q4(n) = }')
    assert q1(n) == 1
    assert q2(n) == 2
    assert q3(n) == 3
    assert q4(n) == 4

    n = 0o010203040506
    assert s1(n) == 1
    assert s2(n) == 2
    assert s3(n) == 3
    assert s4(n) == 4
    assert s5(n) == 5
    assert s6(n) == 6

    n = 0o126117114061
    assert w2ascii(n) == 'VOL1'
    n = 0o060061000000
    assert w2ascii(n) == '01..'
