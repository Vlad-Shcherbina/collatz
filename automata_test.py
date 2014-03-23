from nose.tools import eq_

from automata import *


#def test_apply():
    #eq_(None, dfa_apply(drop_head_and_reverse, ''))
    #eq_([''], dfa_apply(drop_head_and_reverse, '0'))
    #eq_(['', '1', '0', '0', '1'], dfa_apply(drop_head_and_reverse, '10110'))


def test_collatz_transducer():
    def apply(s):
        result = dfa_apply(collatz_transducer, s)
        if result is None:
            return result
        #print result
        return ''.join(result)

    eq_(apply(''), None)
    eq_(apply('0'), None)
    eq_(apply('1'), None)
    eq_(apply('1$'), None)
    eq_(apply('01$'), None)

    def to_bin(n):
        s = bin(n)
        assert s.startswith('0b')
        return s[2:][::-1] + '$'

    def check(n):
        k = n
        while k % 2 == 0:
            k //= 2
        if k == 1:
            return
        k = 3 * k + 1
        print to_bin(n), '->', to_bin(k)
        eq_(to_bin(k), apply(to_bin(n)))

    for i in range(1, 100):
        check(i)
    #assert False
