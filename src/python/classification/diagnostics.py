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
from pipe import Pipe
import pickle
import marshal
from sklearn import svm, grid_search
import classifier
from sklearn.cross_validation import StratifiedShuffleSplit
from scipy.sparse import *
from sklearn.metrics import *
from pprint import pprint
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import copy
from time import time
from sklearn.feature_selection import SelectPercentile, chi2

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')



def do_cv(X, Y, folds=5, C=1.0):
		clf = svm.LinearSVC(C=C)
		logging.info("Starting cross validation")
		skf = cross_validation.StratifiedKFold(Y, n_folds=folds)
		scores = cross_validation.cross_val_score(clf, X, Y, cv=skf, n_jobs=8, scoring='roc_auc')
		logging.info("Cross validation completed!")
		print scores
		print("ROC_AUC: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))



def do_grid_search(instances, X, y, folds = 5):

		train, test = split_data_stratified(X,y)
		model = get_model_with_optimal_C (X[train], y[train], folds)
		scores = model.decision_function(X[test])
		print("\nROC score on Test Data")
		print roc_auc_score( y[test], scores)

		#do_error_analysis(y_true, y_pred, d['test_index'], instances)



def get_model_with_optimal_C (X, y, folds = 5):
		param_grid = {'C': [0.000001, 0.001, 0.01, 1,10, 100 ,1000, 10000]}
		svr = svm.LinearSVC()

		strat_cv = cross_validation.StratifiedShuffleSplit(y, test_size = 1.0/folds)
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


def do_roc(X, y, folds = 5):

		cv = StratifiedKFold(y, n_folds=folds)
		classifier = svm.LinearSVC()

		mean_tpr = 0.0
		mean_fpr = np.linspace(0, 1, 100)
		all_tpr = []

		for i, (train, test) in enumerate(cv):
				
				model = classifier.fit(X[train], y[train])
				raw =  model.decision_function(X[test])
				fpr, tpr, thresholds = roc_curve(y[test], raw)
				mean_tpr += interp(mean_fpr, fpr, tpr)
				mean_tpr[0] = 0.0
				roc_auc = auc(fpr, tpr)
				plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))

		plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')

		mean_tpr /= len(cv)
		mean_tpr[-1] = 1.0
		mean_auc = auc(mean_fpr, mean_tpr)
		plt.plot(mean_fpr, mean_tpr, 'k--',
		         label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

		plt.xlim([-0.05, 1.05])
		plt.ylim([-0.05, 1.05])
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver operating characteristic example')
		plt.legend(loc="lower right")
		plt.savefig('roc.png')


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



def do_feature_set_analysis(pipe, X, y):

	groups = set(['unigram_feature_generator','bigram_feature_generator', 'geo_feature_generator', 'simple_entity_text_feature_generator', 'wikipedia_categories_feature_generator'])
	train, test = split_data_stratified(X,y)
	opt_groups = set()
	classifier = svm.LinearSVC(C = 0.01)


	model = get_model_with_optimal_C (X[train], y[train])
	raw =  model.decision_function(X[test])	
	fpr, tpr, thresholds = roc_curve(y[test], raw)
	roc_auc = auc(fpr, tpr)
	plt.plot(fpr, tpr, lw=1, label='ALL  (area = %0.2f)' % (roc_auc))


	all_tpr = []

	for g in groups:
			keep_groups = copy.copy(opt_groups)

			keep_groups.add(g)
			print keep_groups
			X,y,space = pipe.instances_to_scipy_sparse(ignore_groups = groups.difference(keep_groups))

			model = get_model_with_optimal_C (X[train], y[train])

			scores =  model.decision_function(X[test])
			fpr, tpr, thresholds = roc_curve(y[test], scores)

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





def split_data_stratified(X, y, test_size = 0.33):
		sss = StratifiedShuffleSplit(y, 1, test_size=test_size, random_state=0)
		for train_index, test_index in sss:
				return train_index, test_index

def serialize_instances(instances, outfile):
    pickle.dump(instances, open(outfile,'wb'))
    
def main():
		parser = argparse.ArgumentParser(description='build classifier')
		subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')

		parser_cv = subparsers.add_parser('cv', help='perform cross validation')
		parser_cv.add_argument('--folds', type=int, default = 5, required=False, help='number of folds')
		parser_cv.add_argument('--data_folder',  required=True, help='file to pickled instances')


		parser_grid = subparsers.add_parser('grid', help='perform CV grid search')
		parser_grid.add_argument('--folds', type=int, default = 5, required=False, help='number of folds')
		parser_grid.add_argument('--data_folder',  required=True, help='file to pickled instances')

		parser_roc = subparsers.add_parser('roc', help='perform CV grid search')
		parser_roc.add_argument('--folds', type=int, default = 5, required=False, help='number of folds')
		parser_roc.add_argument('--data_folder',  required=True, help='file to pickled instances')

		parser_feat = subparsers.add_parser('features', help='perform CV grid search')
		parser_feat.add_argument('--data_folder',  required=True, help='file to pickled instances')

		args = parser.parse_args()    
		logging.info("Start deserializing")
		instances = classifier.load_instances(args.data_folder)
		pipe = Pipe( instances=instances)
		logging.info("Start loading X, Y")
		X,y,space = pipe.instances_to_scipy_sparse()
		

		if args.subparser_name =="cv":
				do_cv(X, y, args.folds)

		elif args.subparser_name =="grid":
				do_grid_search(instances, X, y, args.folds)

		elif args.subparser_name == "roc":
				do_roc(X, y, args.folds)
 
 		elif args.subparser_name == "features":
 				do_feature_selection(X, y)
 				#do_feature_set_analysis(pipe, X, y)




if __name__=="__main__":
    main()