"""
groups instances by a given attribute name
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from instance import Instance

class InstanceGrouper:
    def __init__(self, group_by_list):
        self.group_by_list = group_by_list
        self.groups = {}
        self.GROUP_BY_COLUMN_NA = "GROUP_BY_ATTRIBUTE_MISSING"
        
    def group_instances(self, instances):
        for instance in instances:
            signature = reduce (lambda a, b: a+'|'+b , map(lambda group: str(instance.get(group,self.GROUP_BY_COLUMN_NA)), self.group_by_list ) )
            self.groups[signature] = self.groups.get(signature,[]) + [instance,]
        return self.groups