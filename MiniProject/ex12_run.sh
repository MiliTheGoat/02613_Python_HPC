#!/bin/bash
# ── Job array: 7 jobs, each processes ~654 buildings ─────────────────────────
# Timing from actual run: ~1.82 s/building on A100 MIG 2g.20gb
#   4571 buildings / 7 jobs = 653 buildings/job
#   653 × 1.82 s = ~20 min  (safe under 30-min wall limit)
#
#BSUB -J "Ex12[1-7]"
#BSUB -q c02613
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=24GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -W 00:30
#BSUB -o output/ex12_%I_%J.out
#BSUB -e output/ex12_%I_%J.err
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

# Compute this job's slice of the 4571 buildings
N_TOTAL=4571
N_JOBS=7
CHUNK=$(( (N_TOTAL + N_JOBS - 1) / N_JOBS ))   # ceil(4571/7) = 654
START=$(( (LSB_JOBINDEX - 1) * CHUNK ))
END=$(( LSB_JOBINDEX * CHUNK ))
if [ $END -gt $N_TOTAL ]; then END=$N_TOTAL; fi

echo "Job array index : $LSB_JOBINDEX / $N_JOBS"
echo "Slice           : buildings [$START, $END)  =  $((END - START)) buildings"
echo "GPU             : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "Host            : $(hostname)"
echo ""

python ex12_simulate.py $START $END

echo "Finished: $(date)"
