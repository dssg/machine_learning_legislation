#!/bin/bash
# usage: ./run_fetch_missing_congress_reports.sh <report_ids_file> <num_threads> <out_dir> 
HOME="/home/mkhabsa/code/machine_learning_legislation"
CMD="python $HOME/src/python/bill_fetcher/congress_report_downloader.py"
FILE_NAMES=$1
THREADS=$2
OUT_DIR=$3

cat $FILE_NAMES | parallel --tmpdir /tmp/congress-reports/ --files -P $THREADS $CMD fetch-zip --reportid "{}" --outdir $OUT_DIR
