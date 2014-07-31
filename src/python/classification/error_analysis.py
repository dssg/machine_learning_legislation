import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from pprint import pprint
import argparse
import psycopg2
import psycopg2.extras
import codecs 
import logging
from dao.Entity import Entity
from util import prompt, path_tools, amend_earmark

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"


def analyze_entity(entity_id):
    
    if entity_is_earmark(entity_id):
        print "Entity is matched to earmark already, your data might be stale. Ignoring entity %d" %(entity_id)
        return
    if entity_is_negative_example(entity_id):
        print "Entity %d is flagged as negative example, ignoring" %(entity_id)
        return
    entity = Entity(entity_id)
    question = "Does this entity look like an earmark?\n%s\nId: %d\nPath: %s\n" %(entity.entity_inferred_name, entity_id, path_tools.doc_id_to_path(entity.document_id))
    is_earmark = prompt.query_yes_no(question, default="yes")
    if is_earmark:
        question = "Does it match an earmark on OMB website?\n"
        is_match = prompt.query_yes_no(question, default="yes")
        if is_match:
            question = "What is the earmark id?\n"
            earmark_id = prompt.query_number(question)
            amend_earmark.match_earmark_with_entity(earmark_id, entity.id)
        else:
            question = "Are you sure you want to create new earmark?\n"
            if prompt.query_yes_no(question, default="yes"):
                #question = "Please enter a year for the earmark?\n"
                year = path_tools.get_report_year(entity.document_id) #prompt.query_number(question)
                amend_earmark.crete_new_earmark(entity.id, year)
    else:
        # it is not an earmark, now flag it as negative
        question = "Do you want to flag it as negative match?\n"
        if prompt.query_yes_no(question, default="yes"):
            amend_earmark.insert_entity_to_negative_table(entity_id)
            print "Entity %d has been labeled as negative example" %(entity_id)
    print chr(27) + "[2J" # this clears the terminal
                
def entity_is_earmark(entity_id):
    cmd = "select earmark_document_id from earmark_document_matched_entities where matched_entity_id = %s"
    parameters = (entity_id,)
    return check_row_exists(cmd, parameters)

def check_row_exists(cmd, parameters):
    conn = psycopg2.connect(CONN_STRING)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(cmd, parameters)
        result = cur.fetchone()
        if result and len(result) > 0:
            return True
        else:
            return False
    except Exception as ex:
        logging.exception("Error in checking if an entity is an earmark match")
    finally:
        conn.close()
            
def entity_is_negative_example(entity_id):
    cmd = "select entity_id from manual_negative_examples where entity_id = %s"
    parameters = (entity_id,)
    return check_row_exists(cmd, parameters)
    

    
                
            
        
        