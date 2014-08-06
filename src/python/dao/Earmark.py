"DAO for earmark in the earmarks table"
import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import psycopg2
import psycopg2.extras
import logging

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"

class Earmark:
    def __init__(self, earmark_id):
         self.cmd = """
         select earmark_id, coalesce(earmark_code,'') as earmark_code, 
         coalesce(agency,'') as agency, coalesce(bureau,'') as bureau, 
         coalesce(account,'') as account, coalesce(program,'') as program,
         enacted_year, coalesce(short_description,'') as short_description, 
         coalesce(full_description,'') as full_description, 
         coalesce(earmark_type,'') as earmark_type, coalesce(spendcom,'') as spendcom, 
         coalesce(recipient,'') as recepient, manual_earmark
         from earmarks where earmark_id = %s
         """
         conn = psycopg2.connect(CONN_STRING)
         try:
             cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
             cur.execute(self.cmd, (earmark_id,))
             result = cur.fetchone()
             if result and len(result) > 0:
                 self.earmark_id = result["earmark_id"]
                 self.earmark_code = result["earmark_code"]
                 self.agency = result["agency"]
                 self.bureau = result["bureau"]
                 self.account = result["account"]
                 self.program = result["program"]
                 self.enacted_year = result["enacted_year"]
                 self.short_description = result["short_description"]
                 self.full_description = result["full_description"]
                 self.earmark_type = result["earmark_type"]
                 self.spendcom = result["spendcom"]
                 self.recepient = result["recepient"]
                 self.manual_earmark = result["manual_earmark"]
             else:
                 raise("No Earmark was found with id %d" %(earmark_id))
         except Exception as exp:
             logging.exception("Error")
         finally:
             conn.close()

    def __str__(self):
        return "Earmark id:%d\nshort description:%s\nfull_description:%s\nrecepient:%s\n"%(self.earmark_id, self.short_description, self.full_description, self.recepient)
         