import json
import pulp
import argparse
import time
import os
import random
import orloge
from math import ceil

# =========================
# Load graph
# =========================
def load_graph(file_path):
    with open(file_path, 'r') as f:
        graph = json.load(f)
    
    # Convert keys to int
    graph = {int(k): v for k, v in graph.items()}
    return graph

# =========================
# Build edge list
# =========================
def build_edges(graph):
    edges = set()
    for i, neighbors in graph.items():
        for j in neighbors:
            if i < j:
                edges.add((i, j))
    return list(edges)

# =========================
# MIS
# =========================
def solve_MIS(graph, time_limit=None):
    nodes = list(graph.keys())
    edges = build_edges(graph)

    model = pulp.LpProblem("MIS", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("x", nodes, cat="Binary")

    model += pulp.lpSum(x[i] for i in nodes)

    for (i, j) in edges:
        model += x[i] + x[j] <= 1

    ind=random.randint(0, 100000);
    solver = pulp.CPLEX_CMD(msg=0, path = r'/home/marko/Desktop/cplex/cplex/bin/x86-64_linux/cplex',  logPath="log_info"+str(ind)+".log", timeLimit=time_limit)
 
    start = time.time()
    model.solve(solver)
    end = time.time()

    solution = [i for i in nodes if pulp.value(x[i]) > 0.5]
    
    # retrieve gap: 
    logs_dict = orloge.get_info_solver("log_info"+str(ind)+".log", "CPLEX" ) # Orloge returns a dict with all logs info
    best_bound, best_solution, status = logs_dict["best_bound"], logs_dict["best_solution"], logs_dict["status"]
    #print("Best bound: ", best_bound) 
    #print(logs_dict)
    os.remove("log_info"+str(ind)+".log")

    return {
        "LB": int(best_bound),
        "status": pulp.LpStatus[model.status],
        "objective": pulp.value(model.objective),
        "solution": solution,
        "time": end - start
    }

# =========================
# MDS
# =========================
def solve_MDS(graph, time_limit=None):
    nodes = list(graph.keys())

    model = pulp.LpProblem("MDS", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", nodes, cat="Binary")

    model += pulp.lpSum(x[i] for i in nodes)

    for i in nodes:
        model += x[i] + pulp.lpSum(x[j] for j in graph[i]) >= 1

    ind=random.randint(0, 100000);
    solver = pulp.CPLEX_CMD(msg=0, path = r'/home/marko/Desktop/cplex/cplex/bin/x86-64_linux/cplex', logPath="log_info"+str(ind)+".log",  timeLimit=time_limit)

    start = time.time()
    model.solve(solver)
    end = time.time()

    solution = [i for i in nodes if pulp.value(x[i]) > 0.5]
    
    # retrieve gap: 
    logs_dict = orloge.get_info_solver("log_info"+str(ind)+".log", "CPLEX" ) # Orloge returns a dict with all logs info
    best_bound, best_solution, status = logs_dict["best_bound"], logs_dict["best_solution"], logs_dict["status"]
    #print("Best bound: ", best_bound) 
    #print(logs_dict)
    os.remove("log_info"+str(ind)+".log")
    
    #return best_solution, ceil(best_bound), int(status == "MIP - Integer optimal")#"MIP - Time limit exceeded" --if not optimal

    return {
        "LB": ceil(best_bound),
        "status": pulp.LpStatus[model.status],
        "objective": pulp.value(model.objective),
        "solution": solution,
        "time": end - start
    }

# =========================
# Save output
# =========================
def save_output(result, output_file):

    #os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(result, f, indent=4)

# =========================
# MAIN (CLI)
# =========================
def main():
    parser = argparse.ArgumentParser(description="Graph Optimization (MIS / MDS)")

    parser.add_argument("-i", "--input", required=True, help="Input graph JSON")
    parser.add_argument("-o", "--output", required=True, help="Output solution file")
    parser.add_argument("-a", "--algorithm", type=int, required=True,
                        help="0: MIS, 1: MDS, 2: TODO")
    parser.add_argument("-t", "--time_limit", type=int, default=None,
                        help="Time limit in seconds (optional)")

    args = parser.parse_args()

    # Load graph
    graph = load_graph(args.input)

    # Select algorithm
    if args.algorithm == 0:
        print("Running MIS...")
        result = solve_MIS(graph, args.time_limit)

    elif args.algorithm == 1:
        print("Running MDS...")
        result = solve_MDS(graph, args.time_limit)

    elif args.algorithm == 2:
        raise NotImplementedError("Algorithm 2 not implemented yet")

    else:
        raise ValueError("Invalid algorithm choice")

    # Save result
    save_output(result, args.output)

    print("Done.")
    print("Objective:", result["objective"])
    print("LB:", result["LB"])
    print("Time:", result["time"])

# =========================
if __name__ == "__main__":
    main()
