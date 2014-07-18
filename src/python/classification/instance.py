"""
instance class
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))

class Instance:
    def __init__(self , entity = None, target_class = 0):
        self.target_class = target_class
        self.feature_groups = {}
        self.attributes = {}
        if entity:
            self.fill_attributes_from_entity(entity)
            
    def __str__(self):
        return "Id:%d , Class: %d, features count:%d, feature names: %s" %(self.attributes['id'], self.target_class, self.feature_count(), self.feature_names() )
        
    def feature_count(self):
        n = 0
        for k, v in self.feature_groups.iteritems():
            n += len(v)
        return n
        
    def feature_names(self):
        names = []
        for k,v in self.feature_groups.iteritems():
            for f in v:
                names.append(f.name)
        return ", ".join(names)
    
    def fill_attributes_from_entity(self, entity):
        """
        fills the attribute dictionary with information about entity
        """
        self.attributes["id"] = entity.id
        self.attributes["entity_text"] = entity.entity_text
        self.attributes["entity_type"] = entity.entity_type
        self.attributes["entity_offset"] = entity.entity_offset
        self.attributes["entity_length"] = entity.entity_length
        self.attributes["entity_inferred_name"] = entity.entity_inferred_name
        self.attributes["source"] = entity.source
        self.attributes["document_id"] = entity.document_id
        self.attributes["entity_url"] = entity.entity_url
