import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from pprint import pprint
import logging
from classification.feature import Feature
import itertools
import matching.string_functions as string_functions


class JaccardFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "JACCARD_FG"
        
    def operate(self, instance):
        entity_attr = instance.attributes["entity"]
        earmark_attr = instance.attributes["earmark"]
        instance.feature_groups[self.name] = {}
        lst_ent_shingles = ["shingles"]
        lst_earmark_shingles = ["sd_shingles", "fd_shingles", "recepient_shingles"]
        pairs = itertools.product(lst_ent_shingles, lst_earmark_shingles)
        for pair in pairs:
            feature_name = self.name + "_" + pair[0] + "_" + pair[1]
            jaccard_score = string_functions.jaccard_distance(entity_attr.attributes[pair[0]], earmark_attr.attributes[pair[1]])
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, jaccard_score)
        
        pairs = itertools.product(["cell_shingles"], lst_earmark_shingles)
        for pair in pairs:
            highest_jaccard = 0
            for i in range(len(entity_attr.attributes[pair[0]])):
                jaccard_score = string_functions.jaccard_distance(entity_attr.attributes[pair[0]][i], earmark_attr.attributes[pair[1]])
                if jaccard_score > highest_jaccard:
                    highest_jaccard = jaccard_score
            feature_name = self.name + "_" + pair[0] + "_" + pair[1]
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, highest_jaccard)

        logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))

                