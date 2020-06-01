#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=10G
cd database/
python get_non_entities.py
sort -u --parallel=8 -o sorted.txt non_entities.txt 
