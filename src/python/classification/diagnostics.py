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
from scipy.sparse import *
from sklearn.metrics import *
from pprint import pprint


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')



def do_cv(X, Y, folds=5):
    C = 1.0
    clf = svm.SVC(kernel='linear', C=C)
    #clf = sklearn.ensemble.RandomForestClassifier()
    logging.info("Starting cross validation")
    skf = cross_validation.StratifiedKFold(Y, n_folds=folds)
    scores = cross_validation.cross_val_score(clf, X, Y, cv=skf, n_jobs=8, scoring='f1')
    logging.info("Cross validation completed!")
    print scores
    print("F1: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def do_grid_search(instances, X, y, folds = 5):

		d = split_data_stratified(X,y)
		#param_grid = {'C': [0.000001, 0.001, 1, 100 , 10000], 'kernel': ['linear']}
		param_grid = {'C': [1,], 'kernel': ['linear']}

		svr = svm.SVC()
		strat_cv = cross_validation.StratifiedKFold(d['y_train'], n_folds=folds)
		clf = grid_search.GridSearchCV(cv  = strat_cv, estimator = svr, param_grid  =param_grid, scoring = 'f1', n_jobs=8)
		clf.fit(d['X_train'], d['y_train'])

		print("Best parameters set found on development set:")
		best_parameters, score, _ = max(clf.grid_scores_, key=lambda x: x[1])
		print(best_parameters, score)
		print "\n"

		print("Grid scores on development set:")
		for params, mean_score, scores in clf.grid_scores_:
		    print("%0.3f (+/-%0.03f) for %r"
		          % (mean_score, scores.std() / 2, params))

		print("Detailed classification report:")
		print("The model is trained on the full development set.")
		print("The scores are computed on the full evaluation set.")
		y_true, y_pred = d['y_test'], clf.predict(d['X_test'])
		print("Confusion Matrix on Test Data")
		print confusion_matrix(y_true, y_pred)
		print("F1 score on Test Data")
		print f1_score(y_true, y_pred)
		print(classification_report(y_true, y_pred))

		do_error_analysis(y_true, y_pred, d['test_index'], instances)


def do_error_analysis(y_true, y_pred, test_index, instances):
	print y_true
	print y_pred
	print test_index

	false_negatives = np.logical_and(y_true==1, y_pred==0).nonzero()[0]
	false_positives = np.logical_and(y_true==0, y_pred==1).nonzero()[0]
	true_negatives = np.logical_and(y_true==0, y_pred==0).nonzero()[0]
	true_positives = np.logical_and(y_true==1, y_pred==1).nonzero()[0]


	if false_negatives.size > 0 :
		print "False Negatives:"
		fn_entities = [instances[test_index[i]].attributes['entity_inferred_name'] for i in np.nditer(false_negatives)]
		print len(fn_entities)
		pprint(fn_entities)

	print "\n"*5

	if false_positives.size >0:
		fp_entities = [instances[test_index[i]].attributes['entity_inferred_name'] for i in np.nditer(false_positives)]
		print "False Posiitves:"
		print len(fp_entities)
		pprint(fp_entities)

	print "\n"*5

	if true_negatives.size >0:
		print "True Negatives:"
		tn_entities = [instances[test_index[i]].attributes['entity_inferred_name'] for i in np.nditer(true_negatives)]
		print len(tn_entities)
		pprint(tn_entities)


	print "\n"*5

	if true_positives.size > 0 :
		print "True Posiitves:"
		tp_entities = [instances[test_index[i]].attributes['entity_inferred_name'] for i in np.nditer(true_positives)]
		print len(tp_entities)
		pprint(tp_entities)





def split_data(X, y, test_size = 0.33):
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
		return {'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test}



def split_data_stratified(X, y, test_size = 0.33):
		sss = StratifiedShuffleSplit(y, 1, test_size=test_size, random_state=0)
		X = csr_matrix(X)
		for train_index, test_index in sss:
				X_train, X_test = X[train_index], X[test_index]
				y_train, y_test = y[train_index], y[test_index]
				return {'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test, 'test_index': test_index}

def serialize_instances(instances, outfile):
    pickle.dump(instances, open(outfile,'wb'))
    
def main():
    parser = argparse.ArgumentParser(description='build classifier')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_cv = subparsers.add_parser('cv', help='perform cross validation')
    parser_cv.add_argument('--folds', type=int, required=True, help='number of folds')
    parser_cv.add_argument('--data_folder',  required=True, help='file to pickled instances')


    parser_grid = subparsers.add_parser('grid', help='perform CV grid search')
    parser_grid.add_argument('--folds', type=int, required=False, help='number of folds')
    parser_grid.add_argument('--data_folder',  required=True, help='file to pickled instances')
    
    args = parser.parse_args()    
    
    #x, y, space = encode_instances(positive_entities, negative_entities, args.depth, distinguish_levels)
    
    if args.subparser_name =="cv":
        logging.info("Start deserializing")
        instances = classifier.load_instances(args.data_folder)
        pipe = Pipe( instances=instances)
        logging.info("Start loading X, Y")
        X,y,space = pipe.instances_to_scipy_sparse() 
        do_cv(X, y, args.folds)


    elif args.subparser_name =="grid":
        logging.info("Start deserializing")
        instances = classifier.load_instances(args.data_folder)
        pipe = Pipe( instances=instances)
        logging.info("Start loading X, Y")
        X,y,space = pipe.instances_to_scipy_sparse() 
        do_grid_search(instances, X, y, args.folds)
 
        



if __name__=="__main__":
    main()