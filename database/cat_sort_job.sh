#!/bin/bash
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=10G
cat non_entities.txt merged*.txt > tokens.txt
sort -u --parallel=8 -o tokens.txt tokens.txt 
tar -cvzf tokens.tar.gz tokens.txt
