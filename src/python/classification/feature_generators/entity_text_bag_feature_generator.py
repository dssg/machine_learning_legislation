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
from matching.string_functions import normalize_no_lower, tokenize
import csv



class unigram_feature_generator:
    def __init__(self, **kwargs):
        self.name = "unigram_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "UNIGRAM_"
        self.forbidden = set()

        absolute_path = os.path.dirname(os.path.abspath(__file__))
        states_path = os.path.join(absolute_path, "../../../../data/states.csv")

        r = csv.reader(open(states_path))
        for row in r:
            self.forbidden.add(row[0].upper())
            self.forbidden.add(row[0])
            self.forbidden.add(row[1])

        cities_path = os.path.join(absolute_path, "../../../../data/cities.csv")


        r = csv.reader(open(cities_path))
        for row in r:
            self.forbidden.add(row[1].upper())
            self.forbidden.add(row[1])




        absolute_path = os.path.dirname(os.path.abspath(__file__))
        senator_path = os.path.join(absolute_path, "../../../../data/senators.csv")

        for row in csv.reader(open(senator_path, 'r')):
            congress = int(row[0])
            if congress > 109:
                sen = re.split('[:;, ]', row[1])[0].title()
                if sen.isalpha():
                    self.forbidden.add(sen)


        rep_path = os.path.join(absolute_path, "../../../../data/representatives.csv")
        for row in csv.reader(open(rep_path, 'r')):
            congress = int(row[0])
            if congress > 109:
                rep = re.split('[:;, ]', row[1])[0].title()
                if rep.isalpha():
                    self.forbidden.add(rep)


            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        instance.feature_groups[self.name] = {}

        tokens = tokenize(normalize_no_lower(instance.attributes["entity_inferred_name"]))

        for token in tokens:
            if token not in self.forbidden:
                feature_name = self.feature_prefix +token.lower()
                instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1) 

       

        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))



class bigram_feature_generator:
    def __init__(self, **kwargs):
        self.name = "bigram_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "BIGRAM_"
            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        instance.feature_groups[self.name] = {}

        entity_text = normalize(instance.attributes["entity_inferred_name"])
        tokens = entity_text.split(' ')
        for i in range(len(tokens)-1):
            feature_name = self.feature_prefix +tokens[i]+"_"+tokens[i+1]
            instance.feature_groups[self.name][feature_name]  = Feature(feature_name, 1) 
        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))
        