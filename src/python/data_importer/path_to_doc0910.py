import csv,time, re, os, ast, sys, inspect

sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe() ))[0],".."))))
import util.path_tools as pt

from datetime import datetime, date

reload(sys)
sys.setdefaultencoding('utf-8')

def path_to_docid0910(earmark_path):
    """
    Input: normalized path
    Output: document id 
    """
    bill_path = pt.BillPathUtils()
    report_path = pt.ReportPathUtils()
    
    congress = earmark_path[0]
    doc_type = earmark_path[1]
    chamber = earmark_path[2]
    doc_name = earmark_path[3]
    
    if doc_type == 'bill':
        if isinstance(doc_name, tuple):
            doc_ref = doc_name[0]
            div_type = doc_name[1]
            PATH = '/mnt/data/sunlight/bills/110/bills/hr/'+str(doc_ref)+'/'
            all_versions = bill_path.get_all_versions(PATH)
            if 'Div.' in div_type:
                pth_versions = bill_path.get_all_versions('/mnt/data/sunlight/bills/111/bills/hr/hr1105/')
                if 'Agriculture' in div_type:
                    version = 'CPRT-111JPRT47494-DivisionA'
                elif 'Commerce' in div_type:
                    version = 'CPRT-111JPRT47494-DivisionB'
                elif 'Energy' in div_type:
                    version = 'CPRT-111JPRT47494-DivisionC'
                elif 'Financial' in div_type:
                    version = 'CPRT-111JPRT47494-DivisionD'
                elif 'Interior' in div_type: 
                    version = 'CPRT-111JPRT47494-DivisionE'
                elif 'Labor' in div_type:
                    version = 'CPRT-111JPRT47494-DivisionF'
                elif 'Transportation' in div_type:
                    version = 'CPRT-111JPRT47494-DivisionI' 
                pth = bill_path.get_bill_path(congress,doc_ref,version)
                doc_id = pt.BillPathUtils(pth).get_db_document_id()
            else:
                version = 'eh'
                pth = bill_path.get_bill_path(congress,doc_ref,version)
                doc_id  = pt.BillPathUtils(pth).get_db_document_id()
                
        else:
            if chamber == 'senate':
                pth = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/s/'+str(doc_name)
            else:
                pth = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/hr/'+str(doc_name)
                
            all_versions = bill_path.get_all_versions(pth)
            best_version = all_versions[0]
            best_date = date(1900,1,1)
            for version in all_versions:
                npth = pth + '/text-versions/' + version 
                bill_date = pt.BillPathUtils(npth).bill_date()
                bill_date = datetime.strptime(bill_date,"%Y-%m-%d").date()
                if bill_date > best_date:
                    best_date = bill_date
                    best_version = version
            PATH_BILL = bill_path.get_bill_path(congress,doc_name,best_version)
            doc_id  = pt.BillPathUtils(PATH_BILL).get_db_document_id()
    else:
        if chamber == 'senate':
            pth = "/mnt/data/sunlight/congress_reports/" + str(congress) +"/senate/" + str(doc_name)
        else:
            pth= "/mnt/data/sunlight/congress_reports/"+str(congress)+"/house/"+str(doc_name)
        all_versions = report_path.get_all_versions(pth)
        rep_path = report_path.get_report_path(int(congress),chamber,int(doc_name),all_versions[0])
        doc_id = pt.ReportPathUtils(rep_path).get_db_document_id()

    return doc_id
