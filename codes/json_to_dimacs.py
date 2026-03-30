import os
import json
import argparse


def load_graph(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Convert keys/values to int (faster later)
    graph = {int(u): [int(v) for v in neighbors] for u, neighbors in data.items()}
    return graph


def convert_to_dimacs_write(graph, output_path):
    # ---- Collect nodes ----
    nodes = set()
    for u, neighbors in graph.items():
        nodes.add(u)
        for v in neighbors:
            nodes.add(v)

    # Map to 1..N
    nodes = sorted(nodes)
    id_map = {node: i + 1 for i, node in enumerate(nodes)}

    # ---- Count edges (no storage!) ----  
    edge_count = 0
    for u, neighbors in graph.items():
        u_m = id_map[u]
        for v in neighbors:
            v_m = id_map[v]
            if u_m < v_m:   # avoids duplicates
                edge_count += 1

    # ---- Write DIMACS ----
    with open(output_path, 'w') as f:
        f.write("c Converted from JSON\n")
        f.write(f"p edge {len(nodes)} {edge_count}\n")

        for u, neighbors in graph.items():
            u_m = id_map[u]
            for v in neighbors:
                v_m = id_map[v]
                if u_m < v_m:   # write each edge once
                    f.write(f"e {u_m} {v_m}\n")


def process_file(input_file, output_file):
    graph = load_graph(input_file)
    convert_to_dimacs_write(graph, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON graphs to DIMACS format (memory-efficient)"
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Input file or directory (JSON)"
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Output directory"
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isfile(args.input):
        # Single file
        out_file = os.path.join(
            args.output,
            os.path.basename(args.input).replace(".json", ".dimacs")
        )
        process_file(args.input, out_file)
        print(f"Converted: {args.input} -> {out_file}")

    else:
        # Directory mode
        for fname in os.listdir(args.input):
            if fname.endswith(".json"):
                in_path = os.path.join(args.input, fname)
                out_path = os.path.join(
                    args.output,
                    fname.replace(".json", ".dimacs")
                )
                process_file(in_path, out_path)
                print(f"Converted: {in_path} -> {out_path}")


if __name__ == "__main__":
    main()
