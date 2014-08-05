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
from dao.Entity import Entity
from dao.Earmark import Earmark
from classification import instance
import logging
from multiprocessing import Manager
from classification.pipe import Pipe
from classification.prepare_earmark_data import  serialize_instances
from classification.feature_generators.shinglizer import ShinglesGenerator
from entity_attributes import EntityAttributes
from earmark_attributes import EarmarkAttributes




logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
MIN = 0.1



manager = Manager()

def get_earmarks_from_db():

    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select earmark_id from row_matching_labels where document_id > %s", (MIN, ))
    earmarks = cur.fetchall()
    conn.close()
    return set([e[0] for e in earmarks])

def get_entities_from_db():

    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select distinct entity_id from row_matching_labels where document_id > 0 and jaccard > %s", (MIN, ))
    entities = cur.fetchall()
    conn.close()
    return set([e[0] for e in entities])



def get_entity_attributes(entity_id):
    return (entity_id, EntityAttributes(Entity(entity_id)))


def get_earmark_attributes(earmark_id):
    return (earmark_id, EarmarkAttributes(Earmark(earmark_id)))


def get_matching_tuples(entity_daos, earmark_daos):
    conn = psycopg2.connect(CONN_STRING)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select earmark_id, entity_id, label from row_matching_labels where document_id > 0 and jaccard > %s", (MIN, ))

    matching_tuples = []

    matches = cur.fetchall()
    for m in matches:
        matching_tuple = [entity_daos[m['entity_id']], earmark_daos[m['earmark_id']], m['label']]
        matching_tuples.append(matching_tuple)

    conn.close()
    return matching_tuples


def get_instance(matching_tuple):
    i = instance.Instance(target_class = matching_tuple[2])
    i.attributes['entity'] =  matching_tuple[0]
    i.attributes['earmark']=  matching_tuple[1]
    return i
    #return instance.Instance(entity = matching_tuple[0], earmark = matching_tuple[1], target_class = matching_tuple[2])


def main():
    parser = argparse.ArgumentParser(description='get pickeled instances')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    

    parser_serialize = subparsers.add_parser('serialize', help='pickle instances')
    parser_serialize.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_serialize.add_argument('--threads', type=int, default = mp.cpu_count(), help='number of threads to run in parallel')

    parser_add = subparsers.add_parser('add', help='add to pickled instances')
    parser_add.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_add.add_argument('--threads', type=int, default = mp.cpu_count(), help='number of threads to run in parallel')

    args = parser.parse_args()
    logging.info("pid: " + str(os.getpid()))

        
    if args.subparser_name == "serialize":

        
        
        earmark_ids = list(get_earmarks_from_db())
        entity_ids = list(get_entities_from_db())



        p = mp.Pool(args.threads)
        earmark_attributes = dict(p.map(get_earmark_attributes, earmark_ids))
        logging.info("Got %d Earmarks" % len(earmark_attributes))



        p = mp.Pool(args.threads)
        entity_attributes = dict(p.map(get_entity_attributes, entity_ids))
        logging.info("Got %d entities" % len(entity_attributes))


        matching_tuples = get_matching_tuples(entity_attributes, earmark_attributes)

        logging.info("Got %d Matching Tuples" % len(matching_tuples))


        instances = []
        for m in matching_tuples:
            instances.append(get_instance(m))



        
        logging.info("Creating pipe")

        feature_generators = [
        
        ]
        


    elif args.subparser_name == "add":
        instances = load_instances(args.data_folder)
        logging.info("Creating pipe")


        feature_generators = [
        ]


    pipe = Pipe(feature_generators, instances, num_processes=args.threads)
    logging.info("Pushing into pipe")
    pipe.push_all_parallel()
    logging.info("Start Serializing")
    serialize_instances(pipe.instances, args.data_folder)
    logging.info("Done!")
        
if __name__=="__main__":
    main()
