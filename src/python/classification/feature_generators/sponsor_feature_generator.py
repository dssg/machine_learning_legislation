import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from matching import string_functions
import csv
from classification.feature import Feature
import logging


class SponsorFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "sponsor_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "SPONOSR_FEAUTURE_"
        self.sponsors = set()
        for row in csv.reader(open("/mnt/data/sunlight/misc/legislators.csv", 'rU')):
            self.sponsors.add(row[0])
        self.sponsors = self.sponsors.difference(set(['Law', 'Page', 'New']))

    def operate(self,instance):
        """                                                                               
        given an instance a list of categories as features                                       
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
             
        instance.feature_groups[self.name] = {}


        text = instance.attributes["entity_inferred_name"]
        
        instance.feature_groups[self.name]['SPONSOR_FEAUTURE_has_sponsor'] = Feature('SPONOSR_FEAUTURE_has_sponsor', self.has_sponsor(text))
        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))



    def has_sponsor(self, text):
        """
        Input: text
        Output: boolean for politician name in text
        """

        tokens = string_functions.tokenize(string_functions.normalize_no_lower(text))
        for token in tokens:
            if token in self.sponsors:
                print token
                return 1
        return 0


    