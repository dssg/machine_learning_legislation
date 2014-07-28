import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from classification.feature import Feature
import logging
import psycopg2
import util.text_table_tools as ttt

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

class table_feature_generator:
    """
    base class for utily methods for table features
    """
    def get_entity_table(self, entity_id):
        conn = psycopg2.connect(CONN_STRING)
        try:
            cur = conn.cursor()
            params = [entity_id]
            sql = """SELECT content
                FROM tables t
                JOIN entities e
                ON t.document_id = e.document_id
                WHERE e.id = %s
                AND e.entity_offset > t.offset
                AND e.entity_offset < t.offset + t.length"""
            cur.execute(sql, params)
            content = cur.fetchone()
            if content:
                return ttt.identify_tables(content)[0]
            else:
                return Table()
        except Exception as exp:
            conn.rollback()
            print exp
            raise exp
        finally:
            conn.close()
