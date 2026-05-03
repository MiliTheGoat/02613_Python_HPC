#!/bin/bash
#BSUB -J Ex10_Profile
#BSUB -q c02613
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=8GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -W 00:30
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
export CUDA_HOME=$CUDA_ROOT
export PATH=$CUDA_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_ROOT/lib64:$LD_LIBRARY_PATH
export CUPY_CACHE_DIR=/tmp/cupy_${LSB_JOBID}

echo "CUDA_PATH : $CUDA_PATH"
echo "GPU       : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo ""

# ── 1. Profile unoptimised (ex9) ─────────────────────────────────────────────
echo "=== nsys: unoptimised (N=5) ==="
nsys profile \
    --trace=cuda,nvtx \
    --output=profiles/ex10_unoptimised_%j \
    --force-overwrite=true \
    python ex9_simulate_cupy.py 5

echo ""
echo "--- What to look for in cudaapisum ---"
echo "  cuMemcpyDtoH will have Num Calls in the THOUSANDS."
echo "  That is delta.item() triggering a GPU->CPU sync every iteration."
echo "  Compare Num Calls here with the optimised version below."
echo ""

# nsys stats text summary (works on DTU if nsys >= 2022.x)
nsys stats --report cuda_api_sum \
    profiles/ex10_unoptimised_${LSB_JOBID}.nsys-rep 2>/dev/null || \
    echo "(nsys stats not available – open .nsys-rep in Nsight Systems GUI)"

echo ""

# ── 2. Profile optimised (ex10) ──────────────────────────────────────────────
echo "=== nsys: optimised (N=5) ==="
nsys profile \
    --trace=cuda,nvtx \
    --output=profiles/ex10_optimised_%j \
    --force-overwrite=true \
    python ex10_simulate_cupy_optimised.py 5

nsys stats --report cuda_api_sum \
    profiles/ex10_optimised_${LSB_JOBID}.nsys-rep 2>/dev/null || true

echo ""

# ── 3. Wall-time comparison ───────────────────────────────────────────────────
echo "=== Timing N=50: unoptimised ==="
python ex9_simulate_cupy.py 50 | tee results/ex10_unoptimised_N50.csv
echo ""
echo "=== Timing N=50: optimised ==="
python ex10_simulate_cupy_optimised.py 50 | tee results/ex10_optimised_N50.csv

echo ""
echo "Done: $(date)"
