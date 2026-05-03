#!/bin/bash
#BSUB -J Ex12_Analyse
#BSUB -q hpc
#BSUB -R "rusage[mem=4GB]"
#BSUB -n 1
#BSUB -R "span[hosts=1]"
#BSUB -W 00:15
#BSUB -o output/ex12_analyse_%J.out
#BSUB -e output/ex12_analyse_%J.err
#BSUB -B
#BSUB -N
##BSUB -u s225102@dtu.dk
# Submit AFTER ex12_run_all.sh has finished.

mkdir -p output figures

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

if [ ! -f results/ex12_all_results.csv ]; then
    echo "ERROR: results/ex12_all_results.csv not found - run ex12_run_all.sh first"
    exit 1
fi

echo "Rows in CSV: $(wc -l < results/ex12_all_results.csv)"
python ex12_analyse.py
echo "Done: $(date)"
