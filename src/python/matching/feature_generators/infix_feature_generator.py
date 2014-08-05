import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from pprint import pprint
import logging
from classification.feature import Feature
import itertools
import matching.string_functions as string_functions

class InfixFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "INFIX_FG"
        
    def operate(self, instance):
        entity_attr = instance.attributes["entity"]
        earmark_attr = instance.attributes["earmark"]
        instance.feature_groups[self.name] = {}
        lst_ent_attrs = ["normalized_entity_inferred_name"]
        lst_earmark_attrs = ["normalized_sd", "normalized_fd", "normalized_recepient"]
        pairs = itertools.product(lst_ent_attrs, lst_earmark_attrs)
        for pair in pairs:
            feature_name = self.name + "_" + pair[0] + "_" + pair[1]
            feature_value = 0
            if string_functions.is_infix(pattern=pair[0], text=pair[1]):
                feature_value = 1
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, feature_value)
        
        pairs = itertools.product(["normalized_cells"], lst_earmark_attrs)
        max_cells_infix_count = 0
        for pair in pairs:
            infix_count = 0
            for i in range(len(entity_attr.attributes[pair[0]])):
                if string_functions.is_infix(pattern=pair[0][i], text=pair[1]):
                    infix_count +=1
            if infix_count > max_cells_infix_count:
                max_cells_infix_count = infix_count
            feature_name = self.name + "_" + pair[0] + "_" + pair[1]
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, infix_count)
        
        feature_name = self.name + "_max_cells_infix_count"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, max_cells_infix_count)
        
        feature_name = self.name + "_max_cells_infix_percenetage"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1.0 * max_cells_infix_count / len(entity_attr.attributes['normalized_cells']))
                