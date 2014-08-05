import os, sys, inspect
#sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
print sys.path
from classification.instance import Instance
import logging
from nltk import metrics, stem, tokenize
from nltk.tokenize import WhitespaceTokenizer
import re

class ShinglesGenerator:
    def __init__(self, **kwargs):
        """
        params: dictionary of parameters to configure the feature generator
        """
        self.name = "ShinglesCreator"
        self.attribute = kwargs.get("attribute")
        self.prefix = "shingles_"
        self.ngrams = kwargs.get('ngrams', 2)
        
    def operate(self, instance_object):
        instance_object.attributes[self.prefix+self.attribute] = self.shinglize(instance_object.attributes[self.attribute], self.ngrams)
        
    def normalize(self,s):
        for p in string.punctuation:
            s = s.replace(p, ' ')
        s = re.sub(r'[ ]{2,}', " ", s)
        return s.lower().strip()
        
    def tokenize(self,s):
        return WhitespaceTokenizer().tokenize(s)
        
    def shinglize(self,s, n, tokenizer=self.tokenize):
        """
        return size n shingles for the string s
        """
        shingles = set()
        tokens = tokenizer(s)
        for i in range(len(tokens) - n + 1):
            shingles.add('_'.join(tokens[i:i+n]))
        return shingles