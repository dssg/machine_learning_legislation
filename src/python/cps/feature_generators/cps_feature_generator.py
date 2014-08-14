import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
import logging
import math
from classification.feature import Feature

class IsSameFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "IS_SAME_FG"
        self.fields = kwargs.get('fields',[])
        
    def operate(self, instance):
        student1 = instance.attributes['student1']
        student2 = instance.attributes['student2']
        instance.feature_groups[self.name] = {}
        for field in self.fields:
            if getattr(student1,field) == getattr(student2, field):
                feature_name = self.name + "_" + field
                instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1)
        logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))
        
class AbsoluteDifferenceFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "ABS_DIFFERENCE_FG"
        self.fields = kwargs.get('fields',[])
    def operate(self, instance):
        student1 = instance.attributes['student1']
        student2 = instance.attributes['student2']
        instance.feature_groups[self.name] = {}
        for field in self.fields:
            difference = abs( getattr(student1,field) - getattr(student2, field))
            feature_name = self.name + "_" + field
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, difference)
        logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))
        

class DistanceFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "DISTANCE_FG"
    def operate(self, instance):
        student1 = instance.attributes['student1']
        student2 = instance.attributes['student2']
        instance.feature_groups[self.name] = {}
        try:
            distance = distance_on_unit_sphere(student1.Latitude, student1.Longitude, student2.Latitude, student2.Longitude )
            feature_name = self.name
            instance.feature_groups[self.name][feature_name] = Feature(feature_name, distance) 
        except Exception as ex:
            logging.exception("Failed to compute distance")
        logging.debug( "Feature count %d for entity after %s" %(instance.feature_count(), self.name))
        
class OtherFeaturesFeatureGenerator:
    def __init__(self, **kwargs):
        self.name = "OTHER"
    def operate(self, instance):
        student1 = instance.attributes['student1']
        student2 = instance.attributes['student2']
        instance.feature_groups[self.name] = {}
        feature_name = self.name + "_BOTH_ENGLISH"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, both_equal_with_value(student1.Language, student2.Language, 'English') ) 
        feature_name = self.name + "_BOTH_SPANISH"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, both_equal_with_value(student1.Language, student2.Language, 'Spanish') )
        feature_name = self.name + "_BOTH_MALE" 
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, both_equal_with_value(student1.Gender, student2.Gender, 'Male') )
        feature_name = self.name + "_BOTH_BORN_OUTSIDE"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, not both_equal_with_value(student1.BirthCountry, student2.BirthCountry, 'United States'))
        feature_name = self.name + "_BOTH_SPANISH_AT_HOME"
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, both_equal_with_value(student1.HomeLanguage, student2.HomeLanguage, 'Spanish'))
        feature_name = self.name + "_ZIPCODE_%d"%(student1.ZipCode)
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1)
        feature_name = self.name + "_ZIPCODE_%d"%(student2.ZipCode)
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1)
        feature_name = self.name + "_SCHOOL_KEY_%d"%(student2.ThisGradeSchoolKey)
        instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1)
        
        
        
        

def both_equal_with_value(var1, var2, value):
    return var1 == var2 == value        
            

def distance_on_unit_sphere(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    return arc