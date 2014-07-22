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
from feature_generators import wikipedia_categories_feature_generator, entity_text_bag_feature_generator, simple_entity_text_feature_generator, gen_geo_features
from instance import Instance
from pipe import Pipe
import cPickle as pickle
import multiprocessing as mp
from multiprocessing import Manager


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

NO_WIKI_PAGE_FEATURE = "NO_WIKIPEDIA_PAGE_WAS_FOUND"

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

def convert_to_svmlight_format(X, Y, entities, path):
    """
    converts x and y into svmlight representaiton and write's it to path
    """
    f = open(path,'w')
    previous_row = -1
    values =  zip(X.row, X.col, X.data)
    rows = {}
    for i, j, v in values:
        if not rows.has_key(i):
            rows[i] = []
        rows[i].append((i,j,v))
    
    for i, list_values in rows.iteritems():
        if Y[i]:
            label = 1
        else:
            label = -1
        f.write("%d " %(label))
        for t in list_values:
            f.write("%d:%d " %(t[1]+1, t[2]))
        f.write("#%d\n" %(entities[i]))
    f.close()
        

def classify_svm_cv(X, Y, folds=2):
    C = 1.0
    #X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.4, random_state=0)
    clf = svm.SVC(kernel='linear', C=C)
    #clf = sklearn.ensemble.RandomForestClassifier()
    #s = clf.score(X_test, y_test)
    logging.info("Starting cross validation")
    skf = cross_validation.StratifiedKFold(Y, n_folds=folds)
    scores = cross_validation.cross_val_score(clf, X, Y, cv=skf, n_jobs=3)
    logging.info("Cross validation completed!")
    print scores
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


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
    file_names = os.listdir(infolder)
    for fname in file_names:
        if fname.endswith('.pickle'):
            logging.debug("Deserializing part %s" %(fname))
            instances += pickle.load(open(os.path.join(infolder, fname), 'rb'))
    logging.info("%d instances deserialized"%(len(instances)))
    return instances
            
    
def main():
    parser = argparse.ArgumentParser(description='build classifier')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    
    parser_transform = subparsers.add_parser('transform', help='transform to svmlight format')
    parser_transform.add_argument('--outfile', required=True, help='path to output file')
    
    parser_serialize = subparsers.add_parser('serialize', help='pickle instances')
    parser_serialize.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_serialize.add_argument('--threads', type=int, default = 8, help='number of threads to run in parallel')
    parser_serialize.add_argument('--positivefile', required=True, help='file containing entities identified as earmarks')
    parser_serialize.add_argument('--negativefile',  required=True, help='file containing negative example entities')


    parser_add = subparsers.add_parser('add', help='add to pickled instances')
    parser_add.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_add.add_argument('--threads', type=int, default = 8, help='number of threads to run in parallel')





    
    args = parser.parse_args()
    
    if args.subparser_name == "transform":
        convert_to_svmlight_format(x, y, positive_entities+negative_entities, args.outfile)


        
    elif args.subparser_name == "serialize":
        logging.info("pid: " + str(os.getpid()))
        positive_entities = read_entities_file(args.positivefile)
        negative_entities = read_entities_file(args.negativefile)
        logging.info("Pulling entities from database")
        positive_instance = get_instances_from_entities(get_entity_objects(positive_entities, args.threads), 1, args.threads )
        negative_instance = get_instances_from_entities(get_entity_objects(negative_entities, args.threads), 0, args.threads )
        instances = positive_instance + negative_instance
        
        logging.info("Creating pipe")

        feature_generators = [
        wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(depth = 2, distinguish_levels=False, force=True ),
        entity_text_bag_feature_generator.unigram_feature_generator(force=True),
        entity_text_bag_feature_generator.bigram_feature_generator(force=True),
        simple_entity_text_feature_generator.simple_entity_text_feature_generator(force=True),
        gen_geo_features.geo_feature_generator(force = True),
        ]

        pipe = Pipe(feature_generators, instances, num_processes=args.threads)

        logging.info("Pushing into pipe")
        pipe.push_all_parallel()
        logging.info("Start Serializing")
        serialize_instances(pipe.instances, args.data_folder)
        logging.info("Done!")


    elif args.subparser_name == "add":
        logging.info("pid: " + str(os.getpid()))
        instances = load_instances(args.data_folder)
        logging.info("Creating pipe")


        feature_generators = [
        wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(depth = 2, distinguish_levels=False, force=True ),
        entity_text_bag_feature_generator.unigram_feature_generator(force=True),
        entity_text_bag_feature_generator.bigram_feature_generator(force=True),
        simple_entity_text_feature_generator.simple_entity_text_feature_generator(force=True),
        gen_geo_features.geo_feature_generator(force = True),
        ]


        pipe = Pipe(feature_generators, instances, num_processes=args.threads)
        logging.info("Pushing into pipe")
        pipe.push_all_parallel()
        logging.info("Start Serializing")
        serialize_instances(pipe.instances, args.data_folder)
        logging.info("Done!")
        
if __name__=="__main__":
    main()
