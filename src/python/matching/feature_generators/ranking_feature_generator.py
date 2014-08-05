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

class simple_entity_text_feature_generator:
    def __init__(self, **kwargs):
        self.force = kwargs.get("force", True)

        self.feature = kwargs['feature']
        self.feature_group = kwargs['feature_group']
        self.reverse = kwargs.get("reverse", True)
        self.name = "RANKNG_FEAUTURE_"+self.attribute.upper()
        self.feature_prefix = "RANKNG_FEAUTURE_"+self.attribute.upper()


            
    

    def operate(self, instances):
        """
        given an instance a list of categories as features
        """

        instances = sorted(instances, reverse = self.reverse, key = lambda x : x.feature_groups[self.feature_group][self.feature])

        for i in range(len(instances)):
            instance = instances[i]

            if not self.force and instance.feature_groups.has_key(self.name):
                return

            instance.feature_groups[self.name] =  {}

            
            instance.feature_groups[self.name][self.feature_prefix] = Feature(self.feature_prefix, i) 

            logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))

