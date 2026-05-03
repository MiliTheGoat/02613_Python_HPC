#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J Week_8
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=4GB]"
# -- tells the scheduler to run the job on Intel Xeon Gold 6142 CPU only--
#BSUB -R "select[model == XeonGold6142]"
# -- Notify me by email when execution begins --
#BSUB -B
# -- Notify me by email when execution ends   --
#BSUB -N
# -- s225102@dtu.dk -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u s225102@dtu.dk
# -- Output File --
#BSUB -o output/PAR_python4C_%J.out
# -- Error File --
#BSUB -e output/PAR_python4C_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 00:30
# -- Number of cores requested -- 
#BSUB -n 4
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python next.py mandelbrot.npy 100 3