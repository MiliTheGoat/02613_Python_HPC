#!/bin/bash
# ── Correct queue from Week 10 slides: c02613 ────────────────────────────────
#BSUB -J Ex9_CuPy
#BSUB -q c02613
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

# ── CUDA setup ────────────────────────────────────────────────────────────────
# Load the module first so $CUDA_ROOT is populated, then export as CUDA_PATH
# so CuPy's nvrtc compiler can find the correct toolkit headers.
module load cuda/11.8
export CUDA_PATH=$CUDA_ROOT
export CUDA_HOME=$CUDA_ROOT
export PATH=$CUDA_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_ROOT/lib64:$LD_LIBRARY_PATH
export CUPY_CACHE_DIR=/tmp/cupy_${LSB_JOBID}   # fresh per-job cache

echo "CUDA_PATH : $CUDA_PATH"
echo "nvcc      : $(which nvcc)  $(nvcc --version | grep release)"
echo "GPU       : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "Host      : $(hostname)"
echo ""

python ex9_simulate_cupy.py 50 | tee results/ex9_N50.csv

echo "Done: $(date)"
