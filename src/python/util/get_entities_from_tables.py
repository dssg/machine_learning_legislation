import text_table_tools 
import path_tools
import csv
import os, sys
import codecs
import random
import psycopg2
import logging

import configuration
CONN_STRING =  configuration.get_connection_string()




def insert_all(directory, conn):
    

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename == "document.txt" or "." not in filename:

                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                get_entities(filepath, conn)



def get_row_entity_text_and_entity_inferred_name(row, column_indices):
    entity_inferred_name = ''
    entity_text = ''

    for i in range(len(row.cells)):
        cell = row.cells[i]
        entity_text += cell.clean_text + " | "
        if i in column_indices:
            entity_inferred_name += cell.clean_text + " | "

    entity_text = entity_text[:-3]
    entity_inferred_name = entity_inferred_name[:-3]
    return entity_text, entity_inferred_name


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
                    (entity_text, entity_inferred_name) = get_row_entity_text_and_entity_inferred_name(row, column_indices)
                    csv_row = [entity_text[:2048], "table_row", table_offset+row.offset, row.length, entity_inferred_name[:2048], table.type + "_table", docid]
                    csv_rows.append(csv_row)

                cmd = "insert into entities (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s, %s, %s)"
                cur = conn.cursor()
                cur.executemany(cmd, csv_rows)
                conn.commit()
            except Exception as e:
                print len(clean_row_text)
                print csv_row
                logging.exception("SCREW UP")


def main():
    years = [ "111", "110","109", "108"] 

    reports_base=configuartion.get_path_to_reports()
    bills2008 = os.path.join(configuartion.get_path_to_bills(), "/110/bills/hr/hr2764/text-versions/")
    bills2009 = os.path.join(configuartion.get_path_to_bills(), "/111/bills/hr/hr1105/text-versions/")


    conn = psycopg2.connect(CONN_STRING)

    insert_all(bills2008, conn);
    insert_all(bills2009, conn);

    for year in years:
       insert_all(reports_base+year+"/", conn);
    conn.close()
    

if __name__=="__main__":

    main()
