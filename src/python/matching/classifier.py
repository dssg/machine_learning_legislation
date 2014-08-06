import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
import numpy as np
from classification.pipe import Pipe
from classification.prepare_earmark_data import load_instances
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from sklearn.externals import joblib
import logging


def classify_randomforest_cv(X,y,estimators=100,test_data=0.4,features_func='log2', loo = False):

    logging.info('Starting Cross Validation')
    clf = RandomForestClassifier(n_estimators=estimators,max_depth=None,
                                 min_samples_split = 1, random_state = 0,max_features = features_func,oob_score = True)


    cv = cross_validation.StratifiedKFold(y, n_folds = 10, random_state = 0)
    
    cv_precision = []
    cv_recall = []
    cv_fscore = []
    cv_support = []

    for i, (train, test) in enumerate(cv):
        model = clf.fit(X[train], y[train])
        y_pred = model.predict(X[test])
        #target_names = ['no match', 'match']target_names=target_names
        print(classification_report(y[test], y_pred))

        #cv_report = precision_recall_fscore_support(y[test],y_pred,average='micro')
        #print(classification_report(y[test], y_pred))
        cv_report = precision_recall_fscore_support(y[test],y_pred)
        cv_precision.append(cv_report[0])
        cv_recall.append(cv_report[1])
        cv_fscore.append(cv_report[2])
        cv_support.append(cv_report[3])



    print "Precision: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(cv_precision),np.std(cv_precision))
    print "Recall: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(cv_recall),np.std(cv_recall))
    print "F-Score: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(cv_fscore),np.std(cv_fscore))
    print "Support: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(cv_support),np.std(cv_support))
    
    precision0 = map(lambda x:x[0],cv_precision)
    precision1 = map(lambda x:x[1],cv_precision)
    
    recall0 = map(lambda x:x[0],cv_recall)
    recall1= map(lambda x:x[1],cv_recall)
    
    fscore0 = map(lambda x:x[0],cv_fscore)
    fscore1 = map(lambda x:x[1],cv_fscore)
    
    support0 = map(lambda x:x[0],cv_support)
    support1 = map(lambda x:x[1],cv_support)
    
    print "Precision Class 0: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(precision0),np.std(precision0))
    print "Precision Class 1: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(precision1),np.std(precision1))

    print "Recall Class 0: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(recall0),np.std(recall0))
    print "Recall Class 1: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(recall1),np.std(recall1))

    
    print "F-Score Class 0: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(fscore0),np.std(fscore0))
    print "F-Score Class 1: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(fscore1),np.std(fscore1))

    
    print "Support Class 0: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(support0),np.std(support0))
    print "Support Class 1: Mean-%0.2f, Standard Error-%0.2f" %(np.mean(support1),np.std(support1))


    if loo :
        n = X.shape[0]
        cv_loo = cross_validation.LeaveOneOut(n)
        scores = cross_validation.cross_val_score(clf,X,Y, cv= cv_loo, n_jobs=8)

        logging.info("Cross validation completed!")
    
    
        print 'LOO Score:', scores
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))





def main():
    parser = argparse.ArgumentParser(description='build classifier')

    parser.add_argument('--data',  required=True, help='folder to pickled training instances')
    parser.add_argument('--action', default = 'cv' , help='cv|build')
    parser.add_argument('--outfile', default = 'matching_rf.pkl' , help='outfile to write model to')
    parser.add_argument('--trees', type=int, default = 100 , help='number of trees')

    args = parser.parse_args()  

    logging.info("Start deserializing")
    instances = load_instances(args.data)
    pipe = Pipe( instances=instances)
    logging.info("Start loading X, Y")
    X, y, feature_space = pipe.instances_to_scipy_sparse()
    if args.action =="cv":
        classify_randomforest_cv(X.todense(), y)
    elif args.action =="build":
        clf = RandomForestClassifier(n_estimators=args.trees, max_depth=None,
                    min_samples_split = 1, random_state = 0,max_features = 'log2',oob_score = True)
        model = clf.fit(X.todense(), y)
        joblib.dump(model, 'matching_rf.pkl', compress=9)
    else:
        print "Unrecognized option!"




if __name__=="__main__":
    main()
