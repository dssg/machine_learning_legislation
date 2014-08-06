import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import string_functions

class EntityAttributes:
    def __init__(self, entity):
        self.entity = entity
        self.attributes = {}
        self.build_attributes()
        
    def __str__(self):
        return self.entity.__str__()
        
    def build_attributes(self):
        self.attributes["normalized_entity_inferred_name"] = string_functions.normalize(self.entity.entity_inferred_name)
        self.attributes["shingles"] = string_functions.shinglize(self.attributes["normalized_entity_inferred_name"])
        self.attributes["normalized_cells"] = [string_functions.normalize(cell) for cell in  self.entity.entity_inferred_name.split(' | ') ]
        self.attributes["cell_shingles"] = [string_functions.shinglize(cell) for cell in self.attributes["normalized_cells"] ]
        
