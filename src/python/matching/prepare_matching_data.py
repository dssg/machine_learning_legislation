import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse

import os
import psycopg2
import psycopg2.extras
CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
import multiprocessing as mp
import string
import re

import logging
from classification.pipe import Pipe
from classification.blocks_pipe import BlocksPipe
from classification.instances_grouper import InstancesGrouper

from classification.prepare_earmark_data import  serialize_instances, load_instances

from matching.feature_generators.jaccard_feature_generator import JaccardFeatureGenerator
from matching.feature_generators.ranking_feature_generator import RankingFeatureGenerator
from matching.feature_generators.difference_feature_generator import DifferenceFeatureGenerator
from matching.feature_generators.infix_feature_generator import InfixFeatureGenerator
from matching.feature_generators.table_feature_generator import TableFeatureGenerator

from matching.matching_util import *


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
MIN = 0.1


def get_earmarks_from_db():

    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select distinct earmark_id from row_matching_labels where document_id > %s", (MIN, ))
    earmarks = cur.fetchall()
    conn.close()
    return [e[0] for e in earmarks]

def get_entities_from_db():

    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select distinct entity_id from row_matching_labels where document_id > 0 and jaccard > %s", (MIN, ))
    entities = cur.fetchall()
    conn.close()
    return [e[0] for e in entities]


def get_earmark_entity_tuples():
    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor()
    cur.execute("select entity_id, earmark_id, label from row_matching_labels where document_id > 0 and jaccard > %s", (MIN, ))
    earmark_entity_tuples =  cur.fetchall()
    conn.close()
    return earmark_entity_tuples
    

def main():
    parser = argparse.ArgumentParser(description='get pickeled instances')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')

    parser_serialize = subparsers.add_parser('serialize', help='pickle instances')
    parser_serialize.add_argument('--data', required=True, help='path to output pickled files')
    parser_serialize.add_argument('--threads', type=int, default = 1 , help='number of threads to run in parallel')

    parser_add = subparsers.add_parser('add', help='add to pickled instances')
    parser_add.add_argument('--data', required=True, help='path to output pickled files')
    parser_add.add_argument('--threads', type=int, default = 1 , help='number of threads to run in parallel')

    args = parser.parse_args()
    logging.info("pid: " + str(os.getpid()))

        
    if args.subparser_name == "serialize":
        
        earmark_ids = list(get_earmarks_from_db())
        logging.info("Got %d earmarks" % len(earmark_ids))

        entity_ids = list(get_entities_from_db())
        logging.info("Got %d entities" % len(entity_ids))


        instances = get_matching_instances(entity_ids, earmark_ids, get_earmark_entity_tuples(), args.threads)
        logging.info("Got %d instances" % len(instances))

    
        logging.info("Creating pipe")
        fgs = [
            JaccardFeatureGenerator(),
            InfixFeatureGenerator(), 
            TableFeatureGenerator(),
        ]
        pipe = Pipe(fgs, instances, num_processes=args.threads)
        logging.info("Pushing into pipe")
        pipe.push_all_parallel()



        # group by earmark and document:
        pairs = [("JACCARD_FG","JACCARD_FG_max_inferred_name_jaccard" ), ("JACCARD_FG", "JACCARD_FG_max_cell_jaccard")]
        fgs = [
            RankingFeatureGenerator(pairs = pairs),
            DifferenceFeatureGenerator(pairs = pairs)
        ]
        grouper = InstancesGrouper(['earmark_id', 'document_id'])
        pipe = BlocksPipe(grouper, fgs, pipe.instances, num_processes=args.threads )
        pipe.push_all_parallel()



        #Serialize
        logging.info("Start Serializing")
        serialize_instances(pipe.instances, args.data)
        logging.info("Done!")



    elif args.subparser_name == "add":
        instances = load_instances(args.data)
        logging.info("Creating pipe")


        fgs = [
            InfixFeatureGenerator()
        ]

        pipe = Pipe(fgs, instances, num_processes=args.threads)
        logging.info("Pushing into pipe")
        pipe.push_all_parallel()
        


        #Serialize
        logging.info("Start Serializing")
        serialize_instances(pipe.instances, args.data)
        logging.info("Done!")


    
        
if __name__=="__main__":
    main()
