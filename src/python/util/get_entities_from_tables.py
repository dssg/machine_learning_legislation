import text_table_tools 
import path_tools
import csv
import os, sys
import codecs
import random
import psycopg2







def insert_all(directory, conn):
    

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            if "xml" not in filename:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                print filepath
                get_entities(filepath, conn)




def get_entities(path, conn):
    try:
        if "congress" in path:
            path_util = path_tools.ReportPathUtils(path  = path)
        else:
            path_util = path_tools.BillPathUtils(path  = path)

        docid = path_util.get_db_document_id()


        fields = ["entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name", "source", "document_id"]
        csv_rows =[]
        paragrapghs_list = text_table_tools.get_paragraphs(open(path,'r'))
        f_str = open(path,'r').read()
        tables = text_table_tools.identify_tables(paragrapghs_list)


        for table in tables:
            text = "".join(table.content)
            prev_entitities = {}
            entities = text_table_tools.get_candidate_entities(table)
            for e in entities:
                paragraph_offset = text.find(e, prev_entitities.get(e, 0))
                prev_entitities[e] = paragraph_offset + len(e)
                offset = table.offset+paragraph_offset
                csv_row = [e, "table_entity", str(offset), len(e), e, "table", str(docid)]
                csv_rows.append(csv_row)

        cmd = "insert into entities (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s, %s, %s)"
        cur = conn.cursor()
        cur.executemany(cmd, csv_rows)
        conn.commit()
    except Exception as e:
        print e
        print "SCREW UP"
    

years = [ "110", "111","109", "108"] 

base="/mnt/data/sunlight/bills/"




CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
conn = psycopg2.connect(CONN_STRING)
for year in years:
    insert_all(base+year+"/", conn);
conn.close()


