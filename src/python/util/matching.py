import os, sys
import codecs
import psycopg2
import psycopg2.extras
import csv
from pprint import pprint
import operator
import string
import itertools
import operator
import path_tools
import re

from nltk import metrics, stem, tokenize
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.tokenize import WhitespaceTokenizer
 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m' 
 
stemmer = stem.PorterStemmer()

THRESHOLD = 0.5
 
def normalize_stem(s):
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])
 
def fuzzy_match(s1, s2):
    return metrics.edit_distance(normalize_stem(s1), normalize_stem(s2)) 

def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, ' ')

    s = re.sub(r'[ ]{2,}', " ", s)

    return s.lower().strip()
    
def tokenize(s):
    return WhitespaceTokenizer().tokenize(s)
    
def shinglize(s, n):
    """
    return size n shingles for the string s
    """
    shingles = set()
    tokens = tokenize(s)
    for i in range(len(tokens) - n + 1):
        shingles.add('_'.join(tokens[i:i+n]))
    return shingles


earmarks_blacklist = set([normalize(line.strip()) for line in open('/mnt/data/sunlight/misc/entities_blacklist.txt').readlines()])

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

def get_earmarks():
    conn = psycopg2.connect(CONN_STRING)
    columns = ["earmark_id", "full_description", "short_description", "recipient"]
    cmd = "select "+", ".join(columns)+" from earmarks where enacted_year = 2008"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd)
    earmarks = cur.fetchall()
    conn.close()
    return earmarks

    #print "number of earmarks", len(earmarks)


def get_earmark_docs(earmark_id):
    """
    given earmark id, return list of all docs that map to this earmark
    """
    conn = psycopg2.connect(CONN_STRING)
    columns = ["document_id"]
    cmd = "select "+", ".join(columns)+" from earmark_documents where earmark_id = %s"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd, (earmark_id,))
    docs = cur.fetchall()
    conn.close()
    return {doc['document_id'] for doc in docs}


def get_entities(doc_id):
    """
    get entities for doc_id
    """
    conn = psycopg2.connect(CONN_STRING)
    columns = ["id", "entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name"]
    cmd = "select "+", ".join(columns)+" from entities where document_id = %s and entity_type in ('Organization', 'Facility', 'Company', 'table_entity')"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd, (doc_id,))
    records = cur.fetchall()
    conn.close()
    return records


def string_match(entity, text):
    return entity in text


def find_best_string_match(matches):
    """
    matches: set of entities
    """
    diff = [x for x in list(matches)  ]
    sorted_desc_entities = sorted(diff, key=len, reverse=True)
    print   sorted_desc_entities[:10] 
    if len(sorted_desc_entities) > 0:
        return sorted_desc_entities[0]
    
def shingle_match(entity_shingles, text_shingles):
    #print entity_shingles, text_shingles
    return (len(entity_shingles.intersection(text_shingles)) * 1.0) / max(1,len(entity_shingles.union(text_shingles)) )
    

        
def find_best_shingle_matches(matches):
    """
    matches: list of tuples, such that tuple is (entity, score)
    """
    best_matches = {}
    for doc_id in matches.keys():
        sorted_desc_entities = sorted(matches[doc_id], key=operator.itemgetter(0), reverse=True)
        if len(sorted_desc_entities) > 0:
            best_matches[doc_id] =  sorted_desc_entities[0]
    return best_matches

def update_earmark_offsets (earmark_id, matches):
    """
    If matching was succesfull, update the inferred_offest in DB"
    """
    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor()
    for doc_id in matches.keys():
        offset = matches[doc_id][1]['entity_offset']
        length = matches[doc_id][1]['entity_length']
        entity_id = matches[doc_id][1]['id']
        print (offset, length, entity_id, earmark_id, doc_id)
        cmd = "update earmark_documents set inferred_offset = %d, ingerred_length = %d, matched_entity_id = %d where earmark_id = %d and document_id = %d" % (offset, length, entity_id, earmark_id, doc_id)

        cur.execute(cmd)
    conn.commit()
    conn.close()



def main():
    earmarks = get_earmarks()
    num_matched = 0
    num_failed = 0
    num_matched_table = 0
    num_matched_calais = 0
    for earmark in earmarks:
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
            #normalized_excerpt = normalize(doc['excerpt'])
            #excerpt_shingles = shinglize(normalized_excerpt, 2)
            print doc_id
            print path_tools.doc_id_to_path(doc_id)
            doc_entities = get_entities(doc_id)
            for doc_entity in doc_entities:
                normalized_entity_text = normalize(doc_entity['entity_text'])
                normalized_entity_inferred_name = normalize(doc_entity['entity_inferred_name'])
                if normalized_entity_text in earmarks_blacklist or \
                normalized_entity_inferred_name in earmarks_blacklist:
                    continue
                    
                e_text_shingles = shinglize(normalized_entity_text, 2)
                e_name_shingles = shinglize(normalized_entity_inferred_name, 2)
                
                lst_entities = [e_text_shingles, e_name_shingles]
                lst_txt = [fd_shingles, sd_shingles, r_shingles] #excerpt_shingles
                
                
                
                for pair in itertools.product(lst_entities, lst_txt):
                    score = shingle_match(*pair)
                    if score > THRESHOLD:

                        matches[doc_id].append( (score, doc_entity))


    
                
        best_matches = find_best_shingle_matches(matches)

        for t in best_matches.values():
            if t[1]['entity_type'] == "table_entity":
                num_matched_table += 1
            else:
                num_matched_calais += 1


        #update_earmark_offsets(earmark['earmark_id'], best_matches)
        if len(best_matches)>0:
            num_matched+=1
            print bcolors.OKGREEN +"Earmark %d with description %s matched:\n ===" %(earmark['earmark_id'] ,earmark['short_description'])
            pprint(best_matches) 
            print "\n\n"+bcolors.ENDC  
        else:
            num_failed+=1
            print bcolors.WARNING + "No match found! for earmark %d,  %s" %(earmark['earmark_id'], earmark['short_description']) + bcolors.ENDC   
        
        print "Matched: %d, Failed %d" %(num_matched, num_failed)
        print "Table: %d, Calais %d" %(num_matched_table, num_matched_calais)


if __name__=="__main__":
    main()

