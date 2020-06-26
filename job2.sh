#!/bin/bash
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
#SBATCH --job-name=20000-39999
#SBATCH --output=%x.out
module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
python process_text.py 20000 39999 10 47
cd sentences/
tar -cvzf sent20000-39999.tar.gz sent20000-39999/
cd ../entities/
tar -cvzf ent20000-39999.tar.gz ent20000-39999/
cd ../terms/
tar -cvzf term20000-39999.tar.gz term20000-39999/