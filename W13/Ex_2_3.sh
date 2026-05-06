#!/bin/bash
#BSUB -J NumPy_MT
#BSUB -q hpc
#BSUB -R "rusage[mem=4GB]"
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6142]"
#BSUB -W 00:10
#BSUB -o output/numpy_mt_%J.out
#BSUB -e output/numpy_mt_%J.err

mkdir -p output

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

NUM_THREADS=8
OMP_NUM_THREADS=$NUM_THREADS
MPI_NUM_THREADS=$NUM_THREADS
MKL_NUM_THREADS=$NUM_THREADS
OPENBLAS_NUM_THREADS=$NUM_THREADS

python matmuls.py