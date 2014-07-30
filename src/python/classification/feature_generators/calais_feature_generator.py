"""
person feature generator

"""
import os, sys, inspect
sys.path.insert(0,os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe() ))[0],"../../ner"))))
from calais import Calais
calaises = [Calais(key, submitter="python-calais-demo") for key in API_KEYS]
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
import csv
from os.path import expanduser


def extract_entities(text):
    """
    Input: entity_text
    Output: calais entity
    """
    entities = []
    try:
        calais = calaises[ random.randint(0, len(calaises)-1 ) ]
        result = calais.analyze(text)
        for calais_entity in result.entities:
            e_name = calais_entity['name']
            entities.append(e_name)
        return entities

    except:
        return []

def calais_feature_dict(extracted_entities):
    """
    Input: list of extracted entities
    Ouput: dictionary of calais entities, count values
    """
    unique_entities = set(extracted_entities)
    feature_dict = dict()
    for item in extracted_entities:
        if item not in feature_dict:
            feature_dict[item]=1
        else:
            feature_dict[item]=feature_dict[item]+1
    return feature_dict

def politicians_names():
    """
    Input: 
    Output: tuple of lists of names 
    """
    poli_df = pd.read_csv('/mnt/data/sunlight/misc/legislators.csv',delimiter=',')
    last_name = set()
    last_name_upper = set()
    first_name = set()
    first_name_upper = set()
    for row in poli_df.iterrows():
        lname = row[1].ix['last_name']
        fname = row[1].ix['first_name']
        last_name.add(lname)
        last_name_upper.add(lname.upper())
        first_name.add(fname)
        first_name_upper.add(fname.upper())
    return (last_name, last_name_upper, first_name, first_name_upper)

def politicians_feature(text,lname,lname_upper,fname,fname_upper):
    """
    Input: text
    Output: boolean for politician name in text
    """
    calais_entities = extract_entities(text)
    if 'Person' in calais_entities:
        for name in last_name:
            if name in text:
                return 1
        for name in last_name_upper:
            if name in text:
                return 1
        for name in first_name:
            if name in text:    
                return 1
        for name in first_name_upper:
            if name in text:
                return 1
    else:
        return 0

class politician_calais_feature_generator:
    def __init__(self, **kwargs):
        self.name = "politician_calais_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "PERSON-CALAIS_FEAUTURE_GENERATOR"
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
                 FEATURE_STRING = 'CALAIS_FEATURE_' + str(key)
                 count_value = calais_dict[key]
                 instance.feature_groups[self.name].append(Feature(FEATURE_STRING, count_value,self.name))
             poli_feature = politicians_feature(text,self.lname,self.lname_upper,self.fname,self.fname_upper)
             instance.feature_groups[self.name].append(Feature('POLITICIAN_FEATURE',poli_feature,self.name))
             logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
