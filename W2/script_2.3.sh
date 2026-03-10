#!/bin/bash
# embedded options to bsub - start with #BSUB
# -- our name ---
#BSUB -J Exercises_Week_1
# -- choose queue --
#BSUB -q hpc
# -- specify that we need 4GB of memory per core/slot --
# so when asking for 4 cores, we are really asking for 4*4GB=16GB of memory 
# for this job. 
#BSUB -R "rusage[mem=4GB]"
# -- tells the scheduler to run the job on aXeonE5_2660v3 CPU only--
#BSUB -R "select[model == XeonE5_2660v3]"
# -- Notify me by email when execution begins --
#BSUB -B
# -- Notify me by email when execution ends   --
#BSUB -N
# -- s225102@dtu.dk -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u s225102@dtu.dk
# -- Output File --
#BSUB -o Output_%J.out
# -- Error File --
#BSUB -e Output_%J.err
# -- estimated wall clock time (execution time): hh:mm -- 
#BSUB -W 2
# -- Number of cores requested -- 
#BSUB -n 1
# -- Specify the distribution of the cores: on a single node --
#BSUB -R "span[hosts=1]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python -u Numpy2.3.py 4 5 6