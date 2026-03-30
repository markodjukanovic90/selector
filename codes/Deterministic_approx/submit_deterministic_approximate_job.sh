#!/bin/bash
#SBATCH --job-name=graph_approx
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=logs/%x_%j.out

INPUT=$1
OUTPUT=$2
ALG=$3

#module purge
module load Python/3.8.6-GCCcore-10.2.0
source /ceph/hpc/home/djukanovicm/venv/bin/activate

# Debug (optional but VERY useful)
#which python3
#python3 -c "import networkx as nx; print(nx.__version__)"

#python -m pip install networkx

python /ceph/hpc/home/djukanovicm/selector/code/approximate_deterministic/approx_deterministic.py -i "$INPUT" -o "$OUTPUT" -a "$ALG"
