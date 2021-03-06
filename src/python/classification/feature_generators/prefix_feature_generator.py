"""
simple enitity text feature generator
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from util import wiki_tools
from pprint import pprint
import logging
import numpy as np
import scipy
import string
import re
from classification.feature import Feature
from matching.string_functions import normalize


class PrefixFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "prefix_feature_generator"
        self.force = kwargs.get("force", True)
        self.prefixes = kwargs['prefixes']

            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return

        instance.feature_groups[self.name] = {}

        s = instance.attributes["entity_inferred_name"]

        for prefix in self.prefixes:
            if s.startswith(prefix):
                feature_name = self.name +"_" + prefix
                instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1)
        

        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
