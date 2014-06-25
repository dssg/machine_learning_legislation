import pandas as pd, numpy as np
import time, re, os, ast, sys
from datetime import datetime
from datetime import date
import path_tools as pt

## importing the 2009 csv file ##
print sys.getdefaultencoding() 
reload(sys)
sys.setdefaultencoding("utf-8")
print sys.getdefaultencoding()

earmarks09  = pd.read_csv("2009_pd.csv")

earmarks09['doc_id'] = ' '
bill_path = pt.BillPathUtils()
report_path = pt.ReportPathUtils()

#c = 0
for row in earmarks09.iterrows():
    path = row[1]['path']
    if isinstance(path,basestring):
         path = ast.literal_eval(path)
         congress = int(path[0])
         bvr = path[1]
         chamber = path[2]
         number = path[3]
         if bvr == 'bill':
             if chamber == 'senate':
                 pth = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/s/'+str(number)
            
             else:
                 pth = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/hr/'+str(number)
                 
            # c = c+1
            # print pth,c    
             all_versions = bill_path.get_all_versions(pth)
             print all_versions
             
             best_date = date(1900,1,1)
             for version in all_versions:
                 npth = bill_path.get_bill_path(congress,number,version)
                 bill_date = pt.BillPathUtils(npth).bill_date()
                 bill_date = datetime.strptime(bill_date,"%Y-%m-%d").date()
                 if bill_date > best_date:
                     best_date = bill_date
                     best_version = version
             PATH_BILL = bill_path.get_bill_path(congress,number,best_version)
             DOC_ID = pt.BillPathUtils(PATH_BILL).get_db_document_id()
            #print DOC_ID,doc_name                                                   
             earmarks09.ix[row[0],'doc_id'] = DOC_ID
             
         elif bvr == "report":
             value = row[1]['doc_name']
             nums = re.findall('\d+',value)
             congress = int(nums[0])
             number = int(nums[1])
             if chamber == "senate":
                 pth = "/mnt/data/sunlight/congress_reports/" + str(congress) + "/senate/" + str(number)
             else: 
                  pth = "/mnt/data/sunlight/congress_reports/" + str(congress) + "/house/"+ str(number)
             
             all_versions = report_path.get_all_versions(pth)
             print all_versions, number,congress
             rep_path = report_path.get_report_path(congress,chamber,number,all_versions[0])
             DOC_ID = pt.ReportPathUtils(rep_path).get_db_document_id()
             earmarks09.ix[row[0],'doc_id'] = DOC_ID
             
         print DOC_ID
### exporting to the csv ## 
earmarks09.to_csv('2009_db.csv',sep=',',encoding='utf8')
