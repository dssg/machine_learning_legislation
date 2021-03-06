"""
wikipedia categories feature generator
"""
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from util import wiki_tools
from util import configuration
from pprint import pprint
import logging
import numpy as np
import scipy
import psycopg2
from classification.feature import Feature


class wikipedia_categories_feature_generator:
    def __init__(self, **kwargs):
        self.name = "wikipedia_categories_feature_generator"
        self.depth = kwargs.get("depth", 3)
        self.distinguish_levels = kwargs.get("distinguish_levels", True)
        self.force = kwargs.get("force", True)
        self.feature_prefix = "WIKI_CATEGORY_"
        self.NO_WIKI_PAGE_FEATURE = "NO_WIKIPEDIA_PAGE_WAS_FOUND"
        self.CONN_STRING = configuration.get_connection_string()

    def entity_id_to_wikipage(self, entity_id):
        """
        given an entity id, returns the corresponding wikipedia page.
        if no page is found, None returned
        """
        conn = psycopg2.connect(self.CONN_STRING)
        try:
            cmd = "select wikipedia_page from entity_wikipedia_page where entity_id = %s"
            cur = conn.cursor()
            cur.execute(cmd, (entity_id,))
            result = cur.fetchone()
            if result and len(result) > 0:
                return result[0]
            else:
                return None
        except Exception as exp:
            conn.rollback()
            print exp
            raise exp
        finally:
            conn.close()


    def entity_text_to_wikipage (self, entity_text):
        """
        given an entity text, returns the corresponding wikipedia page.
        if no page is found, None returned
        """
        conn = psycopg2.connect(self.CONN_STRING)
        try:
            cmd = "select wikipedia_page from entity_wikipedia_page where entity_text = %s"
            cur = conn.cursor()
            cur.execute(cmd, (entity_text,))
            result = cur.fetchone()
            print result
            if result and len(result) > 0:
                return result[0]
            else:
                return None
        except Exception as exp:
            conn.rollback()
            print exp
            raise exp
        finally:
            conn.close()


    def operate(self, instance):
        """
        given an instance a list of categories as features
        """
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        #page_title = self.entity_id_to_wikipage(instance.attributes["id"])
        page_title = self.entity_text_to_wikipage(instance.attributes["entity_inferred_name"])
        logging.debug("TEXT: %s" % instance.attributes["entity_inferred_name"])
        logging.debug( "WIKI PAGE: %s" % page_title)
        instance.feature_groups[self.name] = {}
        if page_title:
            instance.attributes["matching_wiki_page"] = page_title
            categories = wiki_tools.get_category_hierarchy(page_title, self.depth)


            if self.distinguish_levels:
                for i in range(len(categories)):
                    level = categories[i]
                    for cat in level:
                        feature_name = self.feature_prefix +str(i+1)+"_"+cat
                        instance.feature_groups[self.name][feature_name] =  Feature(feature_name, 1)
            else:
                for level in categories:
                    for cat in level:
                        feature_name = self.feature_prefix + cat
                        instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1)
        else:
            instance.feature_groups[self.name][self.NO_WIKI_PAGE_FEATURE] = Feature(self.NO_WIKI_PAGE_FEATURE,1)

        logging.debug( "Feature count %d for entity id: %d after %s" %(instance.feature_count(),instance.attributes["id"], self.name))

