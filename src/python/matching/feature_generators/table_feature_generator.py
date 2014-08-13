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

class TableFeatureGenerator:
    def __init__(self, **kwargs):
        self.force = kwargs.get("force", True)
        self.name = "TABLE_FEAUTURE_GENERATOR"



    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return

        instance.feature_groups[self.name] =  {}

        feature_name = self.name+ "DOTS_OR_DASHES"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, 'dot' in instance.attributes['entity'].entity.source) 

        feature_name = "NUM_CELLS"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, len( instance.attributes['entity'].entity.entity_inferred_name.split("|"))) 


        #logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))

