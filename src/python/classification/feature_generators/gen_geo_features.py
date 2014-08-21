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
import csv
from os.path import expanduser
from matching.string_functions import normalize



def get_states_from_csv():
    full = set()
    full_upper = set()
    abbr = set()

    absolute_path = os.path.dirname(os.path.abspath(__file__))
    states_path = os.path.join(absolute_path, "../../../../data/states.csv")
    r = csv.reader(open(states_path))
    for row in r:
        full_upper.add(row[0].upper())
        full.add(row[0])
        abbr.add(row[1])
    return (full, full_upper, abbr)


def get_cities_from_csv():
    cities = set()
    cities_upper = set()

    absolute_path = os.path.dirname(os.path.abspath(__file__))
    cities_path = os.path.join(absolute_path, "../../../../data/cities.csv")

    r = csv.reader(open(cities_path))
    for row in r:
        cities_upper.add(row[1].upper())
        cities.add(row[1])
    return (cities, cities_upper)



def geo_inferred_text_has_state(tokens, full, full_upper, abbr):
    ret = 0
    for t in tokens:
        if t in full or t in abbr or t in full_upper:
            ret = 1
    #print "Has State: ", ret
    return ret


def geo_inferred_text_has_county(s):
    ret = 0
    if 'county' in s or 'County' in s or 'COUNTY' in s:
        ret = 1
    
    #print "Has County: ", ret
    return ret

def geo_inferred_text_ends_with_state(tokens, abbr, full):
    if len(tokens) == 0:
        return 0
    last_token = tokens[-1]
    return last_token in abbr or last_token in full



def geo_inferred_text_has_city(s, cities, cities_upper):
    ret = 0
    for c in cities:
        if c in s:
            ret = 1
            #print c
    for c in cities_upper:
        if c in s:
            ret = 1
            #print c
    #print "Has City: ", ret
    return ret





class geo_feature_generator:
    def __init__(self, **kwargs):
        self.name = "geo_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "GEO_FEAUTURE_"

        self.full, self.full_upper, self.abbr = get_states_from_csv()
        self.cities, self.cities_upper = get_cities_from_csv()
            
    

    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        instance.feature_groups[self.name] = {}

        s = instance.attributes["entity_inferred_name"]
        tokens = normalize(s).split(' ')

        
        
        instance.feature_groups[self.name]['GEO_FEAUTURE_geo_inferred_text_has_state'] = Feature('GEO_FEAUTURE_geo_inferred_text_has_state', geo_inferred_text_has_state(tokens, self.full, self.full_upper, self.abbr))
        instance.feature_groups[self.name]['GEO_FEAUTURE_geo_inferred_text_has_county'] = Feature('GEO_FEAUTURE_geo_inferred_text_has_county', geo_inferred_text_has_county(s))
        instance.feature_groups[self.name]['GEO_FEAUTURE_geo_inferred_text_has_city'] = Feature('GEO_FEAUTURE_geo_inferred_text_has_city', geo_inferred_text_has_city(s, self.cities, self.cities_upper))
        instance.feature_groups[self.name]['GEO_FEAUTURE_geo_inferred_text_ends_with_state'] = Feature('GEO_FEAUTURE_geo_inferred_text_ends_with_state', geo_inferred_text_ends_with_state(tokens, self.abbr, self.full))


        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))



	

