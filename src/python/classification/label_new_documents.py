import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
import util.text_table_tools as text_table_tools
import util.path_tools as path_tools
import psycopg2
import logging
from sklearn.externals import joblib
import cPickle as pickle
from instance import Instance
from pipe import Pipe
import pipe
from feature_generators import  entity_text_bag_feature_generator, simple_entity_text_feature_generator, gen_geo_features



def get_doc_id(path):
    if "congress" in path:
        path_util = path_tools.ReportPathUtils(path  = path)
    else:
        path_util = path_tools.BillPathUtils(path  = path)

    docid = path_util.get_db_document_id()
    return docid




def label_all(directory, conn, model, feature_space):
    
    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename == "document.txt" or "." not in filename:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                label_doc(filepath, conn, model, feature_space)



def get_instance_from_row(doc_id, table_offset, column_indices, row):
    instance = Instance()

    row_offset = row.offset
    entity_inferred_name = ''
    entity_text = ''

    for i in range(len(row.cells)):
        cell = row.cells[i]
        if len(cell.clean_text) == 0:
            continue
        entity_text += cell.clean_text + " | "
        if i in column_indices:
            entity_inferred_name += cell.clean_text + " | "

    instance.attributes["entity_offset"] = table_offset+row.offset
    instance.attributes["entity_length"] = row.length
    instance.attributes["entity_inferred_name"] = entity_inferred_name[:2048]
    instance.attributes['entity_text'] = entity_text[:2048]
    instance.attributes["document_id"] = doc_id
    instance.attributes["id"] = 0

    return instance



def get_features(instances, num_processes):
    logging.info("Creating pipe")

    fgs = [
        entity_text_bag_feature_generator.unigram_feature_generator(force=True),
        simple_entity_text_feature_generator.simple_entity_text_feature_generator(force=True),
        gen_geo_features.geo_feature_generator(force = True),
    ]
    pipe = Pipe(fgs, instances, num_processes=num_processes)
    pipe.push_all_parallel()
    return pipe.instances



def label_doc(path, conn, model, feature_space):
    doc_id = get_doc_id(path)
    instances = []
    paragraphs_list = text_table_tools.get_paragraphs(open(path,'r'))
    f_str = open(path,'r').read()
    tables = text_table_tools.identify_tables(paragraphs_list)

    for table in tables:
        table_offset = table.offset
        column_indices = sorted(text_table_tools.get_candidate_columns(table))
        for row in table.rows:
            instances.append(get_instance_from_row(doc_id, table_offset, column_indices, row))

    instances = get_features(instances, 1)
    X, y, space = pipe.instances_to_matrix(instances, feature_space = feature_space, dense = False)
    scores = model.decision_function(X)
    fields = ['row', 'row_offset', 'row_length', 'document_id', 'score'] 
    cmd = "insert into candidate_earmarks (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s)"
    for i in range(len(instances)):
        attributes = instances[i].attributes
        cur = conn.cursor()
        cur.execute(cmd, (attributes['entity_text'],attributes['entity_offset'], attributes['entity_length'], doc_id, scores[i]))
        conn.commit()




def main():

    parser = argparse.ArgumentParser(description='Match entities to OMB')
    parser.add_argument('--model', required = True, help='path to pickeld matching model')
    args = parser.parse_args()

    bills2008 = "/mnt/data/sunlight/bills/110/bills/hr/hr2764/text-versions/"
    bills2009 = "/mnt/data/sunlight/bills/111/bills/hr/hr1105/text-versions/"

    years = [ "111", "110","109", "108"] 
    reports_base="/mnt/data/sunlight/congress_reports/"

    folders = [os.path.join(reports_base, year) for year in years] + [bills2008, bills2009]



    CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
    conn = psycopg2.connect(CONN_STRING)

    feature_space = pickle.load(open(args.model+".feature_space", "rb"))
    model = joblib.load(args.model)
    logging.info("Loaded Model")


    for folder in folders:
       label_all(folder, conn, model, feature_space);
    conn.close()




if __name__=="__main__":

    main()


