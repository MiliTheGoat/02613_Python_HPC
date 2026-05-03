#!/bin/bash
#BSUB -J Ex12_RunAll
#BSUB -q gpuv100
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=24GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -W 04:00
#BSUB -o output/ex12_runall_%J.out
#BSUB -e output/ex12_runall_%J.err
#BSUB -B
#BSUB -N
##BSUB -u s225102@dtu.dk

mkdir -p output results

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

module load cuda/11.8
export CUDA_PATH=$CUDA_ROOT
export CUPY_CACHE_DIR=/tmp/cupy_cache_${LSB_JOBID}

echo "GPU  : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "Host : $(hostname)"
echo "Date : $(date)"
echo ""

python ex12_run_all_buildings.py

echo "Done: $(date)"
