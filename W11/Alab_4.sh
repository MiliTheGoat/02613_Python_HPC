#!/bin/bash
#BSUB -J "AfterArray"
#BSUB -q hpc
#BSUB -R "rusage[mem=1GB]"
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -W 00:10
#BSUB -o output/after_array_%J.out
#BSUB -e output/after_array_%J.err
#BSUB -w "ended(21241475)"

mkdir -p output

echo "All array elements have finished."
echo "Job ID : $LSB_JOBID"
echo "Host   : $(hostname)"