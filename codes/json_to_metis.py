import os
import json
import argparse

def convert_json_to_metis(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if not fname.endswith(".json"):
            continue

        in_path = os.path.join(input_dir, fname)
        out_name = fname.replace(".json", ".graph")
        out_path = os.path.join(output_dir, out_name)

        try:
            with open(in_path, "r") as f:
                graph = json.load(f)

            # Convert keys to integers
            nodes = sorted(int(k) for k in graph.keys())
            node_to_idx = {node: i+1 for i, node in enumerate(nodes)}  # METIS uses 1-based

            # Build adjacency list (ensure undirected & no duplicates)
            adj = {node: set() for node in nodes}

            for u_str, neighbors in graph.items():
                u = int(u_str)
                for v in neighbors:
                    v = int(v)
                    if u != v:
                        adj[u].add(v)
                        adj[v].add(u)  # enforce undirected

            # Count edges (each edge once)
            edge_count = sum(len(adj[u]) for u in nodes) // 2

            # Write METIS file
            with open(out_path, "w") as out:
                out.write(f"{len(nodes)} {edge_count}\n")

                for u in nodes:
                    line = " ".join(str(node_to_idx[v]) for v in sorted(adj[u]))
                    out.write(line + "\n")

            print(f"Converted: {fname} → {out_name}")

        except Exception as e:
            print(f"Skipping {fname}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert JSON graphs to METIS format")
    parser.add_argument("-i", "--input", required=True, help="Input directory (JSON graphs)")
    parser.add_argument("-o", "--output", required=True, help="Output directory (METIS files)")

    args = parser.parse_args()

    convert_json_to_metis(args.input, args.output)


if __name__ == "__main__":
    main()
