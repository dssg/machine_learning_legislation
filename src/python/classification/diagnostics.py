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
import pickle
import marshal
from sklearn import svm, grid_search
import classifier
from sklearn.cross_validation import StratifiedShuffleSplit

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')



def classify_svm_cv(X, Y, folds=2):
    C = 1.0
    clf = svm.SVC(kernel='linear', C=C)
    #clf = sklearn.ensemble.RandomForestClassifier()
    logging.info("Starting cross validation")
    skf = cross_validation.StratifiedKFold(Y, n_folds=folds)
    scores = cross_validation.cross_val_score(clf, X, Y, cv=skf, n_jobs=3)
    logging.info("Cross validation completed!")
    print scores
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def do_grid_search(X, Y, folds = 5):

    param_grid = {'C': [0.1, 1, 10, 100, 1000], 'kernel': ['linear']}
    svr = svm.SVC()
    strat_cv = cross_validation.StratifiedKFold(Y, n_folds=folds)
    clf = grid_search.GridSearchCV(cv  = strat_cv, estimator = svr, param_grid  =param_grid, scoring = 'f1')
    clf.fit(X, Y)

    print("Grid scores on development set:")
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r"
              % (mean_score, scores.std() / 2, params))

    print "\n"


    print("Best parameters set found on development set:")
    best_parameters, score, _ = max(clf.grid_scores_, key=lambda x: x[1])
    print best_parameters

    


    print("Detailed classification report:")
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")

    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))
    print()






def serialize_instances(instances, outfile):
    pickle.dump(instances, open(outfile,'wb'))
    
def main():
    parser = argparse.ArgumentParser(description='build classifier')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_cv = subparsers.add_parser('cv', help='perform cross validation')
    parser_cv.add_argument('--folds', type=int, required=True, help='number of folds')
    parser_cv.add_argument('--file',  required=True, help='file to pickled instances')


    parser_grid = subparsers.add_parser('grid', help='perform CV grid search')
    parser_grid.add_argument('--folds', type=int, required=False, help='number of folds')
    parser_grid.add_argument('--file',  required=True, help='file to pickled instances')
    
    parser_pickle = subparsers.add_parser('serialize', help='pickle instances')
    parser_pickle.add_argument('--outfile', required=True, help='path to output pickled file')
    parser_pickle.add_argument('--positivefile', required=True, help='file containing entities identified as earmarks')
    parser_pickle.add_argument('--negativefile',  required=True, help='file containing negative example entities')
    args = parser.parse_args()

    print "parsed"
    
    
    #x, y, space = encode_instances(positive_entities, negative_entities, args.depth, distinguish_levels)
    
    if args.subparser_name =="cv":
        logging.info("Start deserializing")
        #pipe = Pipe( instances= marshal.load(open(args.file, 'rb')))
        logging.info("Start loading X, Y")
        #x,y,space = pipe.instances_to_scipy_sparse() 
        (x,y) = pickle.load(open(args.file, 'rb'))
        classify_svm_cv(x, y, args.folds)


    elif args.subparser_name =="grid":
        logging.info("Start deserializing")
        #pipe = Pipe( instances= marshal.load(open(args.file, 'rb')))
        logging.info("Start loading X, Y")
        #x,y,space = pipe.instances_to_scipy_sparse() 
        (x,y) = pickle.load(open(args.file, 'rb'))
        do_grid_search(x, y, args.folds)
 
        
    elif args.subparser_name == "serialize":
        positive_entities = classifier.read_entities_file(args.positivefile)
        negative_entities = classifier.read_entities_file(args.negativefile)
        print "read entities"
        logging.info("Pulling entities from database")
        positive_instance = classifier.get_instances_from_entities(classifier.get_entity_objects(positive_entities), 1 )
        negative_instance = classifier.get_instances_from_entities(classifier.get_entity_objects(negative_entities), 0 )
        instances = positive_instance + negative_instance
        logging.info("Creating pipe")
        pipe = Pipe([wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(depth = 3,distinguish_levels=True ),], 
        instances)
        logging.info("Pushing into pipe")
        pipe.push_all()
        x,y,space = pipe.instances_to_scipy_sparse() 
        serialize_instances((x,y), args.outfile)


if __name__=="__main__":
    main()