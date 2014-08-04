import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../.."))))
from classification.feature import Feature
import logging
import psycopg2
import util.text_table_tools as ttt
from StringIO import StringIO

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
                self.paragraphs = ttt.get_paragraphs_from_string(content[0])
                return ttt.identify_tables(self.paragraphs)[0]
            else:
                return ttt.Table()
        except Exception as exp:
            conn.rollback()
            print exp
            raise exp
        finally:
            conn.close()

class table_header_feature_generator:
    def __init__(self, **kwargs):
        self.name = "table_headers_feature_generator"
        self.force = kwargs.get("force", True)
        self.feature_prefix = "TABLE_HEADER_"
        self.no_header_feature = "NO_HEADERS_FOUND"

    def operate(self, instance):
        logging.debug("Enter table headers.")
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        entity_id = instance.attributes["id"]
        instance.feature_groups[self.name] = {}

        headers = self.get_table_headers_from_entity_id(entity_id)
        if headers:
            for header in headers:
                feature_name = self.feature_prefix + header
                instance.feature_groups[self.name][feature_name] = Feature(feature_name, 1) 
        else:
            instance.feature_groups[self.name][self.no_header_feature] = Feature(self.no_header_feature, 1)
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

class table_is_first_table_feature_generator:
    def __init__(self, **kwargs):
        self.name = "table_is_first_table_feature_generator"
        self.force = kwargs.get("force", True)

    def operate(self, instance):
        logging.debug("Enter is first table.")
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        entity_id = instance.attributes["id"]
        instance.feature_groups[self.name] = {}
        instance.feature_groups[self.name]['IS_FIRST_TABLE'] = Feature("IS_FIRST_TABLE", self.is_first_table(entity_id))
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

class row_contains_president_feature_generator(table_feature_generator):
    def __init__(self, **kwargs):
        self.name = "row_contains_president_feature_generator"
        self.force = kwargs.get("force", True)

    def operate(self, instance):
        logging.debug("Enter row contains president.")
        if not self.force and instance.feature_groups.has_key(self.name):
            return
        entity_id = instance.attributes["id"]
        table = self.get_entity_table(entity_id)
        instance.feature_groups[self.name] = {}
        for row in table.rows:
            pass #print "Entity: %s (%s) .\n\n Row: %s" % (instance.attributes["entity_text"], instance.attributes["id"], row.raw_text)
        entity_row = [row for row in table.rows if [cell for cell in row.cells if instance.attributes["entity_text"] in cell.clean_text]]
        if entity_row:
            row = entity_row[0]
            if "president" in row.raw_text.lower():
                instance.feature_groups[self.name]['PRESIDENT_IN_ROW'] = Feature("PRESIDENT_IN_ROW", 1)

            logging.debug( "Feature count for entity id: %d after %s" %(instance.attributes["id"], self.name))
        else:
            instance.feature_groups[self.name].append(Feature("PRESIDENT_IN_ROW", 0, self.name))

