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
echo "Host      : $(hostname)"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: nsys profile of the UNOPTIMISED solution (small N, just for the file)
# Note: nsys stderr shows version-mismatch warnings — these are harmless.
# The .nsys-rep file IS generated and can be opened in Nsight Systems GUI
# to see the thousands of DtoH transfers caused by delta.item() each iteration.
# ─────────────────────────────────────────────────────────────────────────────
echo "=== [1/2] nsys profile: generating .nsys-rep files for GUI inspection ==="

nsys profile \
    --trace=cuda,nvtx \
    --output=profiles/ex10_unoptimised_${LSB_JOBID} \
    --force-overwrite=true \
    python ex9_simulate_cupy.py 5 2>/dev/null

echo "Unoptimised profile: profiles/ex10_unoptimised_${LSB_JOBID}.nsys-rep"

nsys profile \
    --trace=cuda,nvtx \
    --output=profiles/ex10_optimised_${LSB_JOBID} \
    --force-overwrite=true \
    python ex10_simulate_cupy_optimised.py 5 2>/dev/null

echo "Optimised profile  : profiles/ex10_optimised_${LSB_JOBID}.nsys-rep"
echo "(Open both in Nsight Systems GUI: unoptimised shows thousands of"
echo " tiny DtoH memcpy calls; optimised shows 100x fewer.)"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: 4-case instrumented profiling with summary table
# Cases: unoptimised N=50, unoptimised N=100, optimised N=50, optimised N=100
# ─────────────────────────────────────────────────────────────────────────────
echo "=== [2/2] Instrumented profiling: 4 cases ==="
python ex10_profile_instrumented.py | tee results/ex10_summary.txt

echo ""
echo "Done: $(date)"