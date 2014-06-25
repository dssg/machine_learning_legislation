CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

import os, sys
import codecs
import random
import psycopg2
import csv, pandas as pd

infile = open('2009_db.csv', 'rb')
outfile = open('tmpfile.csv', 'wb')
BLOCKSIZE = 65536 # experiment with size
while True:
    block = infile.read(BLOCKSIZE)
    if not block: break
    outfile.write(block.decode('ascii').encode('utf8'))
infile.close()
outfile.close()



rows = []
stuff = pd.read_csv(codecs.open('tmpfile.csv','r','utf-8'))
i = 0
for row in stuff.iterrows():
    v = list(row[1])
    i = i+1
    print i 
    if not isinstance(v[3],basestring) or not isinstance(v[2],basestring):
        v[3] = ''
        v[2] = ''
    rows.append(v)

conn = psycopg2.connect(CONN_STRING)
cmd = "insert into earmark_documents (earmark_id, document_id,page_number,excerpt) values (%s, %s, %s, %s)"
params = rows
cur = conn.cursor()
#r.execute ("delete from earmark_documents")
cur.executemany(cmd, params)
conn.commit()
conn.close()
