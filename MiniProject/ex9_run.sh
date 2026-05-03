#!/bin/bash
#BSUB -J Ex9_CuPy
#BSUB -q gpuv100
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=8GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -W 00:30
#BSUB -o output/ex9_cupy_%J.out
#BSUB -e output/ex9_cupy_%J.err
#BSUB -B
#BSUB -N
##BSUB -u s225102@dtu.dk

mkdir -p output results

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

# ── Fix: CuPy needs to know where the CUDA toolkit lives ─────────────────────
# The cuda/11.8 module sets $CUDA_ROOT; export it as CUDA_PATH so that
# CuPy's nvrtc compiler can find the correct headers and architecture flags.
module load cuda/11.8
export CUDA_PATH=$CUDA_ROOT          # CuPy reads CUDA_PATH at compile time
export CUPY_CACHE_DIR=/tmp/cupy_cache_${LSB_JOBID}   # per-job clean cache

echo "CUDA_PATH : $CUDA_PATH"
echo "GPU       : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "Host      : $(hostname)"
echo "Date      : $(date)"
echo ""

python ex9_simulate_cupy.py 50 | tee results/ex9_N50.csv

echo "Done: $(date)"
