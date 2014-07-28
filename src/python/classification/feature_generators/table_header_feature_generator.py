"""
table headers feature generator
"""

import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from classification.feature import Feature
import logging
import psycopg2

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

class table_header_feature_generator:
    def __init__(self, **kwargs):
        self.name = "table_headers_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "TABLE_HEADER_"
        self.no_header_feature = "NO_HEADERS_FOUND"

    def operate(self, instance):
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        entity_id = instance.attributes["id"]
        instance.feature_groups[self.name] = []

        headers = self.get_table_headers_from_entity_id(entity_id)
        if headers:
            instance.feature_groups[self.name] += [Feature(self.feature_prefix + header, 1, self.name) for header in headers]
        else:
            instance.feature_groups[self.name].append(Feature(self.no_header_feature, 1, self.name))
        logging.debug( "Feature count for entity id: %d after %s" %(instance.attributes["id"], self.name))

    def get_table_headers_from_entity_id(self,entity_id):
        conn = psycopg2.connect(CONN_STRING)
        try:
            cur = conn.cursor()
            params = [entity_id]
            sql = """SELECT headers
                FROM tables t
                JOIN entities e
                ON t.document_id = e.document_id
                WHERE e.id = %s
                AND e.entity_offset > t.offset
                AND e.entity_offset < t.offset + t.length"""
            cur.execute(sql, params)
            headers = cur.fetchone()
            if headers:
                if len(headers[0].split(",")) > 1:
                    return [h.lower() for h in headers[0].split(",")]
                else:
                    return headers[0]
            else:
                return None
        except Exception as exp:
            conn.rollback()
            print exp
            raise exp
        finally:
            conn.close()
