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
import multiprocessing as mp


def parallel_target(pipe_instance_tuple):
    pipe = pipe_instance_tuple[0]
    instance = pipe_instance_tuple[1]
    new_instance = pipe(instance)
    parallel_target.queue.put(new_instance)
    
def initilize_parallel(q):
    """
    q: queue object
    """
    #http://stackoverflow.com/questions/3827065/can-i-use-a-multiprocessing-queue-in-a-function-called-by-pool-imap
    parallel_target.queue = q

class Pipe:
    def __init__(self, feature_generators=[], instances=[], num_processes = 1):
        """
        accepts a list of instances of abstract_feature_generator
        """
        self.feature_generators = feature_generators
        self.instances = instances
        self.num_processes = 1
        
    def push_single(self, instance):
        """
        pushes instance through the pipe of feature generators
        """
        for fg in self.feature_generators:
            #logging.debug("operating on instance %s" %(instance.__str__()))
            fg.operate(instance)
        # return statement is added to support multiprocessing
        return instance
    
    def __call__(self, instance):
        return self.push_single(instance)
            
    def push_all(self):
        #pool = multiprocessing.Pool(self.num_processes)
        #pool.map(func=self, iterable=self.instances)
        for i in self.instances:
            self.push_single(i)
            
    def push_all_parallel(self):
        out_queue = mp.Queue()
        pool = mp.Pool(self.num_processes, initilize_parallel, [out_queue])
        pool.map(func=parallel_target, iterable= [(self, i) for i in self.instances])
        new_instances = []
        for i in range(len(self.instances)):
            new_instances.append(out_queue.get())
        self.instances = new_instances
        
    def instances_to_scipy_sparse(self, ignore_groups=[]):
        """
        ingore_groups: list containing generator names to ignore their features
        """
        feature_space = {}
        index = 0
        for i in self.instances:
            for f_group, features in i.feature_groups.iteritems():
                if f_group in ignore_groups:
                    continue
                for f in features:
                    if not feature_space.has_key(f.name):
                        feature_space[f.name] = index
                        index +=1
        logging.debug("%d instances, %d features" %(len(self.instances), len(feature_space)))
        #X = np.zeros( (len(self.instances), len(feature_space)) )
        X = scipy.sparse.lil_matrix((len(self.instances), len(feature_space)))
        Y = []
        for i in range(len(self.instances)):
            for f_group, features in self.instances[i].feature_groups.iteritems():
                if f_group in ignore_groups:
                    continue
                for f in features:
                    X[i, feature_space[f.name]] =  f.value
            Y.append(self.instances[i].target_class)
        logging.info("%d Instances loaded with %d features" %(X.shape[0], X.shape[1]))
        return scipy.sparse.coo_matrix(X), np.array(Y), feature_space            
            
    def set_instances(self, instances):
        self.instances = instances
    
        
            
        
    
