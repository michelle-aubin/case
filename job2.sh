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
python process_text.py 20000 29999 10 47
cd sentences/
tar -cvzf sent20000-29999.tar.gz sent20000-29999/
cd ../ner-results/
tar -cvzf ner20000-29999.tar.gz ner20000-29999/