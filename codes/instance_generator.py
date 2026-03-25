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

# Optional (uncomment if needed)
def mahalanobis_distance_matrix(X):
    cov = np.cov(X, rowvar=False)
    VI = np.linalg.pinv(cov)  # robust inverse
    return squareform(pdist(X, metric='mahalanobis', VI=VI))

# =========================
# 4. GLOBAL reverse mapping
# =========================
def build_global_reverse_mapping(file_paths):
    all_labels = set()
    
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        labels = df.iloc[:, 0].astype(str).tolist()
        all_labels.update(labels)
    
    all_labels = sorted(all_labels)  # ensure consistency
    
    reverse = {label: i for i, label in enumerate(all_labels)}
    
    return reverse

def save_reverse_mapping(reverse):
    os.makedirs("graphs", exist_ok=True)
    
    with open("graphs/global_reverse_mapping.json", "w") as f:
        json.dump(reverse, f, indent=4)
    
    print("Saved: graphs/global_reverse_mapping.json")

# =========================
# 5. Graph construction
# =========================
def build_graph(labels, D, eps, reverse):
    graph = {}
    
    # Initialize nodes present in this dataset
    node_ids = [reverse[label] for label in labels]
    for nid in node_ids:
        graph[nid] = []
    
    n = len(labels)
    
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] <= eps:
                u = reverse[labels[i]]
                v = reverse[labels[j]]
                
                graph[u].append(v)
                graph[v].append(u)
    
    return graph

# =========================
# 6. Save graph
# =========================
def save_graph(graph, filename):
    with open(filename, 'w') as f:
        json.dump(graph, f, indent=4)

# =========================
# 7. Main pipeline
# =========================
def generate_graphs(file_path, representation_name, eps_values, reverse):
    
    labels, X = load_data(file_path)
    X_scaled = scale_data(X)

    # Compute distance matrices
    distances = {
        "cosine": cosine_distance_matrix(X_scaled),
        "correlation": correlation_distance_matrix(X_scaled),
        "seuclidean": standardized_euclidean_distance_matrix(X_scaled),
        # "mahalanobis": mahalanobis_distance_matrix(X_scaled)  # optional
    }

    os.makedirs("graphs", exist_ok=True)

    for dist_name, D in distances.items():
        for eps in eps_values:
            
            graph = build_graph(labels, D, eps, reverse)
            
            filename = f"graphs/{representation_name}_{dist_name}_{eps}.json"
            save_graph(graph, filename)
            
            print(f"Saved: {filename}")

# =========================
# 8. Run everything
# =========================
if __name__ == "__main__":
    
    # Your datasets
    file_paths = [
        "transoptas_5pso.csv",
        "tinytla.csv",
        "ela.csv",
        "deepela_large_r1.csv",
        "doe2vec.csv"
    ]
    
    eps_values = [0.1, 0.2, 0.5, 1.0, 2.0]
    
    # STEP 1: Build GLOBAL reverse mapping
    reverse = build_global_reverse_mapping(file_paths)
    save_reverse_mapping(reverse)
    
    # STEP 2: Generate graphs per dataset
    for file_path in file_paths:
        representation_name = file_path.split(".")[0]
        generate_graphs(file_path, representation_name, eps_values, reverse)
        


