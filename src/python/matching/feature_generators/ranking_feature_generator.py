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

        self.pairs = kwargs['pairs']
        self.reverse = kwargs.get("reverse", True)
        self.name = "RANKING_FEAUTURE_GENERATOR"



    def operate(self, instances):
        """
        given an instance a list of categories as features
        """



        for pair in self.pairs:
            feature_group = pair[0]
            feature = pair[1]
            feature_name = self.name + feature_group + feature


            instances = sorted(instances, reverse = self.reverse, key = lambda x : x.feature_groups[feature_group][feature].value)

            for i in range(len(instances)):
                instance = instances[i]

                # make sure feature dict exists
                instance.feature_groups[self.name] =  instance.feature_groups.get(self.name, {})

                instance.feature_groups[self.name][feature_name] = Feature(feature_name, i) 

        #logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))

