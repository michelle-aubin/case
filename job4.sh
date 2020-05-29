#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
python ner_tool.py 40000 58422 10 47
cd sentences/
tar -cvzf sent40000-58422.tar.gz sent40000-58422/
cd ../ner-results/
tar -cvzf ner40000-58422.tar.gz ner40000-58422/