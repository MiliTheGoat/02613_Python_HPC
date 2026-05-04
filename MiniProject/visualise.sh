#!/bin/bash
# ── LSF/bsub options ──────────────────────────────────────────────────────────
#BSUB -J Ex1_Visualize
#BSUB -q hpc
# 4 GB RAM is plenty for loading a handful of .npy files
#BSUB -R "rusage[mem=4GB]"
# Single core – visualization is not compute-heavy
#BSUB -n 4
#BSUB -R "span[hosts=1]"
# Wall time: 5 minutes is more than enough
#BSUB -W 00:05
# Output / error logs
#BSUB -o outputs/ex1_visualize_%J.out
#BSUB -e outputs/ex1_visualize_%J.err
# E-mail notifications
#BSUB -B
#BSUB -N
##BSUB -u s225102@dtu.dk   # <-- uncomment and replace with your e-mail
# ─────────────────────────────────────────────────────────────────────────────

# Create output directories if they don't exist yet
mkdir -p outputs
mkdir -p figures

# Activate the course conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

# ── Run the visualization script ──────────────────────────────────────────────
# Argument: number of floorplans to visualize (default 6, change freely)

python visualise.py 8
