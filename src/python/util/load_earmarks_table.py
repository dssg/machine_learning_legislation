CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

import os, sys
import codecs
import random
import psycopg2
import csv
with open('/mnt/data/sunlight/OMB/all.csv', 'rb') as f:
	reader = csv.reader(f)
	reader.next()
	rows = []
	for row in reader:
		rows.append(row)

	print len(rows)

conn = psycopg2.connect(CONN_STRING)
cmd = "insert into earmarks (earmark_id, earmark_code, agency, bureau, account, program, enacted_year, short_description, full_description, earmark_type, spendcom) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
params = rows
cur = conn.cursor()
cur.execute ("delete from earmarks")
cur.executemany(cmd, params)
conn.commit()
conn.close()





