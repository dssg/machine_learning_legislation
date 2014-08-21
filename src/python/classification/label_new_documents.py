import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import argparse
import util.text_table_tools as text_table_tools
import psycopg2
import logging
from sklearn.externals import joblib
import cPickle as pickle
from instance import Instance
from pipe import Pipe
import pipe
from feature_generators import  entity_text_bag_feature_generator, simple_entity_text_feature_generator, gen_geo_features, sponsor_feature_generator
import prepare_earmark_data
import diagnostics
from sklearn import svm
from util import path_tools
from util.get_entities_from_tables import get_row_entity_text_and_entity_inferred_name
from matching import string_functions
import csv
import re
import util
import multiprocessing as mp
from pprint import pprint

CONN_STRING = util.configuartion.get_connection_string()



class EarmarkDetector:

    def __init__(self, geo_coder, sponsor_coder, conn, model, feature_space):
        self.geo_coder = geo_coder
        self.sponsor_coder = sponsor_coder
        self.conn = conn
        self.model = model
        self.feature_space = feature_space
        fgs = [
            entity_text_bag_feature_generator.unigram_feature_generator(force=True),
            simple_entity_text_feature_generator.simple_entity_text_feature_generator(force=True),
            gen_geo_features.geo_feature_generator(force = True),
            sponsor_feature_generator.SponsorFeatureGenerator(force = True),

        ]
        self.pipe = Pipe(fgs, num_processes=1)


    def get_instance_from_row(self, row, column_indices):
        instance = Instance()
        row_offset = row.offset
        (entity_text, entity_inferred_name) = get_row_entity_text_and_entity_inferred_name(row, column_indices)
        instance.attributes["entity_inferred_name"] = entity_inferred_name[:2048]
        instance.attributes['entity_text'] = entity_text[:2048]
        instance.attributes["id"] = 0
        return self.pipe.push_single(instance)


    def label_row(self, row, column_indices, table_offset, congress, chamber, document_type, number, sponsor_indices):

        instance = self.get_instance_from_row(row, column_indices)
        X, y, space = pipe.instances_to_matrix([instance,], feature_space = self.feature_space, dense = False)
        scores = self.model.decision_function(X)
        fields = ['congress', 'chamber','document_type','number', 'row', 'row_offset', 'row_length', 'score', 'state', 'sponsors']
        cmd = "insert into candidate_earmarks (" + ", ".join(fields) + ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id"
        attributes = instance.attributes
        state = self.geo_coder.get_state(attributes['entity_text'])
        cur = self.conn.cursor()
        if sponsor_indices:
            print sponsor_indices

        sponsors = []
        for index in sponsor_indices:
            try:
                sponsor_cell = attributes['entity_text'].split("|")[index]
                sponsors_in_cell = string_functions.tokenize(string_functions.normalize_no_lower(sponsor_cell))
                for sic in sponsors_in_cell:
                    if sic in self.sponsor_coder.sponsors[congress]:
                        sponsors.append(sic)

            except Exception as e:
                print "Index: %d" % index
                print len(attributes['entity_text'].split("|"))
                print attributes['entity_text']
                logging.exception("SCREW UP")

        sponsors_string = "|".join(sponsors)[:1024]

        cur.execute(cmd, (congress, chamber, document_type, number, attributes['entity_text'], row.offset+table_offset, row.length, scores[0], state, sponsors_string))
        curr_id = cur.fetchone()[0]

        for sponsor in sponsors:
            cur.execute('insert into sponsors (candidate_earmark_id, sponsor) values (%s, %s)', (curr_id,sponsor ))


        self.conn.commit()


    def label_doc(self, doc_path, congress, chamber, document_type, number):
        print doc_path
        paragraphs_list = text_table_tools.get_paragraphs(open(doc_path,'r'))
        tables = text_table_tools.identify_tables(paragraphs_list)
        for table in tables:
            table_offset = table.offset
            column_indices = sorted(text_table_tools.get_candidate_columns(table))
            sponsor_indices = self.sponsor_coder.find_sponsor_index(table, congress)
            for row in table.rows:
                self.label_row(row, column_indices, table_offset, congress, chamber, document_type, number, sponsor_indices)




class GeoCoder:
    def __init__(self):

        self.state_names_dict = {}
        self.capitalized_state_names_dict = {}

        for row in csv.reader(open("/mnt/data/sunlight/misc/states.csv")):
            self.state_names_dict[row[0]] = row[1]
            self.capitalized_state_names_dict[row[0].upper()] = row[1]

        self.state_names = set(self.state_names_dict.keys())
        self.capitalized_state_names = set(self.capitalized_state_names_dict.keys())
        self.state_abbreviations = set(self.state_names_dict.values())
        self.cities = set()
        self.cities_upper = set()

        for row in csv.reader(open("/home/ewulczyn/machine_learning_legislation/data/cities.csv")):
            self.cities_upper.add(row[1].upper())
            self.cities.add(row[1])


    def get_state(self, row):
        tokens = string_functions.tokenize(row)
        for t in tokens:
            if t in self.capitalized_state_names:
                return self.capitalized_state_names_dict[t]
            if t in self.state_names:
                return self.state_names_dict[t]
            if t in self.state_abbreviations:
                return t
        return None


    def get_city(self, row):
        for city in self.cities:
            if city in row:
                return city

        for city in self.cities_upper:
            if city in row:
                return city
        return None


class SponsorCoder:

    def __init__(self):
        self.sponsors = {i:set() for i in range(1, 114)}

        for row in csv.reader(open("/mnt/data/sunlight/misc/senators.csv", 'r')):
            congress = int(row[0])
            if congress == 20:
                print row
                print row[5]
                print row[6]
            sen = re.split('[:;, ]', row[6])[0].title()
            if sen.isalpha():
                self.sponsors[congress].add(sen)

        for row in csv.reader(open("/mnt/data/sunlight/misc/representatives.csv", 'r')):
            congress = int(row[0])
            if congress == 20:
                print row
                print row[5]
                print row[6]
            rep = re.split('[:;, ]', row[5])[0].title()
            if rep.isalpha():
                self.sponsors[congress].add(rep)

        #pprint(self.sponsors)



    def find_sponsor_index(self, table, congress):
        if len(table.rows) ==0 :
            return None
        m = len(table.rows)
        n = len(table.rows[0].cells)

        columns = [ [table.rows[i].cells[j].clean_text for i in range(m) ] for j in range(n) ]
        sponsor_densities = [(self.compute_sponsor_density(columns[j], congress), j ) for j in range(n)]
        sponsor_densities = sorted(sponsor_densities, reverse = True, key = lambda x : x[0])
        indices = [t[1] for t in sponsor_densities if t[0] > 0.1]

        return indices[:2]


    def compute_sponsor_density(self, column, congress):
        return sum([self.has_sponsor(cell, congress) for cell in column]) / float(len(column))



    def has_sponsor(self, cell, congress):
        tokens = re.split('[:;, ]', cell)
        n = len(tokens)
        num_sponsors = 0.0
        for token in tokens:
            token = token.strip()

            if token in self.sponsors[congress]:
                num_sponsors +=1
            elif token in set(['Rep', 'Rep.', 'Sen', 'Sen.']):
                print token
                num_sponsors +=1

        if num_sponsors/n > 0.7:
            return 1
        else:
            return 0





def label_all(t):
    directory = t[0]
    earmark_detector = t[1]
    earmark_detector.conn = psycopg2.connect(CONN_STRING)
    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename == "document.txt" or "." not in filename:
                doc_path = os.path.join(root, filename)
                if "congress" in doc_path:
                    path_util = path_tools.ReportPathUtils(path  = doc_path)
                    document_type = 'report'
                    number = path_util.report_number()
                else:
                    path_util = path_tools.BillPathUtils(path  = doc_path)
                    document_type = 'bill'
                    path_util.bill_number()
                    number = path_util.bill_number()

                earmark_detector.label_doc(doc_path, path_util.congress(), path_util.chamber(), document_type, number)
    earmark_detector.conn.close()



def main():

    parser = argparse.ArgumentParser(description='Match entities to OMB')
    parser.add_argument('--model', required = False, help='path to pickeld matching model')
    parser.add_argument('--data', required = False, help='path to pickeld instances')
    #parser.add_argument('--path', required = False)

    args = parser.parse_args()

    bills2008 = "/mnt/data/sunlight/bills/110/bills/hr/hr2764/text-versions/"
    bills2009 = "/mnt/data/sunlight/bills/111/bills/hr/hr1105/text-versions/"
    years = [ "111", "110","109", "108", "107", "106", "105", "104"]
    reports_base="/mnt/data/sunlight/congress_reports/"
    folders = [os.path.join(reports_base, year) for year in years] + [bills2008, bills2009]


    conn = psycopg2.connect(CONN_STRING)

    if args.model:
        feature_space = pickle.load(open(args.model+".feature_space", "rb"))
        model = joblib.load(args.model)
        logging.info("Loaded Model")

    elif args.data:
        keep_group = ['unigram_feature_generator', 'simple_entity_text_feature_generator', 'geo_feature_generator', 'sponsor_feature_generator']
        instances = prepare_earmark_data.load_instances(args.data)
        ignore_groups = [ fg for fg in instances[0].feature_groups.keys() if fg not in keep_group]
        X, y, feature_space = pipe.instances_to_matrix(instances, ignore_groups = ignore_groups,  dense = False)
        clf = svm.LinearSVC(C = 0.01)
        param_grid = {'C': [ 0.01, 0.1]}
        model = diagnostics.get_optimal_model (X, y, 5, clf, param_grid, 'roc_auc')
    else:
        exit()

    geo_coder = GeoCoder()
    sponsor_coder = SponsorCoder()


    earmark_detector = EarmarkDetector(geo_coder, sponsor_coder, conn, model, feature_space)


    p = mp.Pool(mp.cpu_count())
    p.map(label_all, [(folder, earmark_detector) for folder in folders])


    #for folder in folders:
    #   label_all((folder, earmark_detector));

    conn.close()




if __name__=="__main__":

    main()


