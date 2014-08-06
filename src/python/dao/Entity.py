"DAO for Entity in the entities table"
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import psycopg2
import psycopg2.extras
import logging


CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

class Entity:
    def __init__(self, entity_id):
        self.cmd = """
        select id, entity_text, entity_type, entity_offset, entity_length, entity_inferred_name, source,
        document_id, entity_url from entities where id = %s
        """
        conn = psycopg2.connect(CONN_STRING)
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(self.cmd, (entity_id,))
            result = cur.fetchone()
            if result and len(result) > 0:
                self.id = result["id"]
                self.entity_text = result["entity_text"]
                self.entity_type = result["entity_type"]
                self.entity_offset = result["entity_offset"]
                self.entity_length = result["entity_length"]
                self.entity_inferred_name = result["entity_inferred_name"]
                self.source= result["source"]
                self.document_id = result["document_id"]
                self.entity_url = result["entity_url"]
            else:
                raise("No Entity was found with id %d" %(entity_id))
        except Exception as exp:
            logging.exception("Error")
        finally:
            conn.close()
    
    def __str__(self):
        return "Entity id: %d, Entity Text: %s" %(self.id, self.entity_inferred_name)