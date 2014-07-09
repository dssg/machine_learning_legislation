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
        path = "/mnt/data/sunlight/test_set_tables/dots2.txt"


        fields = ["entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name", "source", "document_id"]
        csv_rows =[]
        paragrapghs_list = text_table_tools.get_paragraphs(open(path,'r'))
        f_str = open(path,'r').read()
        tables = text_table_tools.identify_tables(paragrapghs_list)


        for table in tables:
            column_indices = text_table_tools.get_candidate_columns(table)
            print "cloumn indices: ", column_indices
            for row in table.rows:
                for idx in column_indices:
                    cell = row.cells[idx]
                    print "cell: ", cell.clean_text
                    csv_row = [cell.clean_text, "table_entity", str(cell.offset), str(cell.length), cell.clean_text, "table", str(docid)]
                    csv_rows.append(csv_row)

        cmd = "insert into entities (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s, %s, %s)"
        cur = conn.cursor()
        cur.executemany(cmd, csv_rows)
        exit()
        conn.commit()
    except Exception as e:
        print e
        print "SCREW UP"
    

years = [ "110", "111","109", "108"] 

base="/mnt/data/sunlight/congress_reports/"




CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
conn = psycopg2.connect(CONN_STRING)
for year in years:
    insert_all(base+year+"/", conn);
conn.close()


