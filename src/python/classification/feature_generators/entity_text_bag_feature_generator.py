"""
enitity text bag of words feature generator
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


class entity_text_bag_feature_generator:
    def __init__(self, **kwargs):
        self.name = "entity_text_bag_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "ENTITY_TEXT_"
            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        instance.feature_groups[self.name] = []

        entity_text = normalize(instance.attributes["entity_inferred_name"])
        tokens = entity_text.split(' ')
        print tokens
        instance.feature_groups[self.name] += [Feature(self.feature_prefix +token, 1, self.name) for token in tokens ] 
        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
        