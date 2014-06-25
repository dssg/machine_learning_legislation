import os, sys
import psycopg2
import csv, pandas as pd
import codecs
from pprint import pprint

USAGE = "python %s <input-csv-file>" %(sys.argv[0])

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

def import_csv_file(path):
    rows  = []
    stuff = pd.read_csv(codecs.open(path,'r','utf-8'))
    i = 0
    for row in stuff.iterrows():
        v = list(row[1])
        i = i+1
        #print i
        if not isinstance(v[3],basestring) or not isinstance(v[2],basestring):
            v[3] = ''
            v[2] = ''
        rows.append(v)

    conn = psycopg2.connect(CONN_STRING)
    cmd = "insert into earmark_documents (earmark_id, document_id,page_number,excerpt)\
 values (%s, %s, %s, %s)"
    params = rows; pprint(rows); return
    cur = conn.cursor()
#r.execute ("delete from earmark_documents")                                       
    cur.executemany(cmd, params)
    conn.commit()
    conn.close()

if __name__=="__main__":
    if len(sys.argv) < 2:
        print USAGE
    else:
        import_csv_file(sys.argv[1])
