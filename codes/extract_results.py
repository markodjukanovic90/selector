import os
import json
import argparse

def extract_results(input_dir, output_file):
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    with open(output_file, "w") as out:
        for fname in sorted(files):
            fpath = os.path.join(input_dir, fname)

            try:
                with open(fpath, "r") as f:
                    data = json.load(f)

                nodes = data.get("nodes", "NA")
                edges = data.get("edges", "NA")
                objective = data.get("objective", "NA")
                lb = data.get("LB", "NA")

                line = f"{fname}, {nodes}, {edges}, {objective}, {lb}\n"
                out.write(line)

            except Exception as e:
                print(f"Skipping {fname}: {e}")

    print(f"Extraction completed → {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Extract MIS/MDS results from JSON files")
    parser.add_argument("-i", "--input", required=True, help="Input directory with JSON files")
    parser.add_argument("-o", "--output", required=True, help="Output file")

    args = parser.parse_args()

    extract_results(args.input, args.output)


if __name__ == "__main__":
    main()
