#!/bin/bash
#SBATCH --time=20:00:00
#SBATCH --mem=10G
module load python/3.7
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt
python ner_tool.py 10000 34210 10 8
