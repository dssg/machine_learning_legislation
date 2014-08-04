from matching import get_earmarks, get_earmark_docs, get_entities, bcolors, shinglize, shingle_match, get_earmark
import os
import argparse
import psycopg2
import psycopg2.extras
CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
from prompt import query_yes_no
from random import shuffle
import multiprocessing as mp
import string
import re
import path_tools


def normalize(s):

    s = s.replace("|", "")
    for p in string.punctuation:
        s = s.replace(p, ' ')

    s = re.sub(r'[ ]{2,}', " ", s)

    return s.lower().strip()


AUTO_LABEL_NEGATIVE = 0.1
AUTO_LABEL_POSITIVE = 0.8



def get_jaccard_rank (matches):

    for i in range(len(matches))


def get_instance(earmark_doc_id_pair):
    earmark = earmark_doc_id_pair[0]
    doc_id = earmark_doc_id_pair[1]

    # get all data for this pair

    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor()
    cur.execute("select * from row_matching_labels where document_id = %s and earmark_id = %s", (doc_id, earmark['earmark_id']))

    matches = cur.fetchall()
    matches = [list(m) for m in matches]
    matches = sorted(matches, reverse = true, key = lambda x: x[3])
    get_jaccard_rank(matches)

    for match in matches:
        print match
        print type(match)
    print "\n"

    """short_desc = normalize(earmark['short_description'])
    full_desc = normalize(earmark['full_description'])


    short_desc_shingles = shinglize(short_desc, 2)
    full_desc_shingles = shinglize(full_desc, 2)

    earmark_document_ids = get_earmark_docs(earmark['earmark_id'])

    matches = []

    for earmark_document_id in earmark_document_ids:
        
        doc_entities = get_entities(earmark_document_id, entity_type = 'table_row')
        for doc_entity in doc_entities:
            #for cell in table_row['entity_inferred_name'].split("|")[:-1]


            entity_inferred_name = normalize(doc_entity['entity_inferred_name'])
            entity_inferred_name_shingles = shinglize(entity_inferred_name, 2)

            s_score = shingle_match(entity_inferred_name_shingles, short_desc_shingles)
            f_score = shingle_match(entity_inferred_name_shingles, full_desc_shingles)
            r_score = shingle_match(entity_inferred_name_shingles, recipient_shingles)

            max_score = max(s_score, f_score, r_score)

            matches.append((max_score, doc_entity, earmark_document_id))
            

    matches = sorted(matches, reverse = True)

    print 'Got Matches for Earmark'

    return earmark, matches"""






def main():

    

    conn = psycopg2.connect(CONN_STRING)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("select earmark_id from row_matching_labels where document_id > 0")
    earmarks = cur.fetchall()
    earmarks = set([e[0] for e in earmarks])
    earmarks = [ get_earmark(e) for e in earmarks ]

    earmark_doc_id_pairs = []

    for earmark in earmarks:
        for doc_id in get_earmark_docs(earmark['earmark_id']):
            earmark_doc_id_pairs.append((earmark, doc_id))


    


    #p = mp.Pool(1)
    #results = p.map(get_instance, earmark_doc_id_pairs )

    for earmark_doc_id_pair in earmark_doc_id_pairs:
        get_instance(earmark_doc_id_pair)







if __name__=="__main__":
    main()