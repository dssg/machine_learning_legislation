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
from feature_generators import wikipedia_categories_feature_generator
from instance import Instance
from pipe import Pipe
import cPickle as pickle
import marshal

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

NO_WIKI_PAGE_FEATURE = "NO_WIKIPEDIA_PAGE_WAS_FOUND"


    
def read_entities_file(path):
    """
    reads a file containing entity ids
    """
    with open(path) as f:
        return [int(line.strip()) for line in f.readlines() if len(line) > 0]
        
def get_entity_objects(entities):
    return [Entity(eid) for eid in entities]
    
def get_instances_from_entities(entities, target_class):
    return [Instance(entity, target_class) for entity in entities]

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
        logging.debug("serializing instance %s" %(subset[-1].__str__()))
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
    
    parser_cv = subparsers.add_parser('cv', help='perform cross validation')
    parser_cv.add_argument('--folds', type=int, required=True, help='number of folds')
    parser_cv.add_argument('--data_folder',  required=True, help='folder containing pickled instances')
    
    parser_transform = subparsers.add_parser('transform', help='transform to svmlight format')
    parser_transform.add_argument('--outfile', required=True, help='path to output file')
    
    parser_pickle = subparsers.add_parser('serialize', help='pickle instances')
    parser_pickle.add_argument('--data_folder', required=True, help='path to output pickled files')
    parser_pickle.add_argument('--threads', type=int, default = 1, help='number of threads to run in parallel')
    parser_pickle.add_argument('--positivefile', required=True, help='file containing entities identified as earmarks')
    parser_pickle.add_argument('--negativefile',  required=True, help='file containing negative example entities')
    #parser.add_argument('--depth', type=int, default = 3,  help='wikipedia category level depth')
    #parser.add_argument('--ignore_levels', action='store_false', default=False, help='distinguish between category levels')
    
    args = parser.parse_args()
    #distinguish_levels = not args.ignore_levels
    
    
    
    
    
    #x, y, space = encode_instances(positive_entities, negative_entities, args.depth, distinguish_levels)
    
    if args.subparser_name =="cv":
        logging.info("Start deserializing")
        pipe = Pipe( instances= load_instances(args.data_folder))
        logging.info("Start creating X, Y")
        x,y,space = pipe.instances_to_scipy_sparse() 
        classify_svm_cv(x, y, args.folds)
        
    elif args.subparser_name == "transform":
        convert_to_svmlight_format(x, y, positive_entities+negative_entities, args.outfile)
        
    elif args.subparser_name == "serialize":
        print "pid: ", os.getpid()
        positive_entities = read_entities_file(args.positivefile)
        negative_entities = read_entities_file(args.negativefile)
        logging.info("Pulling entities from database")
        positive_instance = get_instances_from_entities(get_entity_objects(positive_entities), 1 )
        negative_instance = get_instances_from_entities(get_entity_objects(negative_entities), 0 )
        instances = positive_instance + negative_instance
        logging.info("Creating pipe")
        pipe = Pipe([wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(depth = 3,distinguish_levels=True ),], 
        instances, num_processes=args.threads)
        logging.info("Pushing into pipe")
        #pipe.push_all()
        pipe.push_all_parallel()
        logging.info("Start Serializing")
        serialize_instances(instances, args.data_folder)
        logging.info("Done!")
        
if __name__=="__main__":
    main()
