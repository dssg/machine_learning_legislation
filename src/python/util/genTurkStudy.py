

import os, sys
import codecs
import psycopg2
import csv

from path_tools import BillPathUtils
from sunlight_id_to_path import sunlightid_to_path

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"
conn = psycopg2.connect(CONN_STRING)
cmd = "select distinct bill_id from  old_billentities where entity_type = 'Currency'"
cur = conn.cursor()
cur.execute(cmd)
ids = cur.fetchall()
split_ids = [ i[0].split("-") for i in ids]
bpu = BillPathUtils();
#paths = [bpu.get_bill_path( int(split_id[1]), split_id[0], split_id[2])+'document.txt' for split_id in split_ids]
paths = [sunlightid_to_path(i[0]) for i in ids]
print paths[0:3]
print "bills with Currency",  len(ids)


#get bill from file

# chema id entity_text, entity_type, entity_offset, entity_length, entity_name, bill_id
#schema  0        1            2            3              4              5          6
pre_window = 700
post_window = 300

fw = open ("temp.txt", 'w')
writer = csv.writer(fw, delimiter=',', quotechar='"')

header = ["ORG_id", "ALLOC_id", "text"]
writer.writerow(header)



for i in range(100):

	f = open(paths[i], 'r')
	
	doc = f.read()

	cmd = "select * from old_billentities where bill_id = " + "'"+ids[i][0]+"' and entity_type = 'Currency'"
	cur.execute(cmd)
	currency_entities = cur.fetchall()
	print "Number of Currency entities in Bill"+ids[i][0], len(currency_entities)
	for ce in currency_entities:
		offset = ce[3]
		upper = offset + post_window;
		lower = offset - pre_window;
		cmd = "select * from old_billentities where bill_id = " + "'"+ids[i][0]+"' and entity_type != 'Currency' and entity_offset>="+str(lower)+"and entity_offset<="+str(upper);
		cur.execute(cmd)
		org_entities = cur.fetchall()
		c_start = ce[3]
		c_end = ce[3] + ce[4]
		highlighted_c = "<SPAN style='BACKGROUND-COLOR: #ffff00'>" + doc[ce[3]:(ce[3]+ce[4])] + "</SPAN>"
		print "Number of Other entities near currency entity", len(org_entities)
		for oe in org_entities:
			o_start = oe[3]
			o_end = oe[3] + oe[4]
			highlighted_o = "<SPAN style='BACKGROUND-COLOR: #FFCCFF'>" + doc[oe[3]:(oe[3]+oe[4])] + "</SPAN>"

			aug_text = doc[lower:min(c_start, o_start)]
			if (c_end < o_end):
				aug_text = aug_text + highlighted_c + doc[c_end:o_start] + highlighted_o + doc[o_end:upper]
			else:
				aug_text = aug_text + highlighted_o + doc[o_end:c_start] + highlighted_c + doc[c_end:upper]


			print oe[3], oe[4], doc[oe[3]:(oe[3]+oe[4])]

			row = [oe[0], ce[0], aug_text]
			writer.writerow(row)



	

	# chunk into paragraphs


	# find entities per parargraph


	# output csv 


conn.close()
