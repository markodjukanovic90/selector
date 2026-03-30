import os
import json
import argparse


def load_graph(json_path):
    """
    Load JSON graph and convert keys/values to integers.
    Expected format:
    {
        "1": [2,3,4],
        "2": [1,5],
        ...
    }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    # Convert to int (faster later, avoids repeated casting)
    graph = {int(u): [int(v) for v in nbrs] for u, nbrs in data.items()}
    return graph


def build_node_mapping(graph):
    """
    Create mapping from original node IDs to 1..N (METIS format).
    """
    nodes = set()
    for u, nbrs in graph.items():
        nodes.add(u)
        for v in nbrs:
            nodes.add(v)

    nodes = sorted(nodes)
    node_to_idx = {node: i + 1 for i, node in enumerate(nodes)}
    return node_to_idx, len(nodes)


def convert_to_metis(graph, output_path):
    """
    Convert graph (dict) to METIS format in a memory-efficient way.
    """
    node_to_idx, n = build_node_mapping(graph)

    # Use lists instead of sets → much lower RAM
    adj = [[] for _ in range(n + 1)]  # 1-based indexing

    edge_count = 0

    # Build adjacency (undirected, no duplicates)
    for u, nbrs in graph.items():
        u_m = node_to_idx[u]
        for v in nbrs:
            v_m = node_to_idx[v]

            # Only process one direction → avoids duplicates
            if u_m < v_m:
                adj[u_m].append(v_m)
                adj[v_m].append(u_m)
                edge_count += 1

    # Write METIS file
    with open(output_path, "w") as out:
        out.write(f"{n} {edge_count}\n")

        for u in range(1, n + 1):
            if adj[u]:
                # Sort only at write time (better performance)
                line = " ".join(map(str, sorted(adj[u])))
                out.write(line + "\n")
            else:
                out.write("\n")


def process_file(input_file, output_file):
    graph = load_graph(input_file)
    convert_to_metis(graph, output_file)


def convert_json_to_metis(input_dir, output_dir):
    """
    Process all JSON files in a directory.
    """
    print(f"Processing directory: {input_dir}")
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if not fname.endswith(".json"):
            continue

        in_path = os.path.join(input_dir, fname)
        out_name = fname.replace(".json", ".graph")
        out_path = os.path.join(output_dir, out_name)

        try:
            process_file(in_path, out_path)
            print(f"Converted: {fname} → {out_name}")
        except Exception as e:
            print(f"Skipping {fname}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON graphs to METIS format (memory-efficient)"
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

    if os.path.isfile(args.input):
        # Single file mode
        os.makedirs(args.output, exist_ok=True)
        out_file = os.path.join(
            args.output,
            os.path.basename(args.input).replace(".json", ".graph")
        )
        process_file(args.input, out_file)
        print(f"Converted: {args.input} → {out_file}")

    else:
        # Directory mode
        convert_json_to_metis(args.input, args.output)


if __name__ == "__main__":
    main()
