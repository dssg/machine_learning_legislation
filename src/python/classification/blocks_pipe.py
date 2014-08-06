"""
this is blocks pipe. it groups instances by a grouper before generating
features.it's usefull for features on the document level
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
from pprint import pprint
import psycopg2
import logging
import numpy as np
import scipy
import multiprocessing as mp

def parallel_target(pipe_instances_tuple):
    pipe = pipe_instances_tuple[0]
    instances = pipe_instances_tuple[1]
    new_instances = pipe(instances)
    return new_instances
    for inst in new_instances:
        parallel_target.queue.put(inst)
    
def initilize_parallel(q):
    """
    q: queue object
    """
    #http://stackoverflow.com/questions/3827065/can-i-use-a-multiprocessing-queue-in-a-function-called-by-pool-imap
    parallel_target.queue = q
    
class BlocksPipe:
    def __init__(self, grouper, feature_generators=[], instances=[], num_processes = 1):
        self.feature_generators = feature_generators
        self.instances = instances
        self.num_processes = num_processes
        self.grouper = grouper
    
    def push_all_parallel(self):
        groups = self.grouper.group_instances(self.instances)
        if self.num_processes == 1:
            logging.info("pushing through block pipe with no pool")
            lst_of_lst_of_instances = [self.push_single(instances) for grp, instances in groups.iteritems()]
        else:
            logging.info("creating thread pool with %d threads" %(self.num_processes))
            logging.info("Before running thread pool")
            pool = mp.Pool(self.num_processes)
            lst_of_lst_of_instances = pool.map(func=parallel_target, iterable= [(self, instances) for grp, instances in groups.iteritems()])
        del self.instances[:]
        self.instances = []
        for lst in lst_of_lst_of_instances:
            for inst in lst:
                self.instances.append(inst)
        
        
    def __call__(self, instances):
        return self.push_single(instances)

        
    def push_single(self, instances):
        #logging.debug("operating on instance")
        for fg in self.feature_generators:
            fg.operate(instances)
        return instances