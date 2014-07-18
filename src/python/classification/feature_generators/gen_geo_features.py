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


def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, ' ')

    s = re.sub(r'[ ]{2,}', " ", s)
    return s.lower()


	def geo_inferred_text_has_state(self, entity):



	def geo_inferred_text_has_city(self, entity):




feature_functions = [
('geo_inferred_text_has_state', geo_inferred_text_has_state), 
('geo_inferred_text_has_city', geo_inferred_text_has_city), 
]

    


class geo_feature_generator:
    def __init__(self, **kwargs):
        self.name = "geo_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "GEO_FEAUTURE_"
            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        instance.feature_groups[self.name] = []

        s = instance.attributes["entity_inferred_name"]
        
        
        instance.feature_groups[self.name]+= [Feature(self.feature_prefix +t[0], t[1](s), self.name) for t in feature_functions]



        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))



	

