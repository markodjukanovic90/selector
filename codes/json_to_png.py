import os
import json
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from random import shuffle 
import random


SUBGRAPH_SIZE=500 # the isze of subgraph to be visualized 

def load_graph(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data


def build_graph(data):
    G = nx.Graph()

    for u, neighbors in data.items():
        u = int(u)
        G.add_node(u)

        for v in neighbors:
            v = int(v)
            if u != v:
                G.add_edge(u, v)

    return G


def draw_graph(G, output_path):
    plt.figure(figsize=(8, 8))

    # Layout (can change if needed)
    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G, pos,
        node_size=50,
        with_labels=False,
        width=0.5
    )

    plt.savefig(output_path, dpi=300)
    plt.close()


from networkx.drawing.nx_agraph import to_agraph

def draw_graph_fast(G, output_path):
    A = to_agraph(G)
    A.layout(prog="sfdp")  # key for large graphs
    A.draw(output_path)

def process_file(input_file, output_dir):
    data = load_graph(input_file)
    G = build_graph(data)
    
    #draw only subgraph with 1000 nodes 
    random_nodes = random.sample(list(G.nodes()),  SUBGRAPH_SIZE)
    G = G.subgraph( random_nodes )
    
    base = os.path.basename(input_file)
    name = os.path.splitext(base)[0]
    output_path = os.path.join(output_dir, f"{name}.png")

    draw_graph_fast(G, output_path)
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Draw graphs from JSON and save as PNG")
    parser.add_argument("-i", "--input", required=True, help="Input file or directory (JSON)")
    parser.add_argument("-o", "--output", default="png_output", help="Output directory")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isfile(args.input):
        process_file(args.input, args.output)
    else:
        for fname in os.listdir(args.input):
            if fname.endswith(".json"):
                in_path = os.path.join(args.input, fname)
                process_file(in_path, args.output)


if __name__ == "__main__":
    main()
