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



#number of all caps

def num_all_caps(s):
    return sum(1 for c in s if c.isupper())

# number of dots
def num_dots(s):
    return sum(1 for c in s if c == '.')

#num_words

def num_words(s):
    return len(normalize(s).split(' '))

#number of digits
def num_digits(s):
    return sum(1 for c in s if c.isdigit())

def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, ' ')

    s = re.sub(r'[ ]{2,}', " ", s)
    return s.lower()

def starts_with_for(s):
    tokens = s.split(' ')
    if len(tokens) == 0:
        return False

    first_token = tokens[0]
    return first_token == 'for'



def percent_capitalized(s):
    tokens = s.split(' ')
    if len(tokens) == 0:
        return 0
    count = 0.0
    for token in tokens:
        if len(token)>0:
            if token[0].isupper():
                count +=1.0
    return count/len(tokens)



feature_functions = [
('num_all_caps', num_all_caps), 
('num_dots', num_dots), 
('length', len), 
('num_words', num_words), 
('num_digits', num_digits),
('starts_with_for', starts_with_for), 
('percent_capitalized', percent_capitalized),
]

    


class simple_entity_text_feature_generator:
    def __init__(self, **kwargs):
        self.name = "simple_entity_text_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "ENTITY_TEXT_FEAUTURE_"
            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        instance.feature_groups[self.name] = {}

        s = instance.attributes["entity_inferred_name"]
        
        for t in feature_functions:
            feature_name = self.feature_prefix +t[0]
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, t[1](s))



        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
















        