import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from matching import string_functions
import csv
from classification.feature import Feature
import logging
import re

class SponsorFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "sponsor_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "SPONOSR_FEAUTURE_"
        self.sponsors = set()

        #absolute_path = os.path.dirname(os.path.abspath(__file__))
        #legislators_path = os.path.join(absolute_path,"../../../../data/legislators.csv")

        #for row in csv.reader(open(legislators_path, 'rU')):
        #    self.sponsors.add(row[0])
        #self.sponsors = self.sponsors.difference(set(['Law', 'Page', 'New', 'Fort', 'Camp', 'Field']))

        absolute_path = os.path.dirname(os.path.abspath(__file__))
        senator_path = os.path.join(absolute_path, "../../../../data/senators.csv")

        for row in csv.reader(open(senator_path, 'r')):
            congress = int(row[0])
            if congress > 109:
                sen = re.split('[:;, ]', row[1])[0].title()
                if sen.isalpha():
                    self.sponsors.add(sen)


        rep_path = os.path.join(absolute_path, "../../../../data/representatives.csv")
        for row in csv.reader(open(rep_path, 'r')):
            congress = int(row[0])
            if congress > 109:
                rep = re.split('[:;, ]', row[1])[0].title()
                if rep.isalpha():
                    self.sponsors.add(rep)

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
        cells = text.split(' | ')
        for cell in cells:
            tokens = re.split('[:;, ]', cell)
            n = len(tokens)
            num_sponsors = 0.0
            for token in tokens:
                if token in self.sponsors:
                    num_sponsors +=1
            if num_sponsors/n > 0.7:
                return 1
        return 0


    