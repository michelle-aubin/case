#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
#SBATCH --output=sort-job-%j.out
module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r ../requirements.txt
python get_non_entities.py 0 29999 10 47
python get_non_entities.py 30000 58421 10 47
cat token-results/token0-29999/*.txt token-results/token30000-58421/*.txt  > all_tokens.txt
tar -cvzf all_tokens.tar.gz all_tokens.txt


