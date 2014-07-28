import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from classification.feature import Feature
import logging
import psycopg2

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

class table_is_first_table_feature_generator:
    def __init__(self, **kwargs):
        self.name = "table_is_first_table_feature_generator"
        self.force = kwargs.get("force", True)

    def operate(self, instance):
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        entity_id = instance.attributes["id"]
        instance.feature_groups[self.name] = []
        instance.feature_groups[self.name].append(Feature("IS_FIRST_TABLE", self.is_first_table(entity_id), self.name))

        logging.debug( "Feature count for entity id: %d after %s" %(instance.attributes["id"], self.name))

    def is_first_table(self,entity_id):
        conn = psycopg2.connect(CONN_STRING)
        try:
            cur = conn.cursor()
            params = [entity_id]
            sql = """SELECT t.id
            FROM tables t
            JOIN entities e
            ON t.document_id = e.document_id
            WHERE e.id = %s
            AND e.entity_offset > t.offset
            AND e.entity_offset < t.offset + t.length"""
            cur.execute(sql, params)
            entity_table_id = cur.fetchone()
            sql = """SELECT t.id
            FROM tables t
            JOIN entities e
            ON t.document_id = e.document_id
            WHERE e.id = %s
            ORDER BY t.id
            LIMIT 1"""
            cur.execute(sql, params)
            first_table_id = cur.fetchone()
            return int(entity_table_id == first_table_id)
        except Exception as exp:
            conn.rollback()
            print exp
            raise exp
        finally:
            conn.close()
