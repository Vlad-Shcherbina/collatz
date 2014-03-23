from collections import namedtuple
import operator
import random


WeightedDFA = namedtuple('WeightedDFA', 'enter exits t')

Accumulator = namedtuple('Accumulator', 'default compose')

# t[v][input_char] = (next_v, weight)


def dfa_vertices_in_postorder(dfa):
    postorder = []
    visited = set()
    def visit(v):
        if v in visited:
            return
        visited.add(v)
        for _, (v2, _) in reversed(dfa.t[v].items()):
            visit(v2)
        postorder.append(v)
    visit(dfa.enter)
    return postorder


def dfa_edges(dfa):
    for v in dfa_vertices_in_postorder(dfa):
        for _, (v2, w) in dfa.t[v].items():
            yield (v, v2, w)


def dfa_print(dfa):
    for v in reversed(dfa_vertices_in_postorder(dfa)):
        if v in dfa.exits:
            print v, '(exit)'
        else:
            print v
        for c, (v2, w) in sorted(dfa.t[v].items()):
            print '  - {} ->  {}, {}'.format(c, v2, w)


def dfa_apply(dfa, inputs):
    result = []
    s = dfa.enter
    for c in inputs:
        q = dfa.t[s].get(c)
        if q is None:
            return None
        s, w = q
        result.append(w)
    if s in dfa.exits:
        return result
    else:
        return None


def dfa_weight_map(wdfa, map_fn):
    t1 = {
        v: {c: (next_v, map_fn(c, w)) for c, (next_v, w) in fan.items()}
        for v, fan in wdfa.t.items()}
    return WeightedDFA(wdfa.enter, wdfa.exits, t1)


def dfa_compose(wdfa1, wdfa2):
    """
    It is expected that weights of the first wdfa are of the form
      (accumulator, sequence_of_second_automaton_inputs)
    """
    exits = set()
    t = {}
    def visit(s1, s2):
        if (s1, s2) in t:
            return
        t[s1, s2] = {}
        if s1 in wdfa1.exits and s2 in wdfa2.exits:
            exits.add((s1, s2))
        for c, (new_s1, (accum, inputs)) in wdfa1.t[s1].items():
            w = accum.default
            new_s2 = s2
            for c2 in inputs:
                q = wdfa2.t[new_s2].get(c2)
                if q is None:
                    break
                new_s2, w2 = q
                w = accum.compose(w, w2)
            else:
                t[s1, s2][c] = (new_s1, new_s2), w
                visit(new_s1, new_s2)

    visit(wdfa1.enter, wdfa2.enter)
    return WeightedDFA((wdfa1.enter, wdfa2.enter), exits, t)


drop_leading_one_and_reverse = WeightedDFA('a', 'b', {
    'a': {'0': ('b', '1'), '1': ('b', '')},
    'b': {'0': ('b', '1'), '1': ('b', '0')},
})


# odd: 3*x + 1, even: x/2
collatz_transducer = WeightedDFA('enter', ['exit'], {
    'enter': {'0': ('enter', ''), '1': ('one', '0')},
    'c0': {'0': ('c0', '0'), '1': ('c1', '1'), '$': ('exit', '$')},
    'c1': {'0': ('c0', '1'), '1': ('c2', '0'), '$': ('exit', '1$')},
    'c2': {'0': ('c1', '0'), '1': ('c2', '1'), '$': ('exit', '01$')},
    'one': {'0': ('c1', '0'), '1': ('c2', '1')},
    'exit': {},
})


# odd: x + 1, even: x/2
pseudo_collatz_transducer = WeightedDFA('enter', ['exit'], {
    'enter': {'0': ('enter', ''), '1': ('one', '0')},
    'c0': {'0': ('c0', '0'), '1': ('c0', '1'), '$': ('exit', '$')},
    'c1': {'0': ('c0', '1'), '1': ('c1', '0'), '$': ('exit', '1$')},
    'one': {'0': ('c0', '1'), '1': ('c1', '0')},
    'exit': {},
})


def hz(wdfa, tr):
    tr2 = dfa_weight_map(tr, lambda c, w: (Accumulator(0, operator.add), w))
    q = dfa_compose(tr2, dfa_weight_map(wdfa, lambda _, w: -w))
    #print
    #dfa_print(q)
    #print
    d = dfa_weight_map(wdfa, lambda c, w: (Accumulator(w, operator.add), [c]))
    return dfa_compose(d, q)


def build_constraint_graph(wdfa, tr):
    def _flatten(x):
        return repr(x).replace('(', '').replace(')', '').replace(', ', '').replace("''", '-')
    def pos_vertex(v):
        return _flatten(('pos', v))
    def dec_vertex(v):
        return _flatten(('dec', v))
    start = 'start'
    q = hz(wdfa, tr)
    #print 'dec automaton:'
    #dfa_print(q)
    #print '---'
    vertices = (
        [start] +
        map(pos_vertex, dfa_vertices_in_postorder(wdfa)) +
        map(dec_vertex, dfa_vertices_in_postorder(q)))
    edges = []
    edges.append((start, pos_vertex(wdfa.enter), 0))
    edges.append((start, dec_vertex(q.enter), 0))
    for v1, v2, w in dfa_edges(wdfa):
        edges.append((pos_vertex(v1), pos_vertex(v2), w))
    for v1, v2, w in dfa_edges(q):
        edges.append((dec_vertex(v1), dec_vertex(v2), w))
    for exit in wdfa.exits:
        edges.append((pos_vertex(exit), start, 1000))
    for exit in q.exits:
        edges.append((dec_vertex(exit), start, -1))

    return start, vertices, edges
    #for edges in edges: pass


def make_random_automaton(size, alphabet):
    while True:
        vertices = ['s{}'.format(i) for i in range(size)]
        t = {}
        for v in vertices:
            t[v] = {a: (random.choice(vertices), None) for a in alphabet}
        dfa = WeightedDFA(vertices[0], vertices, t)
        if len(dfa_vertices_in_postorder(dfa)) < size:
            continue
        return dfa

def make_random_dollar_automaton(size, alphabet):
    while True:
        vertices = ['s{}'.format(i) for i in range(size-1)] + ['exit']
        t = {}
        for v in vertices[:-1]:
            t[v] = {a: (random.choice(vertices[:-1]), None) for a in alphabet}
            t[v]['$'] = ('exit', None)
        t['exit'] = {}
        dfa = WeightedDFA(vertices[0], ['exit'], t)
        if len(dfa_vertices_in_postorder(dfa)) < size:
            continue
        return dfa


if __name__ == '__main__':
    x = z3.Int('x')
    y = z3.Int('y')

    dfa_print(drop_head_and_reverse)
    print '---'
    dfa = WeightedDFA('a', 'ab', {
        'a': {'0': ('a', x), '1': ('a', y)},
        #'b': {'0': ('a', 100), '1': ('a', 150)},
        #'c': {0: ('c', 50)},
    })
    dfa_print(dfa)
    print '----'
    dfa_print(hz(dfa, drop_head_and_reverse))
    print '---'
    from pprint import pprint
    pprint(build_constraint_graph(dfa, drop_head_and_reverse))
    exit()

    transducer = WeightedDFA('a', 'ab', {
        'a': {0: ('b', [0, 0]), 1: ('b', [1, 1])},
        'b': {0: ('b', [1, 1]), 1: ('b', [0, 0])},
    })

    dfa = WeightedDFA('a', 'c', {
        'a': {0: ('b', 10), 1: ('c', 20)},
        'b': {1: ('b', 30), 0: ('c', 40)},
        'c': {0: ('c', 50)},
    })
    #dfa_print(dfa)
    print dfa_apply(dfa, [0, 1])
    #exit()
    print '---'
    t2 = dfa_weight_map(transducer, lambda c, w: (Accumulator(0, operator.add), w))
    dfa_print(t2)
    print '---'
    dfa_print(dfa_compose(t2, dfa))
    print '----'
    dfa_compose(dfa, )