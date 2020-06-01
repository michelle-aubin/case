#!/bin/bash
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=0
sort -u --parallel=8 -o sorted.txt non_entities.txt 