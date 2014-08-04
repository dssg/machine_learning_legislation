"""
feature for classification
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))

class Feature:
    def __init__(self, name = "", value=0.0):
        self.name = name
        self.value = value
