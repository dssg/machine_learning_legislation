import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from pprint import pprint
import logging
import numpy as np
import scipy
import string
import re
from classification.feature import Feature

class RankingFeatureGenerator:
    def __init__(self, **kwargs):
        self.force = kwargs.get("force", True)

        self.feature = kwargs['feature']
        self.feature_group = kwargs['feature_group']
        self.reverse = kwargs.get("reverse", True)
        self.name = kwargs['prefix'] + "RANKNG_FEAUTURE_"+self.feature.upper()
        self.feature_prefix = self.name



            
    

    def operate(self, instances):
        """
        given an instance a list of categories as features
        """

        instances = sorted(instances, reverse = self.reverse, key = lambda x : x.feature_groups[self.feature_group][self.feature].value)

        for i in range(len(instances)):
            instance = instances[i]

            if not self.force and instance.feature_groups.has_key(self.name):
                return

            instance.feature_groups[self.name] =  {}

            
            instance.feature_groups[self.name][self.feature_prefix] = Feature(self.feature_prefix, i) 

            #logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))

