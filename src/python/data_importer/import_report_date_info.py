import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from util import path_tools, configuration
import psycopg2
import datetime
import argparse
import logging
from util import path_tools

CONN_STRING = configuration.get_connection_string()

def get_documents_with_null_date():
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = "select id from documents where date is null"
        cur = conn.cursor()
        cur.execute(cmd)
        return [record[0] for record in cur.fetchall()]
    except Exception as exp:
        logging.exception("Couldn't get document ids")
    finally:
        conn.close()

def update_document_date(document_id):
    conn = psycopg2.connect(CONN_STRING)
    try:
        doc_date = path_tools.get_report_date(document_id)
        parts = [int(p) for p in doc_date.split('-')]
        cmd = "update documents set date = %s where id = %s"
        cur = conn.cursor()
        cur.execute(cmd, ( datetime.date(parts[0],parts[1],parts[2]), document_id))
        conn.commit()
    except Exception as exp:
        conn.rollback()
        logging.exception("Couldn't get document ids")
    finally:
        conn.close()

def main():
    doc_ids = get_documents_with_null_date()
    for i in range(len(doc_ids)):
        if i % 100 ==0:
            print i
        update_document_date(doc_ids[i])

if __name__=="__main__":
    main()
