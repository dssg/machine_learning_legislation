import os
import psycopg2
import re
from bs4 import BeautifulSoup

root_dir = "/mnt/data/sunlight/congress_reports/"

# loop through each folder
def get_reports(path, congress):
    for report in os.listdir(path):
        if "mods.xml" not in os.listdir(os.path.join(path, report)):
            print "No metadata file found for directory %s" % os.path.join(path, report)
        else:
            xml_file = os.path.join(path, report, "mods.xml")
            associated_bill = get_associated_bill(xml_file)
            report_dir = os.listdir(os.path.join(path, report))
            if "mods.xml" in bill_dir:
                report_dir.remove("mods.xml")
            write_bill_association(os.path.join(path, report, report_dir), get_bill_directory(associated_bill, congress))

def get_associated_bill(xml_file):
    bill_name = ""
    soup = BeautifulSoup(open(xml_file))
    bill = soup.find("associatedbills")
    if not bill:
        print "No associated bill found for %s" % xml_file
    else:
        bill_name = bill.text
    return bill_name

def write_bill_association (report_id, bill_id):
    print "%s,%s" % (report_id, bill_id)

def get_bill_directory(bill_name, congress_number):
    if not bill_name:
        return ""

    bill_dir = ""
    root_bill_dir = "/mnt/data/sunlight/bills/"
    bill_dir = os.path.join(root_bill_dir, congress_number)
    bill_dir = os.path.join(bill_dir, "bills")
    bill_dir = os.path.join(bill_dir, get_bill_type_dir(bill_name))
    bill_dir = os.path.join(bill_dir, get_full_bill_dir(bill_name))

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
    bill_type = get_bill_type(bill_name)

    bill_num_regex = re.compile(r"\d+")
    number_match = bill_num_regex.search(bill_name)
    bill_number = number.match.group()

    return bill_type + bill_number

def main():
    # for each congress
    for congress in os.listdir(root_dir):
        path = os.path.join(root_dir, congress, "house")
        get_reports(path, congress)
        path = os.path.join(root_dir, congress, "senate")
        get_reports(path, congress)

if __name__ == "__main__":
    main()
