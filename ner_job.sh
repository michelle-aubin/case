#!/bin/bash
#SBATCH --time=12:00:00
python ner_tool.py 10000 34210 10 4
python ner_tool.py 34211 58422 10 4

