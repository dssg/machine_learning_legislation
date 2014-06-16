import os
import psycopg2
import re
from bs4 import BeautifulSoup

root_dir = "/mnt/data/sunlight/congress_reports/"
conn = psycopg2.connect("dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com")

# loop through each folder
def get_reports(path, congress):
    for report in os.listdir(path):
        if "mods.xml" not in os.listdir(os.path.join(path, report)):
            print "No metadata file found for directory %s" % os.path.join(path, report)
        else:
            xml_file = os.path.join(path, report, "mods.xml")
            associated_bill = get_associated_bill(xml_file)
            bill_dir = os.listdir(os.path.join(path, report))
            if "mods.xml" in bill_dir:
                bill_dir.remove("mods.xml")
            write_bill_association(conn, bill_dir[0], clean_up_bill_name(associated_bill, congress))

def get_associated_bill(xml_file):
    bill_name = ""
    soup = BeautifulSoup(open(xml_file))
    bill = soup.find("associatedbills")
    if not bill:
        print "No associated bill found for %s" % xml_file
    else:
        bill_name = bill.text
    return bill_name

def write_bill_association(conn, report_id, bill_id):
    cmd = "INSERT INTO reports_bills (report_id, bill_id) values (%s, %s)"
    params = (report_id, bill_id)
    cur = conn.cursor()
    cur.execute(cmd, params)
    conn.commit()

def clean_up_bill_name(bill_name, congress_number):
    if not bill_name:
        return ""
    clean_name = ""
    # house or senate identifier
    if bill_name[0].lower() == 's':
        clean_name = clean_name + "s"
    if bill_name[0].lower() == 'h':
        clean_name = clean_name + "hr"
    # bill number
    bill_number= re.compile("\d+")
    clean_name = clean_name + bill_number.search(bill_name).group()

    clean_name = clean_name + "-%s" % congress_number
    return clean_name

def main():
    # for each congress
    for congress in os.listdir(root_dir):
        path = os.path.join(root_dir, congress, "house")
        get_reports(path, congress)
        path = os.path.join(root_dir, congress, "senate")
        get_reports(path, congress)

if __name__ == "__main__":
    main()
