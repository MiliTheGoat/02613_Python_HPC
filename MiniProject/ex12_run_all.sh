#!/bin/bash
#BSUB -J Ex12_RunAll
#BSUB -q c02613
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
export CUDA_HOME=$CUDA_ROOT
export PATH=$CUDA_ROOT/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_ROOT/lib64:$LD_LIBRARY_PATH
export CUPY_CACHE_DIR=/tmp/cupy_${LSB_JOBID}

echo "CUDA_PATH : $CUDA_PATH"
echo "GPU       : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo ""

python ex12_run_all_buildings.py

echo "Done: $(date)"
