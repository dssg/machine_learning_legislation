import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))

import re
from pprint import pprint
import argparse
import csv
import math
import psycopg2
import psycopg2.extras

from util import wiki_tools

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"


def get_positive_eamples(year):
	entities =get_earmark_entities(year)
	for entity in entities:
		 pages = wiki_tools.get_wiki_page_title_google(entity['entity_inferred_name'])
		 if len(pages)>1:
		 		hierarchy = wiki_tools.get_category_hierarchy(pages[0], 3)
		 		pprint(hierarchy)





def get_earmark_entities(year):
    """
    get entities for doc_id
    """
    conn = psycopg2.connect(CONN_STRING)
    columns = ["matched_entity_id", "entity_inferred_name"]
    cmd = "select "+", ".join(columns)+" from entities, earmark_documents, earmarks where \
     matched_entity_id = entities.id and earmarks.earmark_id = earmark_documents.earmark_id and enacted_year = %s"
    print cmd
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd, (year,))
    records = cur.fetchall()
    conn.close()
    return records







if __name__=="__main__":
    parser = argparse.ArgumentParser(description='get positive examples')
    parser.add_argument('--year', type = int, required=True, help='year for pulling data')
    args = parser.parse_args()
    get_positive_eamples(args.year)
