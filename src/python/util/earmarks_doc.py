import pandas as pd, numpy as np
import time, re, os, ast
from datetime import datetime
from datetime import date
import path_tools as pt

## importing the relevant csv file ## 
earmarks_10 = pd.read_csv("2010_pd.csv") 

earmarks_10['doc_id'] = ' '
bill_path = pt.BillPathUtils()
report_path = pt.ReportPathUtils()

for i in earmarks_10.iterrows():
    path = i[1]['path']
    #doc_name = i[1]['doc_name']
    if isinstance(path,basestring):
        path = ast.literal_eval(path)
        congress = 111
        bvr = path[0]
        hvs = path[1]
        num = path[2]
        if bvr == 'bill':
            if hvs == 'senate':
                pth = '/mnt/data/sunlight/bills/111/bills/s/' + str(num)
            else: 
                pth = '/mnt/data/sunlight/bills/111/bills/hr/' + str(num)

            all_versions = bill_path.get_all_versions(pth)
            #print all_versions
        
            best_date = date(1900,1,1)
            for version in all_versions:
                npth = bill_path.get_bill_path(congress,num,version)
                bill_date = pt.BillPathUtils(npth).bill_date()
                bill_date = datetime.strptime(bill_date,"%Y-%m-%d").date()
                if bill_date > best_date:
                    best_date = bill_date
                    best_version = version 
            PATH_BILL = bill_path.get_bill_path(congress,num,best_version)
            DOC_ID = pt.BillPathUtils(PATH_BILL).get_db_document_id()
            #print DOC_ID,doc_name
            earmarks_10.ix[i[0],'doc_id'] = DOC_ID
        
        elif bvr == "report":
            if hvs == 'senate':
                pth = "/mnt/data/sunlight/congress_reports/111/senate/" + str(num)
            else: 
                pth = "/mnt/data/sunlight/congress_reports/111/house/" + str(num)
              
            all_versions = report_path.get_all_versions(pth)
            rep_path = report_path.get_report_path(congress,hvs,int(num),all_versions[0])
            DOC_ID = pt.ReportPathUtils(rep_path).get_db_document_id()
            earmarks_10.ix[i[0],'doc_id'] = DOC_ID

## exporting the csv ##
earmarks_10.to_csv('2010_db.csv',sep=',',encoding='utf8')                

## imports the new data frame to the database ## 
import psycopg2
import csv, pandas as pd

rows  = []
stuff = pd.read_csv(codecs.open('2010_db.csv','r','utf-8'))
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
cmd = "insert into earmark_documents (earmark_id, document_id,page_number,excerpt)\
 values (%s, %s, %s, %s)"
params = rows
cur = conn.cursor()
#r.execute ("delete from earmark_documents")                                       
cur.executemany(cmd, params)
conn.commit()
conn.close()
