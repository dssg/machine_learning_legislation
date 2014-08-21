import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from util import configuration
import re,sys,csv,codecs
import math
import solr,psycopg2

def idf(entity_count):
    log_input = float(document_count)/(1+entity_count)
    return math.log10(log_input)


solr_connection = solr.SolrConnection('http://54.184.78.244:8983/solr/solr')
CONN_STRING = configuration.get_connection_string()
conn = psycopg2.connect(CONN_STRING)
cur = conn.cursor()
cur.execute("select  count(distinct id) from documents")
document_count = int(cur.fetchall()[0][0])
cur.execute("select e.entity_inferred_name,log(75905/(count(e.document_id)+1)+1) as idf from entities as e join documents on e.document_id = documents.id join congress_meta_document as cmd on documents.congress_meta_document = cmd.id left join earmark_documents as ed on ed.matched_entity_id = e.id where e.entity_type <> 'Currency' and cmd.congress = 111 and ed.matched_entity_id is null group by e.entity_inferred_name order by idf desc")
entities = cur.fetchall()

with open('entity_idf.csv', mode= 'w') as f_obj:
    entity_idf_csv = csv.writer(f_obj, delimiter='\t',lineterminator='\n')
    for ent in entities:
        name = ent[0]
        idf = float(ent[1])
        row = [name, idf]
        entity_idf_csv.writerow(row)

