#!/bin/bash
#SBATCH --time=3:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=10G
module load python/3.6
cat merged*.txt > tokens_for_db.txt
tar -cvzf tokens_for_db.tar.gz tokens_for_db.txt
python simplify.py
sort -u --parallel=8 -o tokens.txt tokens.txt 
python get_freq.py