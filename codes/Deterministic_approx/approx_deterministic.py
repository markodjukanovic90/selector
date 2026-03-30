#!/usr/bin/env python3
import argparse
import json
import time
import networkx as nx
from networkx.algorithms import approximation as approx  # ← import approximation submodule

def load_graph(json_path):
    """Load a graph from a JSON adjacency list."""
    with open(json_path, "r") as f:
        adj = json.load(f)
    G = nx.Graph()
    for u, neighbors in adj.items():
        u = int(u)
        for v in neighbors:
            v = int(v)
            G.add_edge(u, v)
    return G


def greedy_mis(G):
    G_copy = G.copy()
    indep_set = set()

    while G_copy.number_of_nodes() > 0:
        # pick node with smallest degree (better heuristic)
        v = min(G_copy.degree, key=lambda x: x[1])[0]
        indep_set.add(v)

        # remove v and its neighbors
        neighbors = list(G_copy.neighbors(v))
        G_copy.remove_node(v)
        G_copy.remove_nodes_from(neighbors)

    return indep_set


import random

def greedy_mis_random(G):
    G_copy = G.copy()
    indep_set = set()

    while G_copy.number_of_nodes() > 0:
        # pick among k smallest degree nodes
        degrees = sorted(G_copy.degree, key=lambda x: x[1])
        k = min(5, len(degrees))
        v = random.choice(degrees[:k])[0]

        indep_set.add(v)

        neighbors = list(G_copy.neighbors(v))
        G_copy.remove_node(v)
        G_copy.remove_nodes_from(neighbors)

    return indep_set

def solve_mis(G):
    """Solve Maximum Independent Set using NetworkX heuristic."""
    start = time.time()
    # NetworkX greedy MIS
    mis_nodes = greedy_mis(G) #approx.maximum_independent_set(G)  # use approx module #nx.algorithms.approximation.maximum_independent_set(G)
    end = time.time()
    return {
        "nodes": list(mis_nodes),
        "objective": len(mis_nodes),
        "time": end - start
    }

def solve_mds(G):
    """Solve Minimum Dominating Set using NetworkX heuristic."""
    start = time.time()
    mds_nodes =  mds_nodes = approx.min_weighted_dominating_set(G)  # use approx module #nx.algorithms.approximation.min_weighted_dominating_set(G)
    end = time.time()
    return {
        "nodes": list(mds_nodes),
        "objective": len(mds_nodes),
        "time": end - start
    }

def main():
    parser = argparse.ArgumentParser(description="MIS and Minimum Dominating Set solver")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file with graph")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file to save solution")
    parser.add_argument("-a", "--algorithm",   type=int, choices=[0, 1], required=True, help="Algorithm to run: MIS or MDS")
    args = parser.parse_args()

    G = load_graph(args.input)

    if args.algorithm == 0:
        result = solve_mis(G)
    else:
        result = solve_mds(G)

    # Save solution to output JSON
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"{args.algorithm} solved. Objective: {result['objective']}, Time: {result['time']:.4f}s")

if __name__ == "__main__":
    main()
