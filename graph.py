
INF = float('+inf')


def find_neg_cycle(start, vertices, edges):
    """
    Find cycle of negative weight reachable from start.

    start: start vertex
    vertices: list of hashable objects
    edges: list of triples (vertex1, vertex2, weight)

    returns: list of edges forming cycle or None
    """
    #print 'graph:'
    #print start, vertices
    #print edges
    #print '---'

    d = dict.fromkeys(vertices, INF)
    p = dict.fromkeys(vertices)
    d[start] = 0

    for i in range(len(vertices)):
        for e in edges:
            v1, v2, w = e
            if d[v1] + w < d[v2]:
                d[v2] = d[v1] + w
                p[v2] = e
                if i == len(vertices) - 1:
                    v = v2
                    result = []
                    #print p
                    while True:
                        #print result
                        assert len(result) <= len(vertices)
                        v, _, _ = e = p[v]
                        result.append(e)

                        for i in range(len(result)):
                            if result[i][1] == result[-1][0]:
                                result = result[i:]
                                result.reverse()
                                check_neg_cycle(result)
                                return result

                        #if v == v2:
                        #    result.reverse()
                        #    check_neg_cycle(result)
                        #    return result

    return None


def check_neg_cycle(edges):
    w = 0
    for e1, e2 in zip(edges, edges[1:] + edges[:1]):
        assert e1[1] == e2[0]
        w += e1[2]
    assert w < 0
