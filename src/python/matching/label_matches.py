from matching import get_earmarks, get_earmark_docs, get_entities, bcolors, shinglize, shingle_match
import os
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
import psycopg2
import psycopg2.extras
CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
from util.prompt import query_yes_no
import multiprocessing as mp
import string
import re
from util import path_tools
import random


def normalize(s):

    s = s.replace("|", "")
    for p in string.punctuation:
        s = s.replace(p, ' ')

    s = re.sub(r'[ ]{2,}', " ", s)

    return s.lower().strip()


AUTO_LABEL_NEGATIVE = 0.05
AUTO_LABEL_POSITIVE = 0.8


def get_matches(earmark):

    short_desc = normalize(earmark['short_description'])
    full_desc = normalize(earmark['full_description'])
    recipient = normalize(earmark['recipient'])


    short_desc_shingles = shinglize(short_desc, 2)
    full_desc_shingles = shinglize(full_desc, 2)
    recipient_shingles = shinglize(recipient, 2)

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

    return earmark, matches




def label_earmark(earmark, matches, conn, cmd, cur):
    
    os.system('clear')

    short_desc = normalize(earmark['short_description'])
    full_desc = normalize(earmark['full_description'])
    recipient = normalize(earmark['recipient'])

    print "Lets Label Earmark: %d" % earmark['earmark_id']
    #print "Recipient: %s" % bcolors.OKGREEN + recipient + bcolors.ENDC
    print "Short Desription: %s" % bcolors.OKGREEN + short_desc + bcolors.ENDC
    print "Full Description: %s" % bcolors.OKGREEN + full_desc + bcolors.ENDC

    consecutive_nos = 0
    labeled = False

    for i in range(len(matches)):
        score = matches[i][0]
        entity = matches[i][1]
        earmark_document_id = matches[i][2]
        entity_id = entity['id']

        query_str = bcolors.WARNING + entity['entity_inferred_name'] + bcolors.ENDC

        #Auto label the rest false
        if consecutive_nos > 10:
            cur.execute(cmd, (earmark['earmark_id'], earmark_document_id, entity_id, score, False))


        elif score >= AUTO_LABEL_POSITIVE:
            print "Auto Lableing: %s" % query_str
            cur.execute(cmd, (earmark['earmark_id'], earmark_document_id, entity_id, score, True))
            labeled = True

        elif score <= AUTO_LABEL_NEGATIVE:
            pass
            #cur.execute(cmd, (earmark['earmark_id'], earmark_document_id, entity_id, score, False))

        else:
            print path_tools.doc_id_to_path(earmark_document_id)
            if query_yes_no(query_str):
                cur.execute(cmd, (earmark['earmark_id'], earmark_document_id, entity_id, score,  True))
                consecutive_nos = 0
            else:
                cur.execute(cmd, (earmark['earmark_id'], earmark_document_id, entity_id, score, False))
                consecutive_nos += 1
            labeled = True

    if not labeled:
        print "no matches above minimum theshold!"
        cur.execute(cmd, (earmark['earmark_id'], -1, -1, 0, False))



    conn.commit()






def main():

    parser = argparse.ArgumentParser(description='Label String Matches')
    parser.add_argument('--year', required=True, type=int, help='which year to match')
    parser.add_argument('--num', type=int, default=5, help='number of examples to check')
    args = parser.parse_args()


    conn = psycopg2.connect(CONN_STRING)
    cmd = """insert into row_matching_labels
            (earmark_id, document_id, entity_id, jaccard, label, year)
            values 
            (%s, %s, %s, %s, %s,""" +str(args.year)+ ")"

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    



    cur.execute("select earmark_id from row_matching_labels")
    labeled_earmarks = cur.fetchall()
    labeled_earmarks = set([e[0] for e in labeled_earmarks])

    all_earmarks = get_earmarks(args.year)

    random.seed(42)
    random.shuffle(all_earmarks)
    unlabeled_earmarks =  []
    count = 0

    for earmark in all_earmarks:
        if earmark['earmark_id'] not in labeled_earmarks:
            unlabeled_earmarks.append(earmark)
            count +=1
        if count > args.num:
            break


    p = mp.Pool(15)
    results = p.map(get_matches, unlabeled_earmarks )



    for r in results:
        label_earmark(r[0], r[1], conn, cmd, cur)

    conn.close()





if __name__=="__main__":
    main()