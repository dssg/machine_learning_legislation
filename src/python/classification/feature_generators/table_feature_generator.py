"""
table headers feature generator
"""

import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from classification.feature import Feature
import logging

class table_headers_feature_generator:
    def __init__(self, **kwargs):
        self.name = "table__headers_feature_generator"
        self.feature_prefix = "TABLE_HEADER_"
        self.no_header_feature = "NO_HEADERS_FOUND"

    def operate(self, instance):
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        entity_id = instance.attributes["id"]

        table = self.get_table_from_entity_id(entity_id)
        headers = table.headers
        if headers:
            instance.feature_groups[self.name] += [Feature(self.feature_prefix + header, 1, self.name) for header in headers]
        else:
            instance.feature_groups[self.name].append(Feature(self.no_header_feature, 1, self.name))
        logging.debug( "Feature count for entity id: %d after %s" %(instance.attributes["id"], self.name))

    def get_table_from_entity_id(entity_id):
        pass
        # TODO
