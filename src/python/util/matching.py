import os, sys
import codecs
import psycopg2
import psycopg2.extras
import csv
from pprint import pprint
import operator
import string

from nltk import metrics, stem, tokenize
 
stemmer = stem.PorterStemmer()
 
def normalize_stem(s):
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])
 
def fuzzy_match(s1, s2):
    return metrics.edit_distance(normalize_stem(s1), normalize_stem(s2)) 

def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, '')
 
    return s.lower().strip()



CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
conn = psycopg2.connect(CONN_STRING)
columns = ["earmark_documents.earmark_id", "document_id", "excerpt", "full_description", "short_description"]
cmd = "select "+", ".join(columns)+" from earmark_documents join earmarks on earmark_documents.earmark_id=earmarks.earmark_id"
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute(cmd)
earmarks = cur.fetchall()
print "number of earmarks", len(earmarks)


i=0
for earmark in earmarks:
	i=i+1	#get all named entities from the document
	columns = ["entity_text", "entity_type", "entity_offset", "entity_length", "entity_inferred_name"]
	cmd = "select "+", ".join(columns)+" from entities where document_id = "+str(earmark['document_id']) + " and entity_type in ('Organization', 'Facility', 'Company')"
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur.execute(cmd)
	entities = cur.fetchall()
	print "number of entities", len(entities)
	# find all entities that occur in excerpt, short description or full description or excerpt
	short_description =  earmark["short_description"]
	
	normalized_description = normalize(short_description)
	normalized_excerpt = normalize(earmark['excerpt'])
	print "short_description: \n", normalized_description
	print "excerpt:\n ", normalized_excerpt

	d_desc=set()
	d_exerpt=set()
	for entity in entities:
		normalized_entity = normalize(entity['entity_text'])
		normalized_inferred_name = normalize(entity['entity_inferred_name'])

		if normalized_entity in normalized_description:
			d_desc.add(normalized_entity)
		if  normalized_inferred_name in normalized_description:
			d_desc.add(normalized_inferred_name)

		if normalized_entity in normalized_excerpt:
			d_exerpt.add(normalized_entity)
		if normalized_inferred_name in normalized_excerpt:
			d_exerpt.add(normalized_inferred_name)

	print "entities in description: ",  d_desc
	print "\n"
	print "entities in excerpt:", d_exerpt
	print "\n\n"
	#print "all", set([entity['entity_inferred_name'] for entity in entities])


	print "\n"*4
	if i==100:
		break

