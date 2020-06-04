#!/bin/bash
#SBATCH --time=4:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r ../requirements.txt
python get_non_entities.py 50000 58422 10 47
cat token-results/token50000-58422/*.txt > merged50000-58422.txt
sort -u --parallel=8 -o merged50000-58422.txt merged50000-58422.txt

