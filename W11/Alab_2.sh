#!/bin/bash
#BSUB -J "Thajob[2, 29, 71, 73, 127]"
#BSUB -q hpc
#BSUB -R "rusage[mem=1GB]"
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -W 00:10
#BSUB -o output/array_%I_%J.out
#BSUB -e output/array_%I_%J.err

mkdir -p output

echo "Job array index : $LSB_JOBINDEX"
echo "Job ID          : $LSB_JOBID"
echo "Host            : $(hostname)"