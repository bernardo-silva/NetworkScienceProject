import networkx as nx
import networkx.algorithms.community as nx_comm

from utilities import import_networks
from networkx.algorithms.community.centrality import girvan_newman

import matplotlib.pyplot as plt
import numpy as np

from multiprocessing import Pool
import itertools
import time

import json


networks = import_networks()
print("\n".join([str(x) for x in networks]))

for g in networks:
    g.remove_edges_from([v for v in g.edges(data=True) if v[2]["weight"] < 10])

for g in networks:
    g.remove_nodes_from(list(nx.isolates(g)))
print("\n".join([str(x) for x in networks]))

def chunks(l, n):
    """Divide a list of nodes `l` in `n` chunks"""
    l_c = iter(l)
    while 1:
        x = tuple(itertools.islice(l_c, n))
        if not x:
            return
        yield x

def betweenness_centrality_parallel(G, processes=None):
    """Parallel betweenness centrality  function"""
    p = Pool(processes=processes)
    node_divisor = len(p._pool) * 4
    node_chunks = list(chunks(G.nodes(), int(G.order() / node_divisor)))
    num_chunks = len(node_chunks)
    bt_sc = p.starmap(
        nx.edge_betweenness_centrality_subset,
        zip(
            [G] * num_chunks,
            node_chunks,
            [list(G)] * num_chunks,
            [True] * num_chunks,
            ["weight"] * num_chunks,
        ),
    )

    # Reduce the partial solutions
    bt_c = bt_sc[0]
    for bt in bt_sc[1:]:
        for n in bt:
            bt_c[n] += bt[n]
    return bt_c


def most_valuable_parallel(G):
    centrality = betweenness_centrality_parallel(G)
    return max(centrality,key=centrality.get)


k = 4
gn_iterator = [girvan_newman(g,most_valuable_parallel) for g in networks]
limited = [itertools.takewhile(lambda c: max([len(x) for x in c]) >= 300, comp) for comp in gn_iterator]

gn_comms = []
start = time.time()

for l,year in zip(limited,range(2018,2022)):
    for communities in l:
        # gn_comms = [tuple(c for c in comm) for comm in communities]
        com = tuple(list(c) for c in communities)
        gn_comms.append(com)
        with open(f"data/GNCommunities_{year}.json","w") as f:
            json.dump(gn_comms,f)
    
        print(f"Found {len(com)} communities( {[len(x) for x in com]}) in {time.time()-start}s")

        start = time.time()

