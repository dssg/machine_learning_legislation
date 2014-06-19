import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from util import path_tools
import psycopg2
import datetime
import argparse

CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"



def import_bill(path):
    """
    import a certain bill.
    path: absolute path to the bill directory
    example: /mnt/data/sunlight/bills/111/bills/s/s100/
    """
    bill_path_obj = path_tools.BillPathUtils(path)
    db_bill_id = import_bill_info(True, 
    "%s-%d" %(bill_path_obj.bill_number(), bill_path_obj.congress()) , bill_path_obj.congress(), 
    bill_path_obj.bill_number(), bill_path_obj.chamber() =='senate' )
    #print db_bill_id
    versions = bill_path_obj.get_all_versions(path)
    for version_name in versions:
        v = path_tools.BillPathUtils( os.path.join(os.path.join(path,'text-versions'), version_name))
        parts = [int(p) for p in v.bill_date().split('-')]
        import_version(v.version(), db_bill_id, datetime.date(parts[0],parts[1],parts[2]) )
        
def import_bill_info(bill, sunlight_id, congress, number, senate):
    """
    import a bill to database
    bill: bollean, True refers to bill, False to report
    sunlight_id: legacy string id
    congress: congress number, should be an integer. example, 111
    number: bill number or report number. example s133, hr4522, 
    senate: boolean that is True when it's a senate bill or report, False for house
    """
    conn = psycopg2.connect(CONN_STRING)
    try:
        cmd = "insert into congress_meta_document (bill, sunlight_id, congress, number, senate) \
        values (%s, %s, %s, %s, %s) returning id"
        cur = conn.cursor()
        cur.execute(cmd, (bill, sunlight_id, congress, number, senate))
        conn.commit()
        return cur.fetchone()[0]
        
    except Exception as exp:
        conn.rollback()
        print exp
        raise exp
    finally:
        conn.close()
    
def import_version(version_name, congress_meta_doc_id, version_date=None):
    conn = psycopg2.connect(CONN_STRING)
    try:
        cur = conn.cursor()
        cmd = 'insert into documents (date, version, congress_meta_document) values(%s,%s,%s)'
        cur.execute(cmd, (version_date, version_name, congress_meta_doc_id))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        print ex
        raise ex
    finally:
        conn.close()
        

def import_bills_folder(path):
    for dir in os.listdir(path):
        import_bill(os.path.join(path, dir))    

def import_congress_bills(path):
    """
    path: path to congress bills
    example: /mnt/data/sunlight/bills/110/bills/
    """
    for dir in os.listdir(path):
        import_bills_folder(os.path.join(path,dir))
    
def main():
    parser = argparse.ArgumentParser(description='Import bills and reports to the database')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--bills', action='store_true' , help ="import bills")
    group.add_argument('--reports', action='store_true', help="import reports")
    parser.add_argument('--path', required=True, help='path to congress directory containing bills or reports')
    args = parser.parse_args()
    path = args.path
    if args.bills:
        import_congress_bills(path)
    else:
        pass
if __name__=="__main__":
    main()
    
