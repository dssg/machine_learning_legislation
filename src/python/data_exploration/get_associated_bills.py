# get all associated bills from congressional reports for analysis

import os
import re
from bs4 import BeautifulSoup

root_dir = "/mnt/data/sunlight/congress_reports/"

# loop through each folder
def get_reports(path, congress):
    bills_file = open("bills.txt", "a+")
    for report in os.listdir(path):
        if "mods.xml" not in os.listdir(os.path.join(path, report)):
            print "No metadata file found for directory %s" % os.path.join(path, report)
        else:
            xml_file = os.path.join(path, report, "mods.xml")
            associated_bill = get_associated_bill(xml_file)
            bills_file.write("%s\n" % associated_bill)

def get_associated_bill(xml_file):
    bill_name = ""
    soup = BeautifulSoup(open(xml_file))
    bill = soup.find("associatedbills")
    if not bill:
        print "No associated bill found for %s" % xml_file
    else:
        bill_name = bill.text
    return bill_name

def main():
    # for each congress
    for congress in os.listdir(root_dir):
        path = os.path.join(root_dir, congress, "house")
        get_reports(path, congress)
        path = os.path.join(root_dir, congress, "senate")
        get_reports(path, congress)

if __name__ == "__main__":
    main()
