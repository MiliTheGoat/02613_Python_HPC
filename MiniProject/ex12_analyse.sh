#!/bin/bash
# ── Run AFTER all 7 Ex12 jobs have finished ───────────────────────────────────
# Pure CPU: merges 7 slice CSVs and runs pandas/matplotlib analysis.
# Can also be run directly on the login node without submitting:
#   python ex12_merge_analyse.py
#
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

mkdir -p output figures

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

echo "Slice files in results/:"
ls -lh results/ex12_[0-9]*_[0-9]*.csv 2>/dev/null || echo "  (none found)"
echo ""

# Merge + analyse in one script
python ex12_merge_analyse.py

echo "Done: $(date)"
