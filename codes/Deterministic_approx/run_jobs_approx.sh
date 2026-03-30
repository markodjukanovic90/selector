#!/bin/bash

#########################################################################################
# Run MIS / MDS over all graphs using SLURM (srun): two exact solvers are implemented, 
########################################################################################

ALG=$1        # 0 = MIS, 1 = MDS
TIME_MAX=600  # seconds

# Directories
GRAPH_DIR="/ceph/hpc/home/djukanovicm/selector/code/graphs"
RUNS_DIR="/ceph/hpc/home/djukanovicm/selector/code/results_deterministic_approximate"

mkdir -p "$RUNS_DIR"


echo "Running algorithm: $ALG"
echo "Graph dir: $GRAPH_DIR"
echo "Results dir: $RUNS_DIR"
echo "--------------------------------------------------"

# Loop over all graph files
for graph in ${GRAPH_DIR}/*.json; do
	    
	    fname=$(basename "$graph" .json)
	        out_file="${RUNS_DIR}/${fname}_alg${ALG}.json"

		    echo "Submitting: $fname"

		    sbatch submit_deterministic_approximate_job.sh "$graph" "$out_file" "$ALG"
done

# Wait for all jobs
		

		echo "All jobs completed."
