import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from scipy.spatial.distance import pdist, squareform
import json
import os

# =========================
# 1. Load data
# =========================
def load_data(file_path):
    df = pd.read_csv(file_path)
    
    labels = df.iloc[:, 0].astype(str).tolist()
    X = df.iloc[:, 1:].values.astype(float)
    
    return labels, X

# =========================
# 2. Scaling
# =========================
def scale_data(X):
    scaler = RobustScaler()
    return scaler.fit_transform(X)

# =========================
# 3. Distance functions
# =========================
def cosine_distance_matrix(X):
    return squareform(pdist(X, metric='cosine'))

def correlation_distance_matrix(X):
    return squareform(pdist(X, metric='correlation'))

def standardized_euclidean_distance_matrix(X):
    return squareform(pdist(X, metric='seuclidean'))

def mahalanobis_distance_matrix(X):
    cov = np.cov(X, rowvar=False)
    VI = np.linalg.pinv(cov)
    return squareform(pdist(X, metric='mahalanobis', VI=VI))

# =========================
# 4. Load percentile thresholds
# =========================
def load_percentiles(stats_file):


    df = pd.read_csv(stats_file)
    percentiles = {}
    
    for _, row in df.iterrows():
        rep = str(row["dataset"]).strip().replace(".csv", "")
        metric = str(row["metric"]).strip()
        
        key = (rep, metric)
        
        percentiles[key] = [
            float(row["p10"]),
            float(row["p20"]),
            float(row["p50"]),
            float(row["p80"]),
            float(row["p90"]),
            float(row["p95"])
        ]
    
    return percentiles
    

# =========================
# 5. GLOBAL reverse mapping
# =========================
def build_global_reverse_mapping(file_paths):
    all_labels = set()
    
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        labels = df.iloc[:, 0].astype(str).tolist()
        all_labels.update(labels)
    
    all_labels = sorted(all_labels)
    reverse = {label: i for i, label in enumerate(all_labels)}
    
    return reverse

def save_reverse_mapping(reverse):
    os.makedirs("graphs", exist_ok=True)
    
    with open("global_reverse_mapping.json", "w") as f:
        json.dump(reverse, f, indent=4)
    
    print("Saved: global_reverse_mapping.json")

# =========================
# 6. Graph construction
# =========================
def build_graph(labels, D, eps, reverse):
    graph = {}
    
    node_ids = [reverse[label] for label in labels]
    
    for nid in node_ids:
        graph[nid] = []
    
    n = len(labels)
    
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] >= eps:  ## eps 
                u = reverse[labels[i]]
                v = reverse[labels[j]]
                
                graph[u].append(v)
                graph[v].append(u)
    
    return graph

# =========================
# 7. Save graph
# =========================
def save_graph(graph, filename):
    with open(filename, 'w') as f:
        json.dump(graph, f, indent=4)

# =========================
# 8. Main graph generation
# =========================
def generate_graphs(file_path, representation_name, percentiles_map, reverse):
    
    labels, X = load_data(file_path)
    X_scaled = X  # or use scale_data(X)

    distances = {
        "cosine": cosine_distance_matrix(X_scaled),
        "correlation": correlation_distance_matrix(X_scaled),
        "seuclidean": standardized_euclidean_distance_matrix(X_scaled),
        #"mahalanobis": mahalanobis_distance_matrix(X_scaled)
    }

    os.makedirs("graphs", exist_ok=True)

    for dist_name, D in distances.items():
        
        key = (representation_name, dist_name)
        
        if key not in percentiles_map:
            print(f"Skipping {key} (no percentile data)")
            continue
        
        eps_values = percentiles_map[key]
        percentile_labels = ["p10", "p20", "p50", "p80", "p90", "p95"]
        
        for label_name, eps in zip(percentile_labels, eps_values):
            
            graph = build_graph(labels, D, eps, reverse)
            
            filename = f"graphs/{representation_name}_{dist_name}_{label_name}.json"
            save_graph(graph, filename)
            
            print(f"Saved: {filename}")

# =========================
# 9. Run everything
# =========================
if __name__ == "__main__":
    
    file_paths = [
        #"transoptas_5pso.csv",
        "tinytla.csv",
        "ela.csv",
        "deepela_large_r1.csv",
        "doe2vec.csv"
    ]
    
    stats_file = "distance_stats.csv"
    
    # Load percentile thresholds
    percentiles_map = load_percentiles(stats_file)
    reverse = None

    mapping_file = "global_reverse_mapping.json"
    if os.path.exists(mapping_file ):
        print(f"Loading existing mapping from {mapping_file}")
        with open(mapping_file, "r") as f:
            reverse = json.load(f)
    else:
        print("Building global reverse mapping...")
        reverse = build_global_reverse_mapping(file_paths)
    
        #print(f"Saving mapping to {mapping_file}")
        with open(mapping_file, "w") as f:
            json.dump(reverse, f, indent=4)
        save_reverse_mapping(reverse)
    
    
    # Generate graphs
    for file_path in file_paths:
        representation_name = file_path.split(".")[0]
        generate_graphs(file_path, representation_name, percentiles_map, reverse)
        
        
