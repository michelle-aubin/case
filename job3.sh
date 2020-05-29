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
python process_text.py 30000 39999 10 47
cd sentences/
tar -cvzf sent30000-39999.tar.gz sent30000-39999/
cd ../ner-results/
tar -cvzf ner30000-39999.tar.gz ner30000-39999/