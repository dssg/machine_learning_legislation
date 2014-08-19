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
from sklearn.metrics import classification_report
from instance import Instance
import error_analysis
import pipe 
import marshal
from sklearn import svm, grid_search
import prepare_earmark_data
from sklearn.cross_validation import StratifiedShuffleSplit
from scipy.sparse import *
from pprint import pprint

from sklearn.metrics import roc_curve, auc, precision_recall_curve, f1_score, accuracy_score, accuracy_score, precision_score, recall_score, roc_auc_score, precision_recall_fscore_support
import matplotlib.pyplot as plt

from sklearn.externals import joblib
import cPickle as pickle

import copy
from time import time
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.ensemble import RandomForestClassifier

from matching.matching import bcolors
from util.prompt import query_yes_no
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


metrics = {

'accuracy': accuracy_score, 
'average_precision': accuracy_score,
'f1': f1_score,
'precision' : precision_score,
'recall': recall_score,
'roc_auc': roc_auc_score,
}


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



def get_scores(model, X):
    try:
        scores = model.decision_function(X)
    except:
        scores = model.predict_proba(X)[:, 1]
    return scores



def do_grid_search(X, y, folds, clf, param_grid, scoring, X_test = None, y_test = None):

    if X_test is not None:
        model = get_optimal_model (X, y, folds, clf, param_grid, scoring)

        y_pred = model.predict(X_test)
        scores = get_scores(model, X_test)

        print("Test ROC: %f" % roc_auc_score( y_test, scores))
        print(classification_report(y_test, y_pred))



    else:
        cv = cross_validation.StratifiedKFold(y, n_folds = folds, random_state = 0)
        cv_precision = []
        cv_recall = []
        cv_fscore = []
        cv_support = []
        roc = []

        for i, (train, test) in enumerate(cv):
            #model = get_optimal_model (X[train], y[train], folds, clf, param_grid, scoring)
            model = clf.fit(X[train], y[train])
            logging.info("Finished Training fold %d" %(i))
            y_pred = model.predict(X[test])
            scores = get_scores(model, X[test])

            cv_report = precision_recall_fscore_support(y[test],y_pred)
            cv_precision.append(cv_report[0])
            cv_recall.append(cv_report[1])
            cv_fscore.append(cv_report[2])
            cv_support.append(cv_report[3])
            roc.append(roc_auc_score( y[test], scores))
            
            print "Fold Precision Class 0: %0.4f" %(cv_report[0][0])
            print "Fold Precision Class 1: %0.4f" %(cv_report[0][1])
            print "Fold Recall Class 0: %0.4f" %(cv_report[1][0])
            print "Fold Recall Class 1: %0.4f" %(cv_report[1][1])
            print "Fold F-Score Class 0: %0.4f" %(cv_report[2][0])
            print "Fold F-Score Class 1: %0.4f" %(cv_report[2][1])

        
        
        precision0 = map(lambda x:x[0],cv_precision)
        precision1 = map(lambda x:x[1],cv_precision)
        recall0 = map(lambda x:x[0],cv_recall)
        recall1= map(lambda x:x[1],cv_recall)
        fscore0 = map(lambda x:x[0],cv_fscore)
        fscore1 = map(lambda x:x[1],cv_fscore)
        support0 = map(lambda x:x[0],cv_support)
        support1 = map(lambda x:x[1],cv_support)

        print "\n\n\nAggregate Test Performace\n"

        print "ROC: %0.4f, (%0.4f)" %(np.mean(roc),np.std(roc))
        print "Precision: %0.4f, (%0.4f)" %(np.mean(cv_precision),np.std(cv_precision))
        print "Recall: %0.4f, (%0.4f)" %(np.mean(cv_recall),np.std(cv_recall))
        print "F-Score: %0.4f, (%0.4f)" %(np.mean(cv_fscore),np.std(cv_fscore))
        print "Support: %0.4f, (%0.4f)" %(np.mean(cv_support),np.std(cv_support))
        print "\n"
        print "Precision Class 0: %0.4f, (%0.4f)" %(np.mean(precision0),np.std(precision0))
        print "Precision Class 1: %0.4f, (%0.4f)" %(np.mean(precision1),np.std(precision1))
        print "Recall Class 0: %0.4f, (%0.4f)" %(np.mean(recall0),np.std(recall0))
        print "Recall Class 1: %0.4f, (%0.4f)" %(np.mean(recall1),np.std(recall1))
        print "F-Score Class 0: %0.4f, (%0.4f)" %(np.mean(fscore0),np.std(fscore0))
        print "F-Score Class 1: %0.4f, (%0.4f)" %(np.mean(fscore1),np.std(fscore1))
        print "Support Class 0: %0.4f, (%0.4f)" %(np.mean(support0),np.std(support0))
        print "Support Class 1: %0.4f, (%0.4f)" %(np.mean(support1),np.std(support1))




def save_model(X, y, feature_space, folds, clf, param_grid, scoring, outfile):
   #model = get_optimal_model (X, y, folds, clf, param_grid, scoring)
    clf = svm.LinearSVC(C = 0.01)
    model = clf.fit(X,y)
    joblib.dump(model, outfile, compress=9)
    pickle.dump(feature_space, open(outfile+'.feature_space','wb'))




def get_optimal_model (X, y, folds, clf, param_grid, scoring):

        print "\n\n\nDoing Gridsearch\n"

        strat_cv = cross_validation.StratifiedKFold(y, n_folds = folds)
        model = grid_search.GridSearchCV(cv  = strat_cv, estimator = clf, param_grid  = param_grid,  n_jobs=multiprocessing.cpu_count(), scoring = scoring)
        model = model.fit(X, y)
        y_pred = model.predict(X)
        scores = get_scores(model, X)

        print "Best Model Train ROC AUC: %f" % roc_auc_score(y, scores)
        print "Best Model Train F1: %f" % f1_score(y, y_pred)

        print("\nBest parameters set found:")
        best_parameters, score, _ = max(model.grid_scores_, key=lambda x: x[1])
        print(best_parameters, score)
        print "\n"
        print("Grid scores:")
        for params, mean_score, scores in model.grid_scores_:
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean_score, scores.std() / 2, params))

        return model


def do_feature_selection(train_instances, test_instances, folds, clf, param_grid, dense, outfile):
    keep_groups = set(train_instances[0].feature_groups.keys()).intersection(test_instances[0].feature_groups.keys())

    all_groups = set(train_instances[0].feature_groups.keys()).union(test_instances[0].feature_groups.keys())

    ignore_groups = all_groups.difference(keep_groups)

    X_train, y_train, feature_space = pipe.instances_to_matrix(train_instances, dense = dense, ignore_groups =ignore_groups)
    X_test, y_test = test_instances_to_matrix(feature_space, test_instances, dense = dense)

    all_tpr = []

    (chi2values, pval) =  chi2(X_train, y_train)

    feature_indices = [i[0] for i in sorted(enumerate(pval), key=lambda x:x[1])]
    index_to_name = {v:k for k, v in feature_space.items()}
    feature_names = [index_to_name[i] for i in feature_indices]

    print feature_indices[0:200]
    print feature_names[0:200]

    for percentile in range(1, 5, 1):
            t0 = time()
            ch2 = SelectPercentile(chi2, percentile=percentile)
            X_train_trans = ch2.fit_transform(X_train, y_train)
            print("done in %fs" % (time() - t0))

            model = get_optimal_model (X_train_trans, y_train, folds, clf, param_grid, 'roc_auc')

            X_test_trans = ch2.transform(X_test)

            scores = get_scores(model, X_test_trans)
            fpr, tpr, thresholds = roc_curve(y_test, scores)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, lw=1, label='%d  (area = %0.4f)' % (percentile, roc_auc))
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



def do_feature_set_analysis(train_instances, test_instances, folds, clf, param_grid, dense, outfile):

    groups = set(train_instances[0].feature_groups.keys()).intersection(test_instances[0].feature_groups.keys())
    opt_groups = set()

    X_train, y_train, feature_space = pipe.instances_to_matrix(train_instances, dense = dense)
    X_test, y_test = test_instances_to_matrix(feature_space, test_instances, dense = dense)
    model = get_optimal_model(X_train, y_train, folds, clf, param_grid, 'roc_auc')
    scores =  get_scores(model, X_test) 

    fpr, tpr, thresholds = roc_curve(y_test, scores)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, lw=1, label='ALL  (area = %0.4f)' % (roc_auc))


    all_tpr = []

    for g in groups:
            keep_groups = copy.copy(opt_groups)
            keep_groups.add(g)
            print keep_groups

            X_train, y_train, feature_space = pipe.instances_to_matrix(train_instances, ignore_groups = groups.difference(keep_groups), dense = dense)
            X_test, y_test = test_instances_to_matrix(feature_space, test_instances, dense = dense)

            model = get_optimal_model(X_train, y_train,  folds, clf, param_grid, 'roc_auc')

            scores =  scores =  get_scores(model, X_test)
            fpr, tpr, thresholds = roc_curve(y_test, scores)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, lw=1, label='%s  (area = %0.4f)' % (g.split("_")[0], roc_auc))
            print "\n"*4

    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Feature Set Analysis')
    plt.legend(loc="lower right", prop={'size':12})
    plt.savefig(outfile)





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




def test_instances_to_matrix(feature_space, instances, ignore_groups=[], dense = False):
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

    if not dense:
        return scipy.sparse.csr_matrix(X), np.array(Y) 
    else:
        return X.todense(), np.array(Y) 




def main():
        parser = argparse.ArgumentParser(description='build classifier')

        parser.add_argument('--train',  required=True, help='file to pickled training instances')
        parser.add_argument('--test',  required=False, help='file to pickled test instances')
        parser.add_argument('--folds',  required=False, type = int, default = 5, help='number of folds for cv')
        parser.add_argument('--alg', required = True, help = "'rf' for RandomForest, 'svm' for LinearSVC")
        subparsers = parser.add_subparsers(dest = "subparser_name", help='sub-command help')

        parser_grid = subparsers.add_parser('grid', help='tune hyper-parameters')
        parser_grid.add_argument('--scoring', required = True)

        parser_save = subparsers.add_parser('save', help='tune hyper-parameters')
        parser_save.add_argument('--scoring', required = True)
        parser_save.add_argument('--outfile', required = True)

        parser_error = subparsers.add_parser('error', help='do error analysis')
        parser_features = subparsers.add_parser('features', help='do feature analysis')
        parser_features.add_argument('--outfile', required = True)

        parser_error = subparsers.add_parser('relabel', help='do error analysis')




        args = parser.parse_args() 

        print "Doing %s" % args.subparser_name
        print "Train: %s" %args.train
        print "Test: %s" % args.test

        if args.alg == 'svm':
            clf = svm.LinearSVC(C = 0.01)
            param_grid = {'C': [ 0.001, 0.01, 0.1, 0.5, 1, 4, 10, 100]}
            dense = False

        else:
            clf = RandomForestClassifier(n_estimators=10,max_depth=None, random_state = 0,max_features = 'log2', n_jobs = -1)
            param_grid = {'n_estimators' : [10, 30, 50, 100, 300, 500], 'max_features' : ['log2', 'sqrt'] }
            dense = True

        if args.subparser_name == "save":

            keep_group = ['unigram_feature_generator', 'simple_entity_text_feature_generator', 'geo_feature_generator']
            instances = prepare_earmark_data.load_instances(args.train)
            ignore_groups = [ fg for fg in instances[0].feature_groups.keys() if fg not in keep_group]
            X, y, feature_space = pipe.instances_to_matrix(instances, dense = dense, ignore_groups = ignore_groups)
            save_model(X, y, feature_space, args.folds, clf, param_grid, args.scoring, args.outfile)

        elif args.subparser_name =="error":

            #this does error analysis on training data only!
            instances = prepare_earmark_data.load_instances(args.train)
            X, y, feature_space = pipe.instances_to_matrix(instances, dense = dense)
            error_analysis_for_labeling(instances, X, y, args.folds, clf, param_grid, args.train)

        elif args.subparser_name =="grid":


            if args.test:
                train_instances = prepare_earmark_data.load_instances(args.train)
                test_instances = prepare_earmark_data.load_instances(args.test)
                X_train, y_train, feature_space = pipe.instances_to_matrix(train_instances, dense = dense)
                X_test, y_test = test_instances_to_matrix(feature_space, test_instances, dense = dense)
                

            else:
                instances = prepare_earmark_data.load_instances(args.train)
                X_train, y_train, feature_space = pipe.instances_to_matrix(instances, dense = dense)
                X_test = None
                y_test = None
                

            do_grid_search(X_train, y_train, args.folds, clf, param_grid, args.scoring, X_test, y_test)
            

        elif args.subparser_name == "features":

            if args.test:
                train_instances = prepare_earmark_data.load_instances(args.train)
                test_instances = prepare_earmark_data.load_instances(args.test)
                
            else:
                # this is just for exposition, would really want to cv over this
                instances = prepare_earmark_data.load_instances(args.train)
                X, y, feature_space = pipe.instances_to_matrix(instances, dense = dense)
                train, test =  split_data_stratified(X, y, test_size = 0.33)
                train_instances = [instances[i] for i in train]
                test_instances = [instances[i] for i in test]
                
            #do_feature_selection(train_instances, test_instances, args.folds, clf, param_grid, dense, args.outfile)

            do_feature_set_analysis(train_instances, test_instances, args.folds, clf, param_grid, dense, args.outfile)


if __name__=="__main__":
    main()
