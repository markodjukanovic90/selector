import os
import json
import argparse

def load_graph(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def convert_to_dimacs(graph):
    # Collect all nodes
    nodes = set()
    for u, neighbors in graph.items():
        u = int(u)
        nodes.add(u)
        for v in neighbors:
            nodes.add(int(v))

    # Map old IDs → 1..N
    nodes = sorted(nodes)
    id_map = {node: i+1 for i, node in enumerate(nodes)}

    # Build edge set (avoid duplicates)
    edges = set()
    for u, neighbors in graph.items():
        u = int(u)
        for v in neighbors:
            v = int(v)
            u_m = id_map[u]
            v_m = id_map[v]
            if u_m != v_m:
                edge = tuple(sorted((u_m, v_m)))
                edges.add(edge)

    return len(nodes), edges

def write_dimacs(output_path, num_nodes, edges):
    with open(output_path, 'w') as f:
        f.write("c Converted from JSON\n")
        f.write(f"p edge {num_nodes} {len(edges)}\n")
        for u, v in edges:
            f.write(f"e {u} {v}\n")

def process_file(input_file, output_file):
    graph = load_graph(input_file)
    n, edges = convert_to_dimacs(graph)
    write_dimacs(output_file, n, edges)

def main():
    parser = argparse.ArgumentParser(description="Convert JSON graphs to DIMACS format for NuMDS")
    parser.add_argument("-i", "--input", required=True, help="Input file or directory (JSON)")
    parser.add_argument("-o", "--output", required=True, help="Output directory")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isfile(args.input):
        # Single file
        out_file = os.path.join(args.output, os.path.basename(args.input).replace(".json", ".dimacs"))
        process_file(args.input, out_file)
        print(f"Converted: {args.input} -> {out_file}")

    else:
        # Directory mode
        for fname in os.listdir(args.input):
            if fname.endswith(".json"):
                in_path = os.path.join(args.input, fname)
                out_path = os.path.join(args.output, fname.replace(".json", ".dimacs"))
                process_file(in_path, out_path)
                print(f"Converted: {in_path} -> {out_path}")

if __name__ == "__main__":
    main()

    #Example of execution: python json_to_dimacs.py -i graph.json -o output_dir (single file) or python json_to_dimacs.py -i ./json_graphs/ -o ./dimacs_instances/
