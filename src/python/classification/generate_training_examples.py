import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))

import re
from pprint import pprint
import argparse
import csv
import math
import psycopg2
import psycopg2.extras
import random
import time
import codecs 
from util import wiki_tools
import logging
from dao import Entity
from data_importer import import_entity_wikipedia_mapping

logging.basicConfig(level=logging.INFO)

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"


def get_positive_eamples(year, outfile):
	entity_ids = [entity["matched_entity_id"] for entity in  get_earmark_entities(year)]
	write_entity_ids_to_file(entity_ids, outfile)

def write_entity_ids_to_file(entities, path):
    f = codecs.open(path,'w', 'utf8')
    for entity_id in entities:
		f.write( "%d\n"%(entity_id))
    f.close()
    
def write_entity_text_to_file(entities, path):
    f = codecs.open(path,'w', 'utf8')
    for entity in entities:
		f.write( "%s\n"%(entity))
    f.close()
    
    	
def get_negative_examples(congress, count, outfile):
    entity_ids = [entity["mid"] for entity in  get_candiadte_negative_examples_from_db(congress, count)]
    write_entity_ids_to_file(entity_ids, outfile)
    

def match_entities_to_google(entity_ids):
    for eid in entity_ids:
        entity = Entity.Entity(eid)
        pages = wiki_tools.get_wiki_page_title_google_cse(entity.entity_inferred_name)
        if len(pages)>1:
            import_entity_wikipedia_mapping.import_mapping( [(eid, pages[0],''),] )

def get_earmark_entities(year):
    """
    get entities for doc_id
    """
    conn = psycopg2.connect(CONN_STRING)
    cmd = """select max (earmark_document_matched_entities.matched_entity_id) as matched_entity_id
    from entities, earmark_documents, earmarks, earmark_document_matched_entities 
    where 
    earmark_document_matched_entities.matched_entity_id = entities.id 
    and earmarks.earmark_id = earmark_documents.earmark_id 
    and enacted_year = %s 
    and earmark_document_matched_entities.earmark_document_id = earmark_documents.id
    group by entity_inferred_name"""


    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd, (year,))
    records = cur.fetchall()
    conn.close()
    return records

def get_candiadte_negative_examples_from_db( congress = 111, count=10000 ):
    """
    generates negative examples, randomly, for a given year
    """
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = """
        select mid, entity_inferred_name, random() as r
        from
        (select e.entity_inferred_name, max(e.id) as mid
        from entities as e , documents, congress_meta_document as cmd
        where e.document_id = documents.id 
        and documents.congress_meta_document = cmd.id
        and e.source = 'table'
        and cmd.congress = %s
        and e.id not in (select distinct matched_entity_id from earmark_document_matched_entities)
        group by e.entity_inferred_name
        ) as vu 
        order by r limit %s
        """
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd, (congress, count))
        records = cur.fetchall()
        conn.close()
        return records
    except Exception as ex:
        logging.exception("failed to get negative examples")
    finally:
        conn.close()

def get_uniqe_table_entities():
    """
    gets a list of unique entities from the database
    """
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = """
        select distinct entity_inferred_name from entities
        where source = 'table'
        """
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd)
        records = cur.fetchall()
        return [r['entity_inferred_name'].decode('utf8') for r in records]
    except Exception as ex:
        logging.exception("failed to get negative examples")
    finally:
        conn.close()
        
def match_entities_to_google_by_text(entity_text_list):
    i = 0
    for e_text in entity_text_list:
        i+=1
        if i % 1000 == 0:
            logging.info("Finished %d out of %d" %(i, len(entity_text_list)))
        try:
            pages = wiki_tools.get_wiki_page_title_google_cse(e_text)
            if len(pages)>1:
                import_entity_wikipedia_mapping.import_mapping( [(0, pages[0],e_text),] )
        except Exception as ex:
            logging.exception("Erorr in fetching page for entity")
        
            
    

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='get positive and negative examples')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_positive = subparsers.add_parser('positive', help='create positive examples')
    parser_positive.add_argument('--year', type = int, required=True, help='year for pulling data')
    parser_positive.add_argument('--outfile',  required=True, help='the file to which to write results')
    
    parser_negative = subparsers.add_parser('negative', help='create negative examples')
    parser_negative.add_argument('--congress', type = int, required=True, help='congress number')
    parser_negative.add_argument('--count', type = int, required=True, help='number of negative examples')
    parser_negative.add_argument('--outfile',  required=True, help='the file to which to write results')
    
    parser_all_entities = subparsers.add_parser('alltable', help='gets all table entities')
    parser_all_entities.add_argument('--outfile',  required=True, help='the file to which to write results')
    
    parser_google = subparsers.add_parser('google', help='match entities in file to wikipedia, file contains entity ids')
    parser_google.add_argument('--file',  required=True, help='the file containing list of entity ids')
    
    parser_google_text = subparsers.add_parser('google_text', help='match entities in file to wikipedia, file contains entity text')
    parser_google_text.add_argument('--file',  required=True, help='the file containing list of entity ids')
    
    args = parser.parse_args()
    if args.subparser_name =="positive":
        get_positive_eamples(args.year, args.outfile)
    elif args.subparser_name =="negative":
        get_negative_examples(args.congress, args.count, args.outfile)
    elif args.subparser_name =="google":
        entity_ids = [int(line.strip()) for line in open(args.file).readlines() if len(line) > 1 ]
        match_entities_to_google(entity_ids)
    elif args.subparser_name =="alltable":
        write_entity_text_to_file(get_uniqe_table_entities(), args.outfile)
    elif args.subparser_name =="google_text":
        entities = [line[:-1] for line in codecs.open(args.file,'r','utf8').readlines() if len(line) > 1 ]
        match_entities_to_google_by_text(entities)
    
        
        
        
        
    
    
