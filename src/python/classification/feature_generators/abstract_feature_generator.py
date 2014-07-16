"""
skeleton for all feature generators to follow
They must inherit this class
"""
import os, sys, inspect
#sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
print sys.path
from classification.instance import Instance

class abstract_feature_generator:
    def __init__(self, **kwargs):
        """
        params: dictionary of parameters to configure the feature generator
        """
        self.name = "abstract_feature_generator"
    
    def operate(self, instance_object):
        """
        operates on an instances and append features
        """
        pass
