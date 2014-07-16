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

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

NO_WIKI_PAGE_FEATURE = "NO_WIKIPEDIA_PAGE_WAS_FOUND"

def entity_id_to_wikipage(entity_id):
    """
    given an entity id, returns the corresponding wikipedia page.
    if no page is found, None returned
    """
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = "select wikipedia_page from entity_wikipedia_page where entity_id = %s"
        cur = conn.cursor()
        cur.execute(cmd, (entity_id,))
        result = cur.fetchone()
        if result and len(result) > 0:
            return result[0]
        else:
            return None
        
    except Exception as exp:
        conn.rollback()
        print exp
        raise exp
    finally:
        conn.close()
    
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

def get_entity_features(entity_id, depth=3, distinguish_levels=True):
    """
    given an entity_id, generate a list of categories as features
    entity_id: the id of the entity
    distingiosh_levels: prefix parent categories with their level, so that 
    the categories differ based on the level
    """
    features = set()
    page_title = entity_id_to_wikipage(entity_id)
    if page_title:
        categories = wiki_tools.get_category_hierarchy(page_title, depth)
        if distinguish_levels:
            for i in range(len(categories)):
                level = categories[i]
                features.update([ str(i+1)+"_"+cat for cat in level  ] )
        else:
            features.update([[cat for cat in level] for level in categories ] )
    else:
        set.add(NO_WIKI_PAGE_FEATURE)
    logging.debug("Generated %d features for entity id: %d" %(len(features), entity_id))
    return features
    
def get_entity_list_features(entity_ids_list, depth=3, distinguish_levels=True):
    """
    generate entire feature space for a collection of entities
    """
    if len(entity_ids_list) == 1:
        return get_entity_features(entity_ids_list[0], depth, distinguish_levels)
    else:
        return reduce(lambda a, b : a.union(b) , [get_entity_features(entity_id, depth, distinguish_levels) for entity_id in entity_ids_list]  )

def generate_feature_space(positive_entity_ids_list, negative_entity_ids_list, depth=3, distinguish_levels=True):
    """
    generates the feature space
    """
    positive_space = get_entity_list_features(positive_entity_ids_list, depth, distinguish_levels)
    negative_space = get_entity_list_features(negative_entity_ids_list, depth, distinguish_levels)
    space = positive_space.union(negative_space)
    dimension_ids = sorted( list(space))
    feature_encoding = {}
    i = 1
    for d in dimension_ids:
        feature_encoding[d] = i
        i +=1 
    return feature_encoding

def represent_entity(entity_id, feature_space, depth=3, distinguish_levels=True):
    """
    given feature_space dictionary which is the result of @generate_feature_space
    , the representaiton of this entity id is returned
    """
    feature_names = get_entity_features(entity_id, depth, distinguish_levels)
    dimenstions = set()
    for feature in feature_names:
        set.add(feature_space[feature])
    return sorted(list(dimenstions))
    
    
def encode_instances(positive_entities, negative_entities, depth=3, distinguish_levels=True):
    """
    create representaiton file of the positive and negative entities
    """
    #feature_space = generate_feature_space(positive_entities, negative_entities, depth=3, distinguish_levels=True)
    feature_space = {}
    entity_count = len(positive_entities) + len(negative_entities)
    instances = []
    entities = positive_entities + negative_entities
    index = 0
    for i in range(len(entities)  ):
        features = get_entity_features(entities[i], depth, distinguish_levels)
        f_vector = []
        for f in features:
            if not feature_space.has_key(f):
                feature_space[f] = index
                index +=1
            f_vector.append(feature_space[f])
        instances.append( (entities[i], f_vector))
    X = np.zeros( (entity_count, len(feature_space)) )
    #X = np.sparse.lil_matrix((entity_count, len(feature_space)))
    Y = []
    for i in range(len(instances)):
        for j in instances[i][1]:
            X[i, j] = 1
        Y.append( instances[i][0] in positive_entities)
    logging.info("%d instances were mapped to space with %d dimensions" %(len(entities), len(feature_space)))
    return scipy.sparse.coo_matrix(X), np.array(Y), feature_space

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
    
def main():
    parser = argparse.ArgumentParser(description='build classifier')
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_cv = subparsers.add_parser('cv', help='perform cross validation')
    parser_cv.add_argument('--folds', type=int, required=True, help='number of folds')
    
    parser_cv = subparsers.add_parser('transform', help='transform to svmlight format')
    parser_cv.add_argument('--outfile', required=True, help='path to output file')

    parser.add_argument('--positivefile', required=True, help='file containing entities identified as earmarks')
    parser.add_argument('--negativefile',  required=True, help='file containing negative example entities')
    parser.add_argument('--depth', type=int, default = 3,  help='wikipedia category level depth')
    parser.add_argument('--ignore_levels', action='store_false', default=False, help='distinguish between category levels')
    
    args = parser.parse_args()
    distinguish_levels = not args.ignore_levels
    positive_entities = read_entities_file(args.positivefile)
    negative_entities = read_entities_file(args.negativefile)
    logging.info("Pulling entities from database")
    positive_instance = get_instances_from_entities(get_entity_objects(positive_entities), 1 )
    negative_instance = get_instances_from_entities(get_entity_objects(negative_entities), 0 )
    instances = positive_instance + negative_instance
    
    logging.info("Creating pipe")
    pipe = Pipe([wikipedia_categories_feature_generator.wikipedia_categories_feature_generator(),], instances)
    logging.info("Pushing into pipe")
    pipe.push_all()
    x,y,space = pipe.instances_to_scipy_sparse();
    
    #x, y, space = encode_instances(positive_entities, negative_entities, args.depth, distinguish_levels)
    
    if args.subparser_name =="cv":
        classify_svm_cv(x, y, args.folds)
    elif args.subparser_name == "transform":
        convert_to_svmlight_format(x, y, positive_entities+negative_entities, args.outfile)
        
if __name__=="__main__":
    main()
