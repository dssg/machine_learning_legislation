import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import string_functions

class EarmarkAttributes:
    def __init__(self, earmark):
        self.earmark = earmark
        self.attributes = {}
        self.build_attributes()
    
    def __str__(self):
        return self.earmark.__str__()
        
    def build_attributes(self):
        self.attributes["normalized_sd"] = string_functions.normalize(self.earmark.short_description)
        self.attributes["sd_shingles"] = string_functions.shinglize(self.attributes["normalized_sd"])
        self.attributes["normalized_fd"] = string_functions.normalize(self.earmark.full_description)
        self.attributes["fd_shingles"] = string_functions.shinglize(self.attributes["normalized_fd"])
        self.attributes["normalized_recepient"] = string_functions.normalize(self.earmark.recepient)
        self.attributes["recepient_shingles"] = string_functions.shinglize(self.attributes["normalized_recepient"])
         