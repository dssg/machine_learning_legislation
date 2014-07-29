import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from pprint import pprint
import argparse
import psycopg2
import psycopg2.extras
import codecs 
import logging
from dao.Entity import Entity
import prompt
import path_tools

def analyze_entity(entitiy_id):
    entity = Entity(entity_id)
    question = "Does this entity look like an earmark?\n%s" %entity.entity_inferred_name
    is_earmark = prompt.query_yes_no(question, default="yes")
    if is_earmark:
        question = "Does it match an earmark on OMB website?\nPath:%s"%(path_tools.doc_id_to_path(entity.document_id))
        is_match = prompt.query_yes_no(question, default="yes")
        if is_match:
            question = "What is the earmark id?"
            earmark_id = prompt.query_number(question)
            amend_earmark.match_earmark_with_entity(earmark_id, entity.id)
        else:
            question = "Are you sure you want to create new earmark?"
            if prompt.query_yes_no(question, default="yes"):
                question = "Please enter a year for the earmark?"
                year = prompt.query_number(question)
                amend_earmark.crete_new_earmark(entity.id, year)
                
            
        
        