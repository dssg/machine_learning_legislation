"""
classification methods
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
from util import wiki_tools
from pprint import pprint
import psycopg2
import logging
import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from sklearn.cross_validation import StratifiedKFold
import scipy
from dao.Entity import Entity
#from dao.Student import Student

from feature_generators import wikipedia_categories_feature_generator, entity_text_bag_feature_generator, simple_entity_text_feature_generator, gen_geo_features,calais_feature_generator, prefix_feature_generator, sponsor_feature_generator
from instance import Instance
from pipe import Pipe
import cPickle as pickle
import multiprocessing as mp
from multiprocessing import Manager


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"


manager = Manager()
global_data= manager.list([])
    
def read_entities_file(path):
    """
    reads a file containing entity ids
    """
    with open(path) as f:
        return [int(line.strip()) for line in f.readlines() if len(line) > 0]


def global_data_append_entity(eid):
    global_data.append(Entity(eid))
    
def global_data_append_instance(entity_target_class_tuple):
    entity = entity_target_class_tuple[0]
    target_class = entity_target_class_tuple[1]
    global_data.append(Instance(entity, target_class))
        
def get_entity_objects(entities, threads = 1):
    global global_data
    global_data = manager.list([])
    pool=mp.Pool(processes=threads)
    pool.map(global_data_append_entity ,entities)
    return global_data[:]
    #return map(lambda eid: Entity(eid) , entities)



    
def get_instances_from_entities(entities, target_class, threads = 1):
    global global_data
    global_data= manager.list([])
    logging.debug("Inside get instances, length of global data after initializaing %d" %(len(global_data)))
    pool=mp.Pool(processes=threads)
    pool.map(global_data_append_instance  ,[(entity, target_class) for entity in  entities])
    logging.debug("Inside get instances, created %d instances with class %d" %(len(global_data), target_class))
    return global_data[:]
    #return map( lambda entity: Instance(entity, target_class), entities )

        


def serialize_instances(instances, outfolder, chunk_size = 1000):
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    for i in range( (len(instances) / chunk_size) +1 ):
        subset = instances[i * chunk_size : (i +1) * chunk_size ]
        if len(subset)>0:
            logging.debug("Serializing part %d" %(i+1))
            pickle.dump(subset, open(os.path.join(outfolder, "instances%d.pickle" %(i+1)),'wb'), -1)
        

def load_instances(infolder):
    """
    infolder: folder containing files that are pickled
    """
    instances = []
    for root, dirs, files in os.walk(infolder, followlinks=True):
        for fname in files:
            if fname.endswith('.pickle'):
                logging.debug("Deserializing part %s" %(fname))
                instances += pickle.load(open(os.path.join(root, fname), 'rb'))
    logging.info("%d instances deserialized"%(len(instances)))
    return instances
            
    
def main():
    parser = argparse.ArgumentParser(description='get pickeled instances')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_serialize = subparsers.add_parser('serialize', help='pickle instances')
    parser_serialize.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_serialize.add_argument('--threads', type=int, default = mp.cpu_count(), help='number of threads to run in parallel')
    parser_serialize.add_argument('--positivefile', required=True, help='file containing entities identified as earmarks')
    parser_serialize.add_argument('--negativefile',  required=True, help='file containing negative example entities')

    parser_add = subparsers.add_parser('add', help='add to pickled instances')
    parser_add.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_add.add_argument('--threads', type=int, default = 1, help='number of threads to run in parallel')





    
    args = parser.parse_args()
    logging.info("pid: " + str(os.getpid()))



        
    if args.subparser_name == "serialize":
        positive_entities = read_entities_file(args.positivefile)
        negative_entities = read_entities_file(args.negativefile)
        logging.info("Pulling entities from database")
        positive_instance = get_instances_from_entities(get_entity_objects(positive_entities, args.threads), 1, args.threads )
        negative_instance = get_instances_from_entities(get_entity_objects(negative_entities, args.threads), 0, args.threads )
        instances = positive_instance + negative_instance
        
        logging.info("Creating pipe")

        feature_generators = [
        #wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(depth = 2, distinguish_levels=False, force=True ),
        entity_text_bag_feature_generator.unigram_feature_generator(force=True),
        #entity_text_bag_feature_generator.bigram_feature_generator(force=True),
        simple_entity_text_feature_generator.simple_entity_text_feature_generator(force=True),
        gen_geo_features.geo_feature_generator(force = True),
        #calais_feature_generator.CalaisFeatureGenerator(force=True)
        ]
        


    elif args.subparser_name == "add":
        logging.info("pid: " + str(os.getpid()))
        instances = load_instances(args.data_folder)
        logging.info("Creating pipe")


        feature_generators = [
        #wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(depth = 2, distinguish_levels=False, force=True ),
        #entity_text_bag_feature_generator.unigram_feature_generator(force=True),
        #entity_text_bag_feature_generator.bigram_feature_generator(force=True),
        #simple_entity_text_feature_generator.simple_entity_text_feature_generator(force=True),
        #gen_geo_features.geo_feature_generator(force = True),
        #calais_feature_generator.CalaisFeatureGenerator(force=True),
        #prefix_feature_generator.PrefixFeatureGenerator(force=True, prefixes = ['O&M', 'for'])
        sponsor_feature_generator.SponsorFeatureGenerator(force = True),
        ]


    pipe = Pipe(feature_generators, instances, num_processes=args.threads)
    logging.info("Pushing into pipe")
    pipe.push_all_parallel()
    logging.info("Start Serializing")
    serialize_instances(pipe.instances, args.data_folder)
    logging.info("Done!")
        
if __name__=="__main__":
    main()
