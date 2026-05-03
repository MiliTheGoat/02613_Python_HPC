#!/bin/bash
#BSUB -J Ex10_Profile
#BSUB -q gpuv100
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=8GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -W 00:45
#BSUB -o output/ex10_profile_%J.out
#BSUB -e output/ex10_profile_%J.err
#BSUB -B
#BSUB -N
##BSUB -u s225102@dtu.dk

mkdir -p output results profiles

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

module load cuda/11.8
export CUDA_PATH=$CUDA_ROOT
export CUPY_CACHE_DIR=/tmp/cupy_cache_${LSB_JOBID}

echo "CUDA_PATH : $CUDA_PATH"
echo "GPU       : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "Host      : $(hostname)"
echo "Date      : $(date)"
echo ""

# ── 1. Profile the UNOPTIMISED version with nsys ─────────────────────────────
echo "=== [1/3] nsys profile: unoptimised (ex9), N=5 ==="
nsys profile \
    --trace=cuda,nvtx \
    --output=profiles/ex10_unoptimised_%j \
    --force-overwrite=true \
    python ex9_simulate_cupy.py 5

# Print a quick text summary (works if nsys stats is available)
nsys stats --report cuda_api_sum \
    profiles/ex10_unoptimised_${LSB_JOBID}.nsys-rep 2>/dev/null && echo "" || \
    echo "(Open .nsys-rep in Nsight Systems GUI for the full trace)"

echo ""
echo "--- What to look for in the nsys output ---"
echo "  cudaMemcpy DtoH will appear THOUSANDS of times — one per iteration."
echo "  This is delta.item() forcing a GPU->CPU sync every Jacobi step."
echo "  GPU utilisation will be low; the device sits idle waiting for CPU."
echo ""

# ── 2. Profile the OPTIMISED version ─────────────────────────────────────────
echo "=== [2/3] nsys profile: optimised (ex10), N=5 ==="
nsys profile \
    --trace=cuda,nvtx \
    --output=profiles/ex10_optimised_%j \
    --force-overwrite=true \
    python ex10_simulate_cupy_optimised.py 5

nsys stats --report cuda_api_sum \
    profiles/ex10_optimised_${LSB_JOBID}.nsys-rep 2>/dev/null || true

echo ""

# ── 3. Head-to-head wall-time comparison ─────────────────────────────────────
echo "=== [3/3] Timing comparison N=50 ==="
echo "-- unoptimised --"
python ex9_simulate_cupy.py 50 | tee results/ex10_unoptimised_N50.csv

echo ""
echo "-- optimised --"
python ex10_simulate_cupy_optimised.py 50 | tee results/ex10_optimised_N50.csv

echo ""
echo "Done: $(date)"
