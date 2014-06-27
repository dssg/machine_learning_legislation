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
 
def normalize_stem(s):
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])
 
def fuzzy_match(s1, s2):
    return metrics.edit_distance(normalize_stem(s1), normalize_stem(s2)) 

def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, '')
 
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
    columns = ["earmark_id", "full_description", "short_description"]
    cmd = "select "+", ".join(columns)+" from earmarks where enacted_year = 2010"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd)
    earmarks = cur.fetchall()
    return earmarks
    #print "number of earmarks", len(earmarks)


def get_earmark_doc_ids(earmark_id):
    """
    given earmark id, return list of all docs that map to this earmark
    """
    conn = psycopg2.connect(CONN_STRING)
    columns = ["document_id","excerpt"]
    cmd = "select "+", ".join(columns)+" from earmark_documents where earmark_id = %s"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd, (earmark_id,))
    docs = cur.fetchall()
    return docs


def get_entities(doc_id):
    """
    get entities for doc_id
    """
    conn = psycopg2.connect(CONN_STRING)
    columns = ["entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name"]
    cmd = "select "+", ".join(columns)+" from entities where document_id = %s and entity_type in ('Organization', 'Facility', 'Company', 'table_entity')"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(cmd, (doc_id,))
    records = cur.fetchall()
    return records


def match(entity, text):
    return entity in text
    
def match_jaccard(entity_shingles, text_shingles):
    #print entity_shingles, text_shingles
    return (len(entity_shingles.intersection(text_shingles)) * 1.0) / max(1,len(entity_shingles.union(text_shingles)) )
    
def find_best_match(matches):
    """
    matches: set of entities
    """
    diff = [x for x in list(matches)  ]
    sorted_desc_entities = sorted(diff, key=len, reverse=True)
    print   sorted_desc_entities[:10] 
    if len(sorted_desc_entities) > 0:
        return sorted_desc_entities[0]
        
def find_best_match_with_score(matches):
    """
    matches: list of tuples, such that tupleis (entity, score)
    """
    sorted_desc_entities = sorted(matches, key=operator.itemgetter(1), reverse=True)
    return sorted_desc_entities[:5]


def main():
    earmarks = get_earmarks()
    num_matched = 0
    num_failed = 0
    for e in earmarks:
        normalized_short_desc = normalize(e['short_description'])
        normalized_full_desc = normalize(e['full_description'])
        fd_shingles = shinglize(normalized_full_desc, 2)
        sd_shingles = shinglize(normalized_short_desc, 2)
        desc_short_matches=set()
        excerpt_matches =set()
        desc_full_matches =set()
        matches = []
        doc_ids = get_earmark_doc_ids(e['earmark_id'])
        for doc in doc_ids:
            #normalized_excerpt = normalize(doc['excerpt'])
            #excerpt_shingles = shinglize(normalized_excerpt, 2)
            doc_entities = get_entities(doc['document_id'])
            for doc_e in doc_entities:
                normalized_entity_text = normalize(doc_e['entity_text'])
                normalized_entity_inferred_name = normalize(doc_e['entity_inferred_name'])
                if normalized_entity_text in earmarks_blacklist or \
                normalized_entity_inferred_name in earmarks_blacklist:
                    continue
                    
                e_text_shingles = shinglize(normalized_entity_text, 2)
                e_name_shingles = shinglize(normalized_entity_inferred_name, 2)
                
                lst_entities = [e_text_shingles, e_name_shingles]
                lst_txt = [fd_shingles, sd_shingles ] #excerpt_shingles
                
                
                
                for pair in itertools.product(lst_entities, lst_txt):
                    score = match_jaccard(*pair)
                    if score > 0:
                        matches.append( (pair[0], score) )
                    
                
                
                # excerpt
                """
                if match(normalized_entity_text, normalized_excerpt):
                    excerpt_matches.add(normalized_entity_text)
                if match(normalized_entity_inferred_name, normalized_excerpt):
                    excerpt_matches.add(normalized_entity_inferred_name)
                # short description
                if match(normalized_entity_text, normalized_short_desc):
                    desc_short_matches.add(normalized_entity_text)
                if match(normalized_entity_inferred_name, normalized_short_desc):
                    desc_short_matches.add(normalized_entity_inferred_name)
                # long description
                if match(normalized_entity_text, normalized_full_desc):
                    desc_full_matches.add(normalized_entity_text)
                if match(normalized_entity_inferred_name, normalized_full_desc):
                    desc_full_matches.add(normalized_entity_inferred_name)
               """
        #all_matches = desc_short_matches.union(excerpt_matches).union(desc_full_matches)  
        #pprint( all_matches )         
        best_match = find_best_match_with_score(matches)
        if best_match:
            num_matched+=1
            print bcolors.OKGREEN +"Earmark %d with description %s matched:\n === %s" %(e['earmark_id'] ,e['short_description'],best_match) + bcolors.ENDC   
        else:
            num_failed+=1
            print bcolors.WARNING + "No match found! for earmark %d,  %s" %(e['earmark_id'], e['short_description']) + bcolors.ENDC   
        
        print "Matched: %d, Failed %d" %(num_matched, num_failed)


if __name__=="__main__":
    main()

