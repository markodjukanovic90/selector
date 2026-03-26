import os
import argparse
import random
import numpy as np
from sklearn.metrics import pairwise_distances
import pandas as pd

############################################################
# Load CSV dataset
############################################################
def load_csv_dataset(path):
    df = pd.read_csv(path)

    # If column named 'f' exists → drop it
    if 'f' in df.columns:
        df = df.drop(columns=['f'])

    # Otherwise: drop first column if non-numeric
    elif not np.issubdtype(df.iloc[:, 0].dtype, np.number):
        df = df.iloc[:, 1:]

    # Ensure all remaining data is numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    # Drop rows with NaN
    df = df.dropna()

    return df.values


############################################################
# Sample random pairs
############################################################
def sample_pairs(n, num_samples):
    pairs = set()

    while len(pairs) < num_samples:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)

        if i != j:
            pairs.add((i, j))

    return list(pairs)


############################################################
# Compute distances (FAST version)
############################################################
def compute_distances_fast(X, pairs, metric):
    idx_i = [i for i, j in pairs]
    idx_j = [j for i, j in pairs]

    Xi = X[idx_i]
    Xj = X[idx_j]

    if metric == "seuclidean":
        V = np.var(X, axis=0, ddof=1)
        V[V == 0] = 1e-9
        dists = pairwise_distances(Xi, Xj, metric=metric, V=V)
    else:
        dists = pairwise_distances(Xi, Xj, metric=metric)

    return dists.diagonal()


############################################################
# Compute statistics
############################################################
def compute_stats(dists):
    return {
        "min": float(np.min(dists)),
        "p10": float(np.percentile(dists, 10)),
        "p20": float(np.percentile(dists, 20)),
        "p50": float(np.percentile(dists, 50)),
        "p80": float(np.percentile(dists, 80)),
        "p90": float(np.percentile(dists, 90)),
        "p95": float(np.percentile(dists, 95)),
        "max": float(np.max(dists)),
    }


############################################################
# Main
############################################################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", required=True)
    parser.add_argument("-o", "--output_file", required=True)
    parser.add_argument("-s", "--samples", type=int, default=50000)

    args = parser.parse_args()

    metrics = [
        "cosine",
         #"euclidean",
        "seuclidean",
        "correlation"
    ]

    results = []

    ########################################################
    # Loop over datasets
    ########################################################
    for fname in os.listdir(args.input_dir):

        if not fname.endswith(".csv"):
            continue

        path = os.path.join(args.input_dir, fname)
        print(f"\nProcessing dataset: {fname}")

        X = load_csv_dataset(path)

        if len(X) == 0:
            print("  Skipping (empty dataset)")
            continue

        print(f"  Shape: {X.shape}")

        n = len(X)
        pairs = sample_pairs(n, min(args.samples, n * (n - 1)))

        ####################################################
        # Compute stats for each metric
        ####################################################
        for metric in metrics:
            print(f"  Metric: {metric}")

            try:
                dists = compute_distances_fast(X, pairs, metric)
                stats = compute_stats(dists)

                row = {
                    "dataset": fname,
                    "metric": metric,
                    **stats
                }

                results.append(row)

                ################################################
                # OLD PLOTTING CODE (DISABLED)
                ################################################
                # import matplotlib.pyplot as plt
                # plt.figure()
                # plt.hist(dists, bins=50)
                # plt.title(f"{fname} - {metric}")
                # plt.savefig(...)
                # plt.close()

            except Exception as e:
                print(f" ERROR with {metric}: {e}")

    ########################################################
    # Save results
    ########################################################
    df = pd.DataFrame(results)
    df.to_csv(args.output_file, index=False)

    print(f"\nSaved results to: {args.output_file}")


############################################################
if __name__ == "__main__":
    main()
