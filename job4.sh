#!/bin/bash
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
#SBATCH --job-name=60000-73864
#SBATCH --output=%x.out
module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
python process_text.py 60000 73864 10 47
cd sentences/
tar -cvzf sent60000-73864.tar.gz sent60000-73864/
cd ../entities/
tar -cvzf ent60000-73864.tar.gz ent60000-73864/
cd ../terms/
tar -cvzf term60000-73864.tar.gz term60000-73864/