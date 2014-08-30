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
from matching.string_functions import normalize, tokenize



#number of all caps

def num_all_caps(s, num_chars, tokens, num_tokens):
    return sum(1 for c in s if c.isupper())

# number of dots
def num_dots(s, num_chars, tokens, num_tokens):
    return sum(1 for c in s if c == '.')

def percent_dots(s, num_chars, tokens, num_tokens):
    if num_chars > 0:
        return num_dots(s, num_chars, tokens, num_tokens)/num_chars
    else:
        return 0

#num_words

def num_words(s, num_chars, tokens, num_tokens):
    return num_tokens

#number of digits
def num_digits(s, num_chars, tokens, num_tokens):
    return sum(1 for c in s if c.isdigit())

def percent_digits(s, num_chars, tokens, num_tokens):
    if num_chars > 0:
        return num_digits(s, num_chars, tokens, num_tokens)/len(s)
    else:
        return 0


def starts_with_for(s, num_chars, tokens, num_tokens):
    if num_tokens == 0.0:
        return False

    first_token = tokens[0]
    return first_token == 'for' or first_token == 'For'


def percent_capitalized(s, num_chars, tokens, num_tokens):
    if num_tokens == 0.0:
        return 0
    count = 0.0

    for token in tokens:
        if len(token)>0:
            if token[0].isupper():
                count +=1.0
    return count/num_tokens

def alpha_tokens_count(s, num_chars, tokens, num_tokens):
    return len([t for t in tokens if t.isalpha()])

def percent_alpha_tokens(s, num_chars, tokens, num_tokens):
    if num_tokens > 0:
        return len([t for t in tokens if t.isalpha()]) / num_tokens
    else:
        return 0

def non_alpha_tokens_count(s, num_chars, tokens, num_tokens):
    return len([t for t in tokens if not t.isalpha()])

def percent_non_alpha_tokens(s, num_chars, tokens, num_tokens):
    if num_tokens > 0:
        return len([t for t in tokens if not t.isalpha()]) / num_tokens
    else:
        return 0

def get_len(s, num_chars, tokens, num_tokens):
    return num_chars

feature_functions = [
('num_all_caps', num_all_caps), 
('num_dots', num_dots), 
('length', get_len), 
('num_words', num_words), 
('num_digits', num_digits),
('starts_with_for', starts_with_for), 
('percent_capitalized', percent_capitalized),
('alpha_tokens_count', alpha_tokens_count),
('non_alpha_tokens_count', non_alpha_tokens_count),
('percent_dots', percent_dots), 
('percent_digits', percent_digits),
('percent_alpha_tokens', percent_alpha_tokens), 
('percent_non_alpha_tokens', percent_non_alpha_tokens)
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
        num_chars = float(len(s))
        tokens = tokenize(normalize(s))
        num_tokens = float(len(tokens))
        
        for t in feature_functions:
            feature_name = self.feature_prefix +t[0]
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, t[1](s, num_chars, tokens, num_tokens))



        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
















        