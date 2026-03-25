import os
import argparse

def extract_solution(file_path):
    solution_nodes = []

    with open(file_path, 'r') as f:
        for idx, line in enumerate(f):
            val = line.strip()
            if val == "1":
                solution_nodes.append(idx)

    return solution_nodes


def main():
    parser = argparse.ArgumentParser(description="Extract MIS solutions from files")
    parser.add_argument("-i", "--input", required=True, help="Input directory with solution files")
    parser.add_argument("-o", "--output", required=True, help="Output summary file")

    args = parser.parse_args()

    input_dir = args.input
    output_file = args.output

    with open(output_file, 'w') as out:

        for fname in sorted(os.listdir(input_dir)):

            fpath = os.path.join(input_dir, fname)

            if not os.path.isfile(fpath):
                continue

            try:
                solution_nodes = extract_solution(fpath)
                cardinality = len(solution_nodes)

                out.write(f"{fname}, {solution_nodes}, {cardinality}\n")

            except Exception as e:
                print(f"Error processing {fname}: {e}")

    print(f"Summary written to {output_file}")


if __name__ == "__main__":
    main()
