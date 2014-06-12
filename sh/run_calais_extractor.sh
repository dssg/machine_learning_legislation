#!/bin/bash
# usage: ./run_calais_extractor.sh <bills_paths_file> <num_threads> 
HOME="/home/mkhabsa/code/machine_learning_legislation"
CMD="python $HOME/src/python/ner/bills_ner.py"
FILE_NAMES=$1
THREADS=$2

cat $FILE_NAMES | parallel --tmpdir /tmp/calais/ --files -P $THREADS $CMD "{}"
