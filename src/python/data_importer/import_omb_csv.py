import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
import psycopg2
from  earmarks_to_docid0910 import *

def import_rows(rows):
    CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
    earmarks = []
    for row in rows:
        new_earmark = []
        for item in row:
            if isinstance(item,int):
                new_earmark.append(item)
            else:
                try:
                    new_item = item.decode('latin1').encode('utf8')
                    if len(new_item) >= 4096:
                        new_item = new_item[:4050]
                    new_earmark.append(new_item)
                except:
                    new_earmark.append(item)
        earmarks.append(new_earmark)
  
    conn = psycopg2.connect(CONN_STRING)
    cmd = "insert into earmark_documents (earmark_id, document_id, page_number, excerpt) values (%s, %s, %s, %s)"
    params = rows
    cur = conn.cursor()
    cur.executemany(cmd, earmarks)
    conn.commit()
    conn.close()




def main():
    parser = argparse.ArgumentParser(description='populate earmark_documents table from OMB csvs')
    parser.add_argument('--path', required=True, help='path to csv')
    parser.add_argument('--year', type = int, required=True, help='year of OMB file')

    args = parser.parse_args()

    if args.year == 2010:
        rows = csv_extractor_09_10(args.path, args.year)
        import_rows(rows)
    elif args.year == 2009:
        rows = csv_extractor_09_10(args.path, args.year)
        import_rows(rows)
    elif args.year == 2008:
        rows = csv_extractor08(args.path)
    elif args.year == 2005:
        rows = csv_extractor05(args.path)
    else:
        print "This year is not an option"







if __name__=="__main__":
    main()
