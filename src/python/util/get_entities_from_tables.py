import text_table_tools 
import path_tools
import csv
import os, sys
import codecs
import random
import psycopg2
import logging






def insert_all(directory, conn):
    

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename == "document.txt" or "." not in filename:

                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                get_entities(filepath, conn)




def get_entities(path, conn):
        if "congress" in path:
            path_util = path_tools.ReportPathUtils(path  = path)
        else:
            path_util = path_tools.BillPathUtils(path  = path)

        docid = path_util.get_db_document_id()
        print path, docid


        fields = ["entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name", "source", "document_id"]
        
        paragrapghs_list = text_table_tools.get_paragraphs(open(path,'r'))
        f_str = open(path,'r').read()
        tables = text_table_tools.identify_tables(paragrapghs_list)


        for table in tables:
            table_offset = table.offset
            try:
                csv_rows =[]
                column_indices = sorted(text_table_tools.get_candidate_columns(table))


                for row in table.rows:
                    row_offset = row.offset
                    clean_row_text = ''

                    csv_row = []

                    for idx in column_indices:
                        cell = row.cells[idx]
                        #offset = table_offset+row_offset+cell.offset
                        #print cell.raw_text, f_str[offset:(offset+cell.length)]
                        if len(cell.clean_text) == 0:
                            continue
                        clean_row_text += cell.clean_text + " | "

                        #csv_row = [cell.raw_text, "table_entity", str(offset), str(cell.length), cell.clean_text, "table", str(docid)]
                        #csv_rows.append(csv_row)

                    csv_row = [clean_row_text[:2048], "table_row", table_offset+row_offset, row.length, clean_row_text[:2048], table.type + "_table", docid]

                    csv_rows.append(csv_row)

                cmd = "insert into entities (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s, %s, %s)"
                cur = conn.cursor()
                cur.executemany(cmd, csv_rows)
                conn.commit()
            except Exception as e:
                print len(clean_row_text)
                print csv_row
                logging.exception("SCREW UP")

    

years = [ "111", "110","109", "108"] 

reports_base="/mnt/data/sunlight/congress_reports/"
bills2008 = "/mnt/data/sunlight/bills/110/bills/hr/hr2764/text-versions/"
bills2009 = "/mnt/data/sunlight/bills/111/bills/hr/hr1105/text-versions/"


CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
conn = psycopg2.connect(CONN_STRING)

insert_all(bills2008, conn);
insert_all(bills2009, conn);

for year in years:
   insert_all(reports_base+year+"/", conn);
conn.close()


