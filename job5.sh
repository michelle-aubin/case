#!/bin/bash
#SBATCH --time=4:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --mem=0
module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index -r requirements.txt
python process_text.py 8211 8211 10 47
python process_text.py 12058 12058 10 47
python process_text.py 13029 13029 10 47
python process_text.py 28901 28901 10 47
python process_text.py 38738 38738 10 47
python process_text.py 48712 48712 10 47
python process_text.py 52500 52500 10 47
python process_text.py 53485 53485 10 47
cd sentences/
tar -cvzf sent8211-8211.tar.gz sent8211-8211/
tar -cvzf sent12058-12058.tar.gz sent12058-12058/
tar -cvzf sent13029-13029.tar.gz sent13029-13029/
tar -cvzf sent28901-28901.tar.gz sent28901-28901/
tar -cvzf sent38738-38738.tar.gz sent38738-38738/
tar -cvzf sent48712-48712.tar.gz sent48712-48712/
tar -cvzf sent52500-52500.tar.gz sent52500-52500/
tar -cvzf sent53485-53485.tar.gz sent53485-53485/
cd ../ner-results/
tar -cvzf ner8211-8211.tar.gz sent8211-8211/
tar -cvzf ner12058-12058.tar.gz ner12058-12058/
tar -cvzf ner13029-13029.tar.gz ner13029-13029/
tar -cvzf ner28901-28901.tar.gz ner28901-28901/
tar -cvzf ner38738-38738.tar.gz ner38738-38738/
tar -cvzf ner48712-48712.tar.gz ner48712-48712/
tar -cvzf ner52500-52500.tar.gz ner52500-52500/
tar -cvzf ner53485-53485.tar.gz ner53485-53485/