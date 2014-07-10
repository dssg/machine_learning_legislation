import os, sys
import psycopg2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def toDatabase(rows):
    CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
    earmarks = []
    for row in rows:
        new_earmark = []
        for item in row: 
            if isinstance(item,int):
                new_earmark.append(item)
            else:
                new_item = item.decode('latin1').encode('utf8')
                new_earmark.append(new_item)
        earmarks.append(new_earmark)
  
    conn = psycopg2.connect(CONN_STRING)
    cmd = "insert into earmark_documents (earmark_id, document_id,page_number,excerpt) values (%s, %s, %s, %s)"
    params = rows
    cur = conn.cursor()
    cur.executemany(cmd, earmarks)
    conn.commit()
    conn.close()
