import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
from pprint import pprint
import logging
import numpy as np
from scipy import interp
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from sklearn.cross_validation import StratifiedKFold
import scipy
from dao.Entity import Entity
from instance import Instance
import error_analysis
from pipe import Pipe
import pickle
import marshal
from sklearn import svm, grid_search
import classifier
from sklearn.cross_validation import StratifiedShuffleSplit
from scipy.sparse import *
from sklearn.metrics import *
from pprint import pprint
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import copy
from time import time
from sklearn.feature_selection import SelectPercentile, chi2

from util.matching import bcolors
from util.prompt import query_yes_no

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def error_analysis_for_labeling(instances, X, y, folds, data_folder, clf = svm.LinearSVC(C=0.01)):
	cv = cross_validation.StratifiedKFold(y, n_folds=folds, random_state = 0)
	for i, (train, test) in enumerate(cv):
		model = clf.fit(X[train], y[train])
		y_pred = model.predict(X[test])
		scores =  model.decision_function(X[test])
		#scores = model.predict_proba(X[test])[:,1]
		#precision, recall, thresholds = precision_recall_curve(y[test], scores)
		#print thresholds.shape[0]
		#for i in range(thresholds.shape[0]):
		#    print "Threshold: %f, Precision: %f, Recall: %f" %(thresholds[i], precision[i], recall[i])

		print("\nROC score on Test Data")
		print roc_auc_score( y[test], scores)
		do_error_analysis (y[test], y_pred, scores, test, instances)
		#relabel(y[test], y_pred, scores, test, instances, data_folder)
		print "\n"*5



def do_grid_search(X_train, y_train, X_test, y_test, folds):
		model = get_model_with_optimal_C (X_train, y_train, folds)
		scores = model.decision_function(X_test)
		print("\nROC score on Test Data")
		print roc_auc_score( y_test, scores)

		#do_error_analysis(y[test], model.predict(X[test]), scores,  test, instances)



def get_model_with_optimal_C (X, y, folds):
		param_grid = {'C': [ 0.001, 0.01, 0.1, 0.5, 1, 4, 10, 100]}
		svr = svm.LinearSVC()

		strat_cv = cross_validation.StratifiedKFold(y, n_folds = folds)
		model = grid_search.GridSearchCV(cv  = strat_cv, estimator = svr, param_grid  = param_grid,  n_jobs=8, scoring = 'roc_auc')
		model.fit(X, y)
		scores =  model.decision_function(X)
				
		print "\nROC_AUC on training data: %f" % roc_auc_score(y, scores)
		print("Best parameters set found via CV on training Data:")
		best_parameters, score, _ = max(model.grid_scores_, key=lambda x: x[1])
		print(best_parameters, score)
		print "\n"
		print("Grid scores:")
		for params, mean_score, scores in model.grid_scores_:
		    print("%0.3f (+/-%0.03f) for %r"
		          % (mean_score, scores.std() / 2, params))

		return model


def do_feature_selection(X, y):
		all_tpr = []
		train, test = split_data_stratified(X,y)

		for percentile in range(5, 45, 5):
				t0 = time()
				ch2 = SelectPercentile(chi2, percentile=percentile)
				X_train = ch2.fit_transform(X[train], y[train])
				print("done in %fs" % (time() - t0))

				model = get_model_with_optimal_C(X_train, y[train])

				X_test = ch2.transform(X[test])

				scores = model.decision_function(X_test)
				fpr, tpr, thresholds = roc_curve(y[test], scores)

				roc_auc = auc(fpr, tpr)
				plt.plot(fpr, tpr, lw=1, label='%d  (area = %0.2f)' % (percentile, roc_auc))
				print "\n"*4


		plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')

		
		plt.xlim([-0.05, 1.05])
		plt.ylim([-0.05, 1.05])
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver operating characteristic example')
		plt.legend(loc="lower right")
		plt.savefig('feature_selection.png')
		
		print()



def do_feature_set_analysis(train_instances, test_instances, folds):

	groups = set(['unigram_feature_generator', 'geo_feature_generator', 'simple_entity_text_feature_generator','politician_calais_feature_generator'])

	
	opt_groups = set()
	classifier = svm.LinearSVC(C = 0.01)

	pipe = Pipe( instances=train_instances)
	X_train, y_train, feature_space = pipe.instances_to_scipy_sparse()
	X_test, y_test = test_instances_to_scipy_sparse(feature_space, test_instances)


	model = get_model_with_optimal_C (X_train, y_train, folds)
	raw =  model.decision_function(X_test)	
	fpr, tpr, thresholds = roc_curve(y_test, raw)
	roc_auc = auc(fpr, tpr)
	plt.plot(fpr, tpr, lw=1, label='ALL  (area = %0.2f)' % (roc_auc))


	all_tpr = []

	for g in groups:
			keep_groups = copy.copy(opt_groups)
			keep_groups.add(g)
			print keep_groups


			X_train, y_train, feature_space = pipe.instances_to_scipy_sparse(ignore_groups = groups.difference(keep_groups))
			X_test, y_test = test_instances_to_scipy_sparse(feature_space, test_instances)


			model = get_model_with_optimal_C (X_train, y_train, folds)
			scores =  model.decision_function(X_test)
			fpr, tpr, thresholds = roc_curve(y_test, scores)
			roc_auc = auc(fpr, tpr)
			plt.plot(fpr, tpr, lw=1, label='%s  (area = %0.2f)' % (g.split("_")[0], roc_auc))
			print "\n"*4
	plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')

	
	plt.xlim([-0.05, 1.05])
	plt.ylim([-0.05, 1.05])
	plt.xlabel('False Positive Rate')
	plt.ylabel('True Positive Rate')
	plt.title('Receiver operating characteristic example')
	plt.legend(loc="lower right")
	plt.savefig('features.png')





def relabel(y_true, y_pred, scores, test_index, instances, data_folder, num = 20):
	#false_positives = np.logical_and(y_true==0, y_pred==1).nonzero()[0]
	false_positives = np.logical_and(y_true==0, scores > 0.25).nonzero()[0]

	if false_positives.size == 0:
		return

	fp_instances = [(test_index[i], scores[i]) for i in np.nditer(false_positives)]
	logging.debug("# of false positives %d"% len(fp_instances))
	fp_instances = sorted(fp_instances[:num], key = lambda x: x[0])

	for t in fp_instances[:num]:
		instance = instances[t[0]]
		try:
		    #error_analysis.analyze_entity(instance.attributes['id'])
		    error_analysis.analyze_entity_earmark_pair(instance.attributes['entity'], instance.attributes['earmark'])
		except Exception as ex:
		    logging.exception("Error while relabeling entity %d" %instance.attributes['id'])

def do_error_analysis(y_true, y_pred, scores, test_index, instances, num = 1000):
	#print y_true
	#print y_pred
	#print test_index

	template = "{0:8}  {1:5}  {2:150}" 

	false_negatives = np.logical_and(y_true==1, y_pred==0).nonzero()[0]
	false_positives = np.logical_and(y_true==0, y_pred==1).nonzero()[0]
	true_negatives = np.logical_and(y_true==0, y_pred==0).nonzero()[0]
	true_positives = np.logical_and(y_true==1, y_pred==1).nonzero()[0]

	if false_positives.size >0:
			fp_entities = [(instances[test_index[i]].attributes, scores[i]) for i in np.nditer(false_positives)]
			print "False Positives:"
			print len(fp_entities)
			for t in sorted(fp_entities[:num], key = lambda x: x[1]):
					print template.format (t[0]['id'], t[0]['document_id'], bcolors.OKGREEN + t[0]['entity_inferred_name'] + bcolors.ENDC) 

	print "\n"*5


	
	if false_negatives.size > 0 :
		print "False Negatives:"
		fn_entities = [ (instances[test_index[i]].attributes, scores[i]) for i in np.nditer(false_negatives)]
		print len(fn_entities)
		for t in sorted(fn_entities[:num], key = lambda x :x[1], reverse = True):
				print template.format (t[0]['id'], t[0]['document_id'], bcolors.OKGREEN + t[0]['entity_inferred_name'] + bcolors.ENDC) 
	print "\n"*5

	

	if true_negatives.size >0:
		print "True Negatives:"
		tn_entities = [(instances[test_index[i]].attributes, scores[i]) for i in np.nditer(true_negatives)]
		print len(tn_entities)
		for t in sorted( tn_entities[:num], key = lambda x: x[1]):
				print template.format (t[0]['id'], t[0]['document_id'], bcolors.OKGREEN + t[0]['entity_inferred_name'] + bcolors.ENDC)


	print "\n"*5

	if true_positives.size > 0 :
		print "True Positives:"
		tp_entities = [(instances[test_index[i]].attributes, scores[i]) for i in np.nditer(true_positives)]
		print len(tp_entities)
		for t in sorted (tp_entities[:num], key = lambda x :x[1], reverse = True):
				print template.format (t[0]['id'], t[0]['document_id'], bcolors.OKGREEN + t[0]['entity_inferred_name'] + bcolors.ENDC)


def split_data_stratified(X, y, test_size = 0.33):
		sss = StratifiedShuffleSplit(y, 1, test_size=test_size, random_state=0)
		for train_index, test_index in sss:
				return train_index, test_index

def test_instances_to_scipy_sparse(feature_space, instances, ignore_groups=[]):
    X = scipy.sparse.lil_matrix((len(instances), len(feature_space)))
    Y = []
    keys = set(feature_space.keys())
    for i in range(len(instances)):
        for f_group, features in instances[i].feature_groups.iteritems():
            if f_group in ignore_groups:
                continue
            for f_name, f in features.iteritems():
            		if f.name in keys:
                		X[i, feature_space[f.name]] =  f.value

        Y.append(instances[i].target_class)
    logging.info("%d Instances loaded with %d features" %(X.shape[0], X.shape[1]))
    return scipy.sparse.csr_matrix(X), np.array(Y)      

def main():
		parser = argparse.ArgumentParser(description='build classifier')

		parser.add_argument('--train',  required=True, help='file to pickled training instances')
		parser.add_argument('--test',  required=False, help='file to pickled test instances')
		parser.add_argument('--action',  required=True, help='what analysis do you want to run')
		parser.add_argument('--folds',  required=False, type = int, default = 5, help='number of folds for cv')
		args = parser.parse_args()    
		if args.action =="error":

				#this does error analysis on training data only!
				logging.info("Start deserializing")
				instances = classifier.load_instances(args.train)
				pipe = Pipe( instances=instances)
				logging.info("Start loading X, Y")
				X, y, feature_space = pipe.instances_to_scipy_sparse()
				error_analysis_for_labeling(instances, X, y, args.folds, args.train)

		if args.action =="grid":

				if args.test:
						logging.info("Start deserializing Train")
						train_instances = classifier.load_instances(args.train)
						logging.info("Start deserializing Test")
						test_instances = classifier.load_instances(args.test)
						pipe = Pipe( instances=train_instances)
						logging.info("Start loading X, Y")
						X_train, y_train, feature_space = pipe.instances_to_scipy_sparse()
						X_test, y_test = test_instances_to_scipy_sparse(feature_space, test_instances)


				else:
						logging.info("Start deserializing")
						instances = classifier.load_instances(args.train)
						pipe = Pipe( instances=instances)
						logging.info("Start loading X, Y")
						X, y, feature_space = pipe.instances_to_scipy_sparse()
						train, test =  split_data_stratified(X, y, test_size = 0.33)
						X_train = X[train]
						X_test = X[test]
						y_train = y[train]
						y_test = y[test]

				do_grid_search(X_train, y_train, X_test, y_test, args.folds)

 		elif args.action == "features":

				if args.test:
						logging.info("Start deserializing")
						train_instances = classifier.load_instances(args.train)
						test_instances = classifier.load_instances(args.test)
					
				else:
						logging.info("Start deserializing")
						instances = classifier.load_instances(args.train)
						pipe = Pipe( instances=instances)
						logging.info("Start loading X, Y")
						X, y, feature_space = pipe.instances_to_scipy_sparse()
						train, test =  split_data_stratified(X, y, test_size = 0.33)

						train_instances = [instances[i] for i in train]
						test_instances = [instances[i] for i in test]
						

 				#do_feature_selection(X, y)
 				do_feature_set_analysis(train_instances, test_instances, args.folds)


if __name__=="__main__":
    main()
