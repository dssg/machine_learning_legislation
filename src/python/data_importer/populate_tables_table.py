'''
script used to read through document table, find tables
in those documents, and populate the tables table
'''
import text_table_tools as ttt

def main():
    document_ids = get_document_ids()
    document_paths = get_document_paths_from_ids(document_ids)
    extract_tables(document_paths)

def get_document_ids():
    pass

def get_document_paths_from_ids(document_ids):
    pass

def extract_tables(document_paths):
    pass

if __name__ == "__main":
    main()
