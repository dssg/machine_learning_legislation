"""
mallet equivelant of serial pipe
to generate x and y to be used in sciket learn classification
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
from util import wiki_tools
from pprint import pprint
import psycopg2
import logging
import numpy as np
import scipy

class Pipe:
    def __init__(self, feature_generators, instances=[]):
        """
        accepts a list of instances of abstract_feature_generator
        """
        self.feature_generators = feature_generators
        self.instances = instances
        
    def push_single(self, instance):
        """
        pushes instance through the pipe of feature generators
        """
        for fg in self.feature_generators:
            fg.operate(instance)
            
    def push_all(self):
        for i in self.instances:
            self.push_single(i)
        
    def instances_to_scipy_sparse(self):
        feature_space = {}
        index = 0
        for i in self.instances:
            for f in i.features:
                if not feature_space.has_key(f.name):
                    feature_space[f.name] = index
                    index +=1
        X = np.zeros( (len(self.instances), len(feature_space)) )
        Y = []
        for i in range(len(self.instances)):
            for f in self.instances[i].features:
                X[i, feature_space[f.name]] = f.value
            Y.append(self.instances[i].target_class)
        return scipy.sparse.coo_matrix(X), np.array(Y), feature_space            
            
    def set_instances(self, instances):
        self.instances = instances
    
        
            
        
    
