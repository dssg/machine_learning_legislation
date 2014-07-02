CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

import os, sys
import psycopg2
import csv
import numpy as np
import pandas as pd




years = ['2010', '2009', '2008', '2005']

keep = [
        'earmark_id',
        'earmark_code',
        'agency_title',
        'bureau_title',
        'account_title',
        'program',
        'enacted_year', 
        'short_description',
        'earmark_description',
        'earmark_type_name',
        'spendcom',
        'recipient'
        ]

keepset = set(keep)

ds = []
for year in years:
    fname = '/mnt/data/sunlight/OMB/'+year+'.csv'
    d = pd.read_csv(fname, low_memory=False)
    d.columns = [h.lower().replace(" ", "_") for h in d.columns]    
    if year == '2005':
        d['earmark_id'] = range(d.shape[0])
    ds.append(d)

d = pd.concat(ds)

ear = pd.concat(ds)[keep]

new_index = [
        'earmark_id',
        'earmark_code',
        'agency',
        'bureau',
        'account',
        'program',
        'enacted_year', 
        'short_description',
        'full_description',
        'earmark_type',
        'spendcom',
        'recipient'
        ]






          
ear.columns =  new_index




# there is an entry per sponsor, just keep one of them
def get_recipient(df):
    for index, row in df.iterrows():
        if row["recipient"] is not np.NaN:
            return df.ix[index]
    print "not found"
    
    return df.ix[df.index[0]]
    

ear = ear.groupby('earmark_id').apply(get_recipient)


def shorten_full_description(str):
    try:
        return str[0:2045]
    except:
        return str
    
ear['full_description'] = ear.full_description.map(shorten_full_description)



def convert(x):
    try:
       return x.astype(int)
    except:
        return x
    
ear.apply(convert).to_csv('/mnt/data/sunlight/OMB/all.csv', header=True, index=False)





with open('/mnt/data/sunlight/OMB/all.csv', 'rb') as f:
	reader = csv.reader(f)
	reader.next()
	rows = []
	for row in reader:
		rows.append(row)

	print len(rows)

conn = psycopg2.connect(CONN_STRING)
cmd = "insert into earmarks ("+", ".join(new_index)+") values ("+", ".join(["%s"]*len(new_index))+")"
print cmd
params = rows
cur = conn.cursor()
cur.execute ("delete from earmarks")
cur.executemany(cmd, params)
conn.commit()
conn.close()





