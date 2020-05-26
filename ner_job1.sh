#!/bin/bash
#SBATCH --time=16:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --mem-per-cpu=10G
module load python/3.7
virtualenv --no-download $SLURM_TMPDIR/env1
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt
python ner_tool.py 10710 11709 20 47

