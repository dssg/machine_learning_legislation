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
        if "congress" in path:
            path_util = path_tools.ReportPathUtils(path  = path)
        else:
            path_util = path_tools.BillPathUtils(path  = path)

        docid = path_util.get_db_document_id()


        fields = ["entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name", "source", "document_id"]
        
        paragrapghs_list = text_table_tools.get_paragraphs(open(path,'r'))
        f_str = open(path,'r').read()
        tables = text_table_tools.identify_tables(paragrapghs_list)


        for table in tables:
            table_offset = table.offset
            try:
                csv_rows =[]
                column_indices = text_table_tools.get_candidate_columns(table)
                for row in table.rows:
                    row_offset = row.offset
                    for idx in column_indices:
                        cell = row.cells[idx]
                        offset = table_offset+row_offset+cell.offset
                        #print cell.raw_text, f_str[offset:(offset+cell.length)]
                        if len(cell.clean_text) == 0:
                            continue
                        csv_row = [cell.raw_text, "table_entity", str(offset), str(cell.length), cell.clean_text, "table", str(docid)]
                        csv_rows.append(csv_row)

                cmd = "insert into entities (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s, %s, %s)"
                cur = conn.cursor()
                cur.executemany(cmd, csv_rows)
                conn.commit()
            except Exception as e:
                print e
                print "SCREW UP"

    

years = [ "111", "110","109", "108"] 

base="/mnt/data/sunlight/congress_reports/"




CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
conn = psycopg2.connect(CONN_STRING)
for year in years:
    insert_all(base+year+"/", conn);
conn.close()


