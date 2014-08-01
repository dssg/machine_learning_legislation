import path_tools as pt
import psycopg2
import csv,time, re, os, ast, sys
from datetime import datetime, date
reload(sys)
sys.setdefaultencoding('utf-8')

def path_to_docid05(earmark_path):
    """                                                                                                    
    Input: list of lists of extracted earmark info                                                        \
    Ouput: list of lists containing relevant document id                                                  \
                                                                                                           
    """
    bill_path = pt.BillPathUtils()
    report_path = pt.ReportPathUtils()

    congress = earmark_path[0]
    bill_report = earmark_path[1]
    chamber = earmark_path[2]
    number = earmark_path[3]

    if bill_report == 'bill':

        if chamber == 'senate':
            path =  '/mnt/data/sunlight/bills/'+str(congress)+'/bills/s/'+str(number)
        else:
            path = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/hr/'+str(number)

        all_versions = bill_path.get_all_versions(path)
        best_date = date(1900,1,1)
        for version in all_versions:
            npth =  path + '/text-versions/' + version 
            bill_date = pt.BillPathUtils(npth).bill_date()
            bill_date = datetime.strptime(bill_date,"%Y-%m-%d").date()
            if bill_date > best_date:
                best_date = bill_date
                best_version = version
        PATH_BILL = bill_path.get_bill_path(congress,number,best_version)
        doc_id = pt.ReportPathUtils(PATH_BILL).get_db_document_id()
    else:
        if chamber == "senate":
            path = "/mnt/data/sunlight/congress_reports/" + str(congress) +"/senate/" + str(number)
        else:
            path = "/mnt/data/sunlight/congress_reports/" + str(congress)+"/house/"+ str(number)

        all_versions = report_path.get_all_versions(path)
        rep_path = report_path.get_report_path(int(congress),chamber,int(number),all_versions[0])
        doc_id = pt.ReportPathUtils(rep_path).get_db_document_id()
    return doc_id


def path_to_docid08(earmarks):
    """                                                                                                    
    Input: list of lists of extracted earmark info                                                         
    Ouput: list of lists containing relevant document id                                                   
    """
    bill_path = pt.BillPathUtils()
    report_path = pt.ReportPathUtils()
    database = []
    for earmark in earmarks:
        earmark_id  = earmark[0]
        page = earmark[2]
        excerpt = earmark[3]
        earmark_info = earmark[1]

        congress = int(earmark_info[0])
        bill = earmark_info[1]
        chamber = earmark_info[2]
        number = earmark_info[3]

        if bill == 'bill':
            if isinstance(number,tuple):
                doc_ref  = number[0]
                document_name = number[1]
                all_versions = bill_path.get_all_versions('/mnt/data/sunlight/bills/110/bills/hr/hr2764/')
                if re.search('\Division\s\w',document_name):
                    doc_string = re.findall('\Division\s\w',document_name)[0].replace(" ","")
                    version_index = [div_type for div_type in all_versions if doc_string in i]
                    version = version_index[0]
                    pth = bill_path.get_bill_path(congress,doc_ref,version)
                    doc_id = pt.BillPathUtils(pth).get_db_document_id()
                database.append([earmark_id,22552,page,excerpt])
                database.append([earmark_id,22553,page,excerpt])
                database.append([earmark_id,74460,page,excerpt])
                database.append([earmark_id,74678,page,excerpt])

            else:
                if chamber == 'senate':
                    pth = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/s/'+str(number)
                else:
                    pth = '/mnt/data/sunlight/bills/'+str(congress)+'/bills/hr/'+str(number)
                all_versions = bill_path.get_all_versions(pth)
                best_date = date(1900,1,1)
                for version in all_versions:
                    npth = pth + '/text-versions/' + version 
                    bill_date = pt.BillPathUtils(npth).bill_date()
                    bill_date = datetime.strptime(bill_date,"%Y-%m-%d").date()
                    if bill_date > best_date:
                        best_date = bill_date
                        best_version = version
                PATH_BILL = bill_path.get_bill_path(congress,number,best_version)
                doc_id  = pt.BillPathUtils(PATH_BILL).get_db_document_id()
                if number == 'hr3222':
                    database.append([earmark_id,74360,page,excerpt])
        elif bill=='report':
            if chamber == "senate":
                pth = "/mnt/data/sunlight/congress_reports/" + str(congress) +"/senate/" + str(number)
            else:
                pth = "/mnt/data/sunlight/congress_reports/" + str(congress)+"/house/"+ str(number)

            all_versions = report_path.get_all_versions(pth)
            rep_path = report_path.get_report_path(int(congress),chamber,int(number),all_versions[0])
            doc_id = pt.ReportPathUtils(rep_path).get_db_document_id()

        database.append([earmark_id,doc_id,page,excerpt])
    database_dict = {}
    for ids in database:
        key = (ids[0],ids[1])
        value = [ids[2],ids[3]]
        if not key in database_dict.keys():
            database_dict[key] = [value]
        else:
            database_dict[key].append(value)
    new_database = []
    for key in database_dict.keys():
        item = list(key) + database_dict[key][0]
        new_database.append(item)
    return new_database

