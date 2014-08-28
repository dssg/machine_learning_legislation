import os, path, sys
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from util import configuration
import psycopg2
import re
from bs4 import BeautifulSoup
from datetime import datetime
import json

CONN_STRING = configuration.get_connection_string()
root_dir = configuration.get_path_to_reports()
reports_bills_dict = {}
conn = psycopg2.connect(CONN_STRING)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# loop through each folder
def get_reports(path, congress):
    for report in os.listdir(path):
        if "mods.xml" not in os.listdir(os.path.join(path, report)):
            print "No metadata file found for directory %s" % os.path.join(path, report)
        else:
            xml_file = os.path.join(path, report, "mods.xml")
            associated_bill = get_associated_bill(xml_file)
            report_dir = os.listdir(os.path.join(path, report))
            if "mods.xml" in report_dir:
                report_dir.remove("mods.xml")
            write_bill_association(os.path.join(path, report, report_dir[0]), get_bill_directory(associated_bill, congress))

def get_associated_bill(xml_file):
    bill_name = ""
    soup = BeautifulSoup(open(xml_file))
    bill = soup.find("associatedbills")
    if not bill:
        print "No associated bill found for %s" % xml_file
    else:
        bill_name = bill.text
    return bill_name

def write_bill_association (report_dir, bill_dir):
    reports_bills_dict[bill_dir] = report_dir


def write_to_db():
    for bill_path, report_path in report_bills_dict.iteritems():
        if len(report_path) and len(bill_path):
            report_util = ReportPathUtils(path=report_path)
            bill_util = BillPathUtils(path=bill_path)
            report_id = report_util.get_db_document_id()
            bill_id = bill_util.get_db_document_id()
            if report_id and bill_id:
                cmd = "INSERT INTO bill_reports (bill_id, report_id) VALUES (%s, %s)"
                params = (bill_id, report_id)
                cur.execute(cmd, params)
                conn.commit()


def get_bill_directory(bill_name, congress_number):
    if not bill_name:
        return ""

    bill_dir = ""
    root_bill_dir = configuration.get_path_to_bills()
    bill_dir = os.path.join(root_bill_dir, congress_number)
    bill_dir = os.path.join(bill_dir, "bills")
    bill_dir = os.path.join(bill_dir, get_bill_type_dir(bill_name))
    bill_dir = os.path.join(bill_dir, get_full_bill_dir(bill_name))
    bill_dir = os.path.join(bill_dir, "text-versions")
    bill_dir = os.path.join(bill_dir, get_latest_version(bill_dir))

    return bill_dir

def get_latest_version(bill_path):
    versions = os.listdir(bill_path)
    latest_version = ""
    latest_version_date = datetime(1,1,1)
    for version in versions:
        metadata = json.load(open(os.path.join(bill_path, version, "data.json")))
        if datetime.strptime(metadata["issued_on"], "%Y-%m-%d") > latest_version_date:
            latest_version_date = datetime.strptime(metadata["issued_on"], "%Y-%m-%d")
            latest_version = version

    return latest_version

def get_bill_type_dir(bill_name):
    if "H. Con. Res." in bill_name:
        return "hconres"
    if "H.J. Res." in bill_name:
        return "hjres"
    if "H.R." in bill_name:
        return "hr"
    if "H. Res." in bill_name:
        return "hres"
    if "S. Con. Res." in bill_name:
        return "sconres"
    if "S.J. Res." in bill_name:
        return "sjres"
    if "S. Res." in bill_name:
        return "sres"

    return "s"

def get_full_bill_dir(bill_name):
    bill_type = get_bill_type_dir(bill_name)

    bill_num_regex = re.compile(r"\d+")
    number_match = bill_num_regex.search(bill_name)
    bill_number = number_match.group()

    return bill_type + bill_number

def main():
    # for each congress
    #congresses = ["108", "109", "110", "111"]
    congresses = ['111', ]
    for congress in congresses:
        path = os.path.join(root_dir, congress, "house")
        get_reports(path, congress)
        path = os.path.join(root_dir, congress, "senate")
        get_reports(path, congress)

if __name__ == "__main__":
    main()
