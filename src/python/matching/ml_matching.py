import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import codecs
import psycopg2
import psycopg2.extras
import csv
from pprint import pprint
import operator
import string
import itertools
import operator
import util.path_tools
import re
import argparse
import util.amend_earmark
import logging

import multiprocessing as mp

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m' 
 
stemmer = stem.PorterStemmer()

MIN = 0.1
 


CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

def get_doc_ids_from_db():

    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select distinct document_id from earmark_documents")
    docs = cur.fetchall()
    conn.close()
    return [d[0] for d in docs]


def get_earmark_ids_in_doc(doc_id):
    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select distinct earmark_id_id from earmark_documents where document_id = %s", (doc_id, ))
    earmarks = cur.fetchall()
    conn.close()
    return [e[0] for e in docs earmarks]



def get_entity_ids_in_doc_from_db(doc_id):
    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select distinct entity_id from entities where document_id = %s and entity_type = table_row", (MIN, doc_id))
    entities = cur.fetchall()
    conn.close()
    return [e[0] for e in entities]


def get_earmark_entity_tuples(earmark_ids, entity_ids):
    earmark_entity_tuples = []
    for entity_id in entity_ids:
        for earmark_id in earmark_ids
            earmark_entity_tuples.append((entity_id, earmark_id, 1))
    return earmark_entity_tuples

   




def record_matching (earmark_id, matches):
    """
    If matching was succesfull, update the inferred_offest in DB"
    """
    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor()
    for doc_id in matches.keys():
        for d in matches[doc_id]: 
            offset = d[1]['entity_offset']
            length = d[1]['entity_length']
            entity_id = d[1]['id']
            earmark_document_id = amend_earmark.check_earmark_doc_match(earmark_id, entity_id)
            cmd = """insert into earmark_document_matched_entities 
            (earmark_document_id,matched_entity_id ,manual_match)
            select %d, %d, False
            WHERE NOT EXISTS 
            (SELECT 1 FROM earmark_document_matched_entities WHERE earmark_document_id=%d and matched_entity_id = %d );
            """ %(earmark_document_id,entity_id, earmark_document_id,  entity_id  )
            logging.debug("Inserting for entity %d and earmark %d" %(entity_id, earmark_id))
            cur.execute(cmd)
    conn.commit()
    conn.close()


def process_earmark(earmark_update_pair):
    earmark = earmark_update_pair[0]
    update = earmark_update_pair[1]
    

    out_str = []

    normalized_short_desc = normalize(earmark['short_description'])
    normalized_full_desc = normalize(earmark['full_description'])
    normalized_recipient = normalize(earmark['recipient'])
    fd_shingles = shinglize(normalized_full_desc, 2)
    sd_shingles = shinglize(normalized_short_desc, 2)
    r_shingles = shinglize(normalized_recipient, 2)


    desc_short_matches=set()
    excerpt_matches =set()
    desc_full_matches =set()
    matches = {}
    docs = get_earmark_docs(earmark['earmark_id'])
    for doc_id in docs:
        matches[doc_id] = []
        out_str.append(str(doc_id))
        #print path_tools.doc_id_to_path(doc_id)
        doc_entities = get_entities(doc_id)
        for doc_entity in doc_entities:
            #normalized_entity_text = normalize(doc_entity['entity_text'])
            normalized_entity_inferred_name = normalize(doc_entity['entity_inferred_name'])
            #if normalized_entity_text in earmarks_blacklist or \
            if normalized_entity_inferred_name in earmarks_blacklist:
                continue
            #e_text_shingles = shinglize(normalized_entity_text, 2)
            e_name_shingles = shinglize(normalized_entity_inferred_name, 2)
            
            #lst_entities = [e_text_shingles, e_name_shingles]
            lst_entities = [e_name_shingles,]
            lst_txt = [fd_shingles, sd_shingles, r_shingles] #excerpt_shingles
            
            
            
            for pair in itertools.product(lst_entities, lst_txt):
                score = shingle_match(*pair)
                if score > THRESHOLD:

                    matches[doc_id].append( (score, doc_entity))


            
    best_matches = find_best_shingle_matches(matches)

    if update:
        update_earmark_offsets(earmark['earmark_id'], best_matches)

    if len(best_matches)>0:
        ret=1
        out_str.append( bcolors.OKGREEN +"Earmark %d with description %s matched:\n ===" %(earmark['earmark_id'] ,earmark['short_description']))
        out_str.append( str(best_matches)) 
        out_str.append( "\n\n"+bcolors.ENDC ) 
    else:
        ret=0
        out_str.append( bcolors.WARNING + "No match found! for earmark %d,  %s" %(earmark['earmark_id'], earmark['short_description']) + bcolors.ENDC )  
    print "Done"
    return out_str, ret
    



def main():

    parser = argparse.ArgumentParser(description='Match entities to OMB')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')

    parser_m = subparsers.add_parser('match', help='transform to svmlight format')
    parser_d = subparsers.add_parser('debug', help='transform to svmlight format')


    
    
    parser_m.add_argument('--year', required=True, type=int, help='which year to match')
    parser_m.add_argument('--threads', type=int, default = 8, help='number of threads to run in parallel')
    parser_m.add_argument('--update', action='store_true',default = False,  help = 'record matches in db')
    parser_m.add_argument('--num', type=int, default=-1, help='number of examples to check')


    parser_d.add_argument('--earmark', required = True, type = int)


    args = parser.parse_args()
    
    print "Process id: ", os.getpid()

    if args.subparser_name == "match":

        update = args.update

        earmarks = get_earmarks(args.year)
        if args.num > -1:
            earmarks = earmarks[:args.num]
        p = mp.Pool(args.threads)
        results = p.map(process_earmark, [(earmark, update) for earmark in earmarks])

        matches = [ t[1] for t in results]
        for r in results:
            print "\n".join(r[0])
            print "\n"

        accuracy = sum(matches)/float(len(matches))

        print "Accuracy: ", accuracy

    else:
        print process_earmark((get_earmark(args.earmark), True, False))


    


if __name__=="__main__":

    main()

