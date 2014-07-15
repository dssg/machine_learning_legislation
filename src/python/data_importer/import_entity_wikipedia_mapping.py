"""
imports the mapping of entities to wikipedia pages
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import psycopg2
import datetime
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

def import_mapping(path):
    """
    given tab delimeted file of format earmark_id tab page_title
    it's imported to the database
    """
    lines = [line.strip().split('\t') for line in open(path,'r').readlines() if len(line.strip()) > 1]
    params = [(int(line[0]), line[1]) for line in lines ]
    conn = psycopg2.connect(CONN_STRING)
    try:
        cur = conn.cursor()
        cmd = 'insert into entity_wikipedia_page (entity_id, wikipedia_page) values(%s,%s)'
        cur.executemany(cmd, params)
        conn.commit()
    except Exception as ex:
        conn.rollback()
        logging.exception("failed to import!")
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='Import wikipedia matches to the database using file containing tab delimated entity_id and page title ')
    parser.add_argument('--file', required=True, help='path to the file containing the mapping')
    args = parser.parse_args()
    import_mapping(args.file)
        
if __name__=="__main__":
    main()