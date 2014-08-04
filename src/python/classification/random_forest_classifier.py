"""
random forest classifier
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
from instance import Instance
from pipe import Pipe
import cPickle as pickle
import multiprocessing as mp
from multiprocessing import Manager

def classify_randomforest_cv(X,Y,estimators=10,test_data=0.4,features_func='sqrt'):
    #X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,Y,test_size=test_data, random_state = 0)

    logging.info('Starting Cross Validation')
    clf = RandomForestClassifier(n_estimators=estimators,max_depth=None,
                                 min_samples_split = 1, random_state = 0,max_features = features_func,oob_score = True)
    clf_fit = clf.fit(X,Y)
    oob_score = clf.oob_score_

    n = X.shape[0]
    loo = cross_validation.LeaveOneOut(n)

    loo_score = cross_validation.cross_val_score(clf,X,Y, cv= loo, n_jobs=3)
    logging.info("Cross validation completed!")
    
    print 'OOB Score:', oob_score
    print 'LOO Score:', scores
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    return oob_score,loo_score


def main():
    """
    Inputs Here
    ""
