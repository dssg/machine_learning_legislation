import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from pprint import pprint
import argparse
import psycopg2
import psycopg2.extras
import codecs 
import logging
from dao.Entity import Entity

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

def check_earmark_doc_match(earmark_id, entity_id):
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = """
        select earmark_documents.id from 
        earmark_documents, entities
        where entities.document_id = earmark_documents.document_id
        and earmark_documents.earmark_id = %s
        and entities.id = %s
        """
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd, (earmark_id, entity_id))
        records = cur.fetchone()
        if records and len(records) > 0:
            return records[0]
        else:
            return -1 # indicating not found
    except Exception as ex:
        logging.exception("Failed to check earmark %d and entity %d" %(earmark_id, entity_id))
    finally:
        conn.close()
        
def match_earmark_with_entity(earmark_id, entity_id):
    conn = psycopg2.connect(CONN_STRING)
    try:
        earmark_to_doc_id = check_earmark_doc_match(earmark_id, entity_id)
        if earmark_to_doc_id > -1:
            cmd = """
            insert into earmark_document_matched_entities
            (earmark_document_id, matched_entity_id, manual_match)
            values 
            (%s, %s, True)
            """
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(cmd, (earmark_to_doc_id, entity_id ))
            conn.commit()
        else:
            logging.error("Earmark id %d is not matched to the document containing entity %d, please create new earmark first" %(earmark_id, entity_id))
    except Exception as ex:
        logging.exception("Failed to check earmark %d and entity %d" %(earmark_id, entity_id))
    finally:
        conn.close()
        
def get_max_earmark_id():
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = """
        select max(earmark_id) from earmarks
        """
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd)
        records = cur.fetchone()
        return records[0]
    except Exception as ex:
        logging.exception("Failed to get max earmark id")
    finally:
        conn.close()

def crete_new_earmark_doc_matching(earmark_id, document_id):
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = """
        insert into earmark_documents
        (earmark_id, document_id) 
        values(%s, %s)
        """
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd, (earmark_id, document_id ))
        conn.commit()
    except Exception as ex:
        logging.exception("Failed to create earmark %d to doc %d matching" %(earmark_id, document_id))
        conn.rollback()
    finally:
        conn.close()
    
        
def crete_new_earmark(entity_id, year):
    conn = psycopg2.connect(CONN_STRING)
    try:
        earmark_id = get_max_earmark_id() + 1
        entity = Entity(entity_id)
        cmd = """
        insert into earmarks
        (earmark_id, short_description, enacted_year, manual_earmark) 
        values (%s, %s, %s ,True)
        """
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd, (earmark_id, entity.entity_inferred_name , year))
        conn.commit()
        logging.debug("Creted earmark")
        crete_new_earmark_doc_matching(earmark_id, entity.document_id)
        logging.debug("created earmark to doc matching")
        match_earmark_with_entity(earmark_id, entity_id)
    except Exception as ex:
        logging.exception("Failed to create new earmark with entity %d" %(entity_id))
        conn.rollback()
    finally:
        conn.close()
    
def main():
    parser = argparse.ArgumentParser(description='amend earmarks and their matching')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_check = subparsers.add_parser('check', help='checks if document is linked with earmark')
    parser_check.add_argument('--earmark', type = int, required=True, help='earmark id')
    parser_check.add_argument('--entity', type = int,  required=True, help='entity id')
    
    parser_match = subparsers.add_parser('match', help='add matching from earmark to entity')
    parser_match.add_argument('--earmark', type = int, required=True, help='earmark id')
    parser_match.add_argument('--entity', type = int, required=True, help='entity id')
    
    parser_create_earmark = subparsers.add_parser('create', help='creates new earmark for an entity')
    parser_create_earmark.add_argument('--entity', type=int,  required=True, help='the entity id for which a new earmark will be created')
    parser_create_earmark.add_argument('--year', type = int,  required=True, help='enacted year')
    
        
    args = parser.parse_args()
    
    if args.subparser_name =="check":
        matched_id = check_earmark_doc_match(args.earmark, args.entity)
        if matched_id > -1:
            print "Matched at id %d" %( matched_id)
        else:
            print "FAILED TO MATCH!" 
    elif args.subparser_name =="match":
        match_earmark_with_entity(args.earmark, args.entity)
    elif args.subparser_name =="create":
        crete_new_earmark(args.entity, args.year)
    
if __name__=="__main__":
    main()