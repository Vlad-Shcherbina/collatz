import z3
import random

from graph import find_neg_cycle
from automata import *


import logging
log = logging.getLogger(__name__)


def solve_for_all_nonneg_cycles(start, vertices, edges):
    solver = z3.Solver()
    cnt = 0
    while True:
        cnt += 1
        result = solver.check()

        if result == z3.unsat:
            logging.info('{} iterations, unsat'.format(cnt))
            return None
        elif result == z3.sat:
            model = solver.model()
            concrete_edges = {
                (v1, v2, eval_in_model(model, w)): (v1, v2, w)
                for v1, v2, w in edges}

            cycle = find_neg_cycle(start, vertices, concrete_edges.keys())
            if cycle is None:
                logging.info('{} iterations, solved'.format(cnt))
                return model

            cycle_weight = 0
            #print 'counterexample:'
            for e in cycle:
                _, _, w = e = concrete_edges[e]
                #print e
                cycle_weight += w
            #print 'where', model
            #logging.info('found negative cycle')
            assert eval_in_model(model, cycle_weight) < 0
            solver.add(cycle_weight >= 0)
        else:
            assert False, result


def eval_in_model(model, z3t):
    if isinstance(z3t, int):
        return z3t
    result = model.evaluate(z3t, model_completion=True)
    return int(result.as_string())


def make_random_symbolic_automaton(size, alphabet):
    dfa = make_random_dollar_automaton(size, alphabet)
    def var_generator():
        for i in range(100000):
            yield z3.Int('z{}'.format(i))
    gen = iter(var_generator())
    dfa = dfa_weight_map(dfa, lambda c, w: next(gen))
    return dfa
    pass


def main():
    random.seed(45)
    logging.basicConfig(level=logging.INFO)

    #dfa_print(drop_leading_one_and_reverse)

    for i in range(1000):
        #logging.info('trying another random graph')
        dfa = make_random_symbolic_automaton(6, '01')
        #dfa_print(dfa)
        #exit()
        #print dfa_vertices_in_postorder(dfa)
        constr_graph = build_constraint_graph(dfa, collatz_transducer)
        logging.info(
            '{} vertices in constraint graph'.format(len(constr_graph[1])))

        #print 'solving'
        model = solve_for_all_nonneg_cycles(*constr_graph)
        #print 'solution:'
        #print model
        if model is not None:
            dfa_print(dfa_weight_map(dfa, lambda c, w: eval_in_model(model, w)))
            break


    exit()
    x = z3.Int('x')
    y = z3.Int('y')
    z = z3.Int('z')
    edges = [
        ('a', 'b', x),
        ('b', 'c', y),
        ('c', 'a', -y + x),
        ('a', 'a', -x),
    ]
    print solve_for_all_nonneg_cycles('a', 'abcd', edges)


if __name__ == '__main__':
    main()