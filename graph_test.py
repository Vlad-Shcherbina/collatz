from graph import find_neg_cycle

def test_no_cycles():
    vertices = 'abcd'
    edges = [
        ('a', 'b', -10),
        ('b', 'a', 11),
        ('b', 'c', 4),
        ('c', 'd', 4),
        ('d', 'a', 4),
    ]
    assert find_neg_cycle('a', vertices, edges) is None


def test_loop():
    assert find_neg_cycle('a', 'a', [('a', 'a', -1)]) is not None


def test_simple_cycle():
    assert find_neg_cycle('a', 'ab', [('a', 'b', -2), ('b', 'a', 1)]) is not None
