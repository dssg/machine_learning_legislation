"""
person feature generator
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from util import wiki_tools
from pprint import pprint
import logging, random
import numpy as np
import scipy
import string
import re
from classification.feature import Feature
import csv
from os.path import expanduser


def extract_entities(text):
    """
    Input: entity_text
    Output: calais entity
    """
    import time
    sys.path.insert(0,os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe() ))[0],"../../ner"))))
    from calais import Calais
    API_KEYS = ["wdbkpbpsksskkbm2rpqfm4xa", "mt5qu3e4jdrd6jpc9r9ecama","k9fb7rfh7hpbfp238whuggrr","55rared7un2pnjr23kjtctes"]
    calaises = [Calais(key, submitter="python-calais-demo") for key in API_KEYS]
    entities = []
    calais = calaises[ random.randint(0, len(calaises)-1 ) ]
    try:
        result = calais.analyze(text)
        if result.hasattr('entities'):
            for calais_entity in result.entities:
                e_type = calais_entity['_type']
                entities.append(e_type)
    except:
        logging.exception("failed while calling calais")

    return entities

def calais_feature_dict(extracted_entities):
    """
    Input: list of extracted entities
    Ouput: dictionary of calais entities, count values
    """
    feature_dict = dict()
    for item in extracted_entities:
        feature_dict[item] = feature_dict.get(item, 0)+1

    return feature_dict

def politicians_names():
    """
    Input: 
    Output: tuple of lists of names 
    """
    import csv
    names = list(csv.reader(open('/mnt/data/sunlight/misc/legislators.csv','rU')))
    last_name = set([name[0] for name in names])
    first_name = set([name[1] for name in names])
    first_name_upper = set([name[0].upper() for name in names])
    last_name_upper = set([name[1].upper() for name in names])
    return (last_name, last_name_upper, first_name, first_name_upper)

def politicians_feature(text,lname,lname_upper,fname,fname_upper):
    """
    Input: text
    Output: boolean for politician name in text
    """
    calais_entities = extract_entities(text)
    if 'Person' in calais_entities:
        for name in lname:
            if name in text:
                return 1
        for name in lname_upper:
            if name in text:
                return 1
        for name in fname:
            if name in text:    
                return 1
        for name in fname_upper:
            if name in text:
                return 1
    else:
        return 0

class CalaisFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "politician_calais_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "CALAIS_FEAUTURE_"
        self.lname,self.lname_upper,self.fname,self.fname_upper = politicians_names()

    def operate(self,instance):
        """                                                                               
        given an instance a list of categories as features                                       
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
             
        instance.feature_groups[self.name] = []
        text = instance.attributes["entity_inferred_name"]
        calais_dict = calais_feature_dict(extract_entities(text))
        for key in calais_dict.keys():
            FEATURE_STRING = self.feature_prefix + str(key)
            count_value = calais_dict[key]
            instance.feature_groups[self.name].append(Feature(FEATURE_STRING, count_value,self.name))
        poli_feature = politicians_feature(text,self.lname,self.lname_upper,self.fname,self.fname_upper)
        if poli_feature:
            instance.feature_groups[self.name].append(Feature('POLITICIAN-CALAIS_FEATURE_politician',poli_feature,self.name))
        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
