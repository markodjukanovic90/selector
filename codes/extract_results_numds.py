import os
import argparse

def extract_from_file(filepath):
    results = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 3:
                continue

            graph_path = parts[0]
            solution = parts[-1]

            # Extract filename without path and extension
            base = os.path.basename(graph_path)
            name = os.path.splitext(base)[0]

            results.append((name, solution))

    return results


def main():
    parser = argparse.ArgumentParser(description="Extract solutions from result files")
    parser.add_argument("-i", "--input", required=True, help="Input directory with result files")

    args = parser.parse_args()

    for fname in os.listdir(args.input):
        fpath = os.path.join(args.input, fname)

        if not os.path.isfile(fpath):
            continue

        results = extract_from_file(fpath)

        for name, sol in results:
            print(f"{name} {sol}")


if __name__ == "__main__":
    main()
