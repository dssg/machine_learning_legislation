'''
script used to read through document table, find tables
in those documents, and populate the tables table
'''
import sys, os, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import util.text_table_tools as ttt
from util import configuration
import psycopg2
from util.path_tools import BillPathUtils, ReportPathUtils
import codecs
import argparse

CONN_STRING = configuration.get_connection_string()
conn = psycopg2.connect(CONN_STRING)

def main():
    #TODO: cleanup this API
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--map', action="store_true", required=False)
    parser.add_argument('--insert', action="store_true", required=False)
    parser.add_argument('--file', required=False)
    args = parser.parse_args()

    if args.map:
        document_ids = get_document_ids()
        document_paths = get_document_paths_from_ids(document_ids)
        out_file = open(args.file, "w")
        for path in document_paths:
            out_file.write("%s,%s\n" % path)

    if args.insert:
        in_file = open(args.file)
        document_paths = []
        for line in in_file:
            line = line.replace("(", "").replace(")", "")
            path, doc_id, is_bill = line.split(",")
            document_paths.append((path, doc_id, is_bill))
        extract_tables(document_paths)

def get_document_ids():
    cmd = """SELECT d.id, cmd.bill
    FROM documents d
    JOIN congress_meta_document cmd
    ON d.congress_meta_document = cmd.id"""
    cur = conn.cursor()
    cur.execute(cmd)
    ids = cur.fetchall()
    print "got doc ids"
    return ids

def get_document_paths_from_ids(document_ids):
    paths = []
    for doc_id in document_ids:
        id = doc_id[0]
        is_bill = doc_id[1]
        if is_bill:
            path_util = BillPathUtils()
        else:
            path_util = ReportPathUtils()
        path = path_util.get_path_from_doc_id(id)
        paths.append((path, doc_id))
    print "got paths"
    return paths

def extract_tables(document_paths):
    print "begin table extraction"
    for path in document_paths:
        paragraphs_list = ttt.get_paragraphs(codecs.open(path[0], 'r', 'utf8'))
        tables = ttt.identify_tables(paragraphs_list)
        try:
            params = [(t.offset, t.length, ','.join(t.header), ' '.join(t.title), ' '.join(t.body), ' '.join(t.content), path[1]) for t in tables]
            cmd = 'INSERT INTO tables ("offset", "length", headers, title, body, content, document_id) VALUES (%s,%s,%s,%s,%s,%s,%s)'
            cur = conn.cursor()
            cur.executemany(cmd, params)
            conn.commit()
        except Exception as ex:
            print "Failed to import doc %s: %s" % (path[0], ex)


if __name__ == "__main__":
    main()
