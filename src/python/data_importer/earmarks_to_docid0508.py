# -*- coding: utf-8 -*-
import numpy as np, pandas as pd
import re, time, sys, csv
import path_to_docid
import toDatabase as td
import itertools 
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf-8')

def doc_normalizer08(doc_name):
    """
    Input: document name from 2008 OMB Earmarks
    Output: normalized path 
    """
    congress = 110
    bill = 'bill'
    report = 'report'
    house = 'house'
    senate = 'senate' 
    
    if 'Rept.'in doc_name:
        if 'H.' in doc_name: 
            number = re.findall('\d+',doc_name)[1]
            path = [congress, report, house, number]
        else: 
            number = re.findall('\d+',doc_name)[1]
            path = [congress, report, house, number]  
    elif 'P.L.' in doc_name: 
        if '116' in doc_name:
            # attach a report to this public law: house report 110-434 # 
            path = [congress, bill, house, 'hr3222']
        else:
            # add the two document ids for house reports 
            path = [congress, bill, house, ('hr2764',doc_name)]                 
    else: 
        path = [congress, bill, house, ('hr2764', doc_name)]
    
    return path 
            

def csv_extractor08(earmarks, year=2008):
    """
    Input: csv file for 2008 records
    Output: relevant database information 
    """
    csvFile = csv.reader(earmarks)
    document_columns = ['EARMARK_ID','CITATION_REFERENCE', 'CITATION_LOCATOR','CITATION_EXCERPT']
    columns = []
    earmarks_lis = []
    unis = []
    for rows in csvFile: 
        if not columns:
            columns = [rows.index(i) for i in document_columns]          
        else: 
            new_earmark = [rows[i] for i in columns] 
            earmark_id = new_earmark[0]
            doc_name = new_earmark[1]
            if doc_name and not (earmark_id,doc_name) in unis: 
                new_earmark[1] = doc_normalizer08(doc_name)
                unis.append((earmark_id,doc_name))
                earmarks_lis.append(new_earmark)
    return earmarks_lis

def doc_normalizer05(doc_name):
    """ 
    Input: document name from 2005 modified file" 
    Output: normalized name for the document 
    """
    bill = 'bill'
    report = 'report'
    house = 'house'
    senate = 'senate' 
    
    if 'P.L.' in doc_name: 
        digits = re.findall('\d+',doc_name)
        congress = int(digits[0])
        number = int(digits[1])
        if congress == 109:
            if number == 13:
                path0 = [congress, bill, house, 'hr1268']
                path1 = [congress, report, house, 16]
                path2 = [congress, report, house, 72]
                path3 = [congress, report, senate, 52]
                path = [path0, path1, path2, path3] 
            elif number == 97:
                path0 = [congress, bill, house, 'hr2744' ]
                path1 = [congress, report, house, 102]
                path2 = [congress, report, house, 255]
                path3 = [congress, report, senate, 92] 
                path = [path0, path1, path2, path3] 
            elif number == 115:
                path0 = [congress, bill, house, 'hr1760']
                path1 = [congress, report, house, 153]
                path2 = [congress, report, house, 307]
                path3 = [congress, report, senate, 106]
                path4 = [congress, report, senate, 109] 
                path = [path0, path1, path2, path3, path4] 

        elif congress == 108:
            if number == 447:
                path0 = [congress, bill, house, 'hr4818']
                path1 = [congress, report, house, 599]
                path2 = [congress, report, house, 792]
                path3 = [congress, report, senate, 346]
                path = [path0, path1, path2, path3] 
            elif number == 199:
                path0 = [congress, bill, house, 'hr2673']
                path1 = [congress, report, house, 193]
                path2 = [congress, report, house, 401]
                path3 = [congress, report, senate, 107]
                path = [path0, path1, path2, path3] 
            elif number == 287:
                path0 = [congress, bill, house, 'hr4613']
                path1 = [congress, report, house, 553]
                path2 = [congress, report, house, 622]
                path3 = [congress, report, senate, 284]
                path = [path0, path1, path2, path3] 
            elif number == 324:
                path0 = [congress, bill, house, 'hr4837']
                path1 = [congress, report, house, 607]
                path2 = [congress, report, house, 733]
                path3 = [congress, report, senate, 309]
                path = [path0, path1, path2, path3] 
            elif number == 334:
                path0 = [congress, bill, house, 'hr4567']
                path1 = [congress, report, house, 541]
                path2 = [congress, report, house, 774]
                path3 = [congress, report, senate, 280]
                path = [path0, path1, path2, path3] 
            elif number == 335:
                path0 = [congress, bill, house, 'hr4850']
                path1 = [congress, report, house, 610]
                path2 = [congress, report, house, 734]
                path3 = [congress, report, senate, 354]
                path = [path0, path1, path2, path3]
            elif number == 444:
                path = [congress, bill, senate, 's2965']
            elif number == 448:
                path = [congress, bill, senate, 's2618']
            elif number == 449:
                path0 = [congress, bill, house, 'hr2655']
                path1 = [congress, report, house, 260]
                path = [path0,path1]
            elif number == 477:
                path = [congress, bill, house, 'hr5370']
    elif ('Rept.' in doc_name or 'Report' in doc_name) and not 'Conference' in doc_name:
        digits = re.findall('\d+',doc_name)
        congress = int(digits[0])
        number = int(digits[1])
        if 'H' in doc_name or 'H.' in doc_name or 'House' in doc_name:
            path = [congress, report, house, number]
        else: 
            path = [congress, report, senate, number] 
    elif 'H.R.' in doc_name or 'Bill' in doc_name:
        congress = 108
        digits = re.findall('\d+', doc_name)
        if 'H.R' in doc_name: 
            if len(digits) < 2: 
                number = int(digits[0])
                if number == 4818:
                    path0 = [congress, bill, house, 'hr'+str(number)] 
                    path1 = [congress, report, house, 599]
                    path2 = [congress, report, house, 792]
                    path3 = [congress, report, senate, 346]
                    path = [path0,path1,path2,path3]
                else: 
                    path = [congress, bill, house, 'hr'+str(number)] 
            else: 
                congress= int(digits[0])
                number = int(digits[1])
                path = [congress, report, house, number] 
        elif 'Bill' in doc_name:
            number = digits[0]
            path = [congress, bill, senate, 's'+str(number)]
    else:
        path = ''
    return path 
            
            
            


def csv_extractor05(earmarks):
    """
    Input: csv file for 2005 records (altered using OpenRefine)
    Output: relevant database information
    """
    csvFile = csv.reader(earmarks)
    document_columns = ['earmark_id', 'Citation Reference', 'Citation Locator', 'Citation Excerpt']
    columns = []
    earmarks_lis = []
    for rows in csvFile: 
        if not columns:
            columns = [rows.index(i) for i in document_columns]   
        else: 
            earmark_id = rows[columns[0]]
            doc_name = rows[columns[1]]
            page = rows[columns[2]]
            excerpt = rows[columns[3]]
            if doc_name: 
                if not '&&' in doc_name: 
                    doc_normal = doc_normalizer05(doc_name)
                    if doc_normal:
                        if all([isinstance(elem, list) for elem in doc_normal]):
                            for dnormal in doc_normal:
                                doc_id = ed.path_to_docid(dnormal)
                                earmarks_lis.append([earmark_id, doc_id, page, excerpt])
                        else:
                            doc_id = ed.path_to_docid(doc_normal)
                            earmarks_lis.append([earmark_id, doc_id, page, excerpt])
                else:
                    doc_names = re.split('&&', doc_name)
                    for docs in doc_names: 
                        doc_normal = doc_normalizer05(docs)
                        if doc_normal:
                            if all([isinstance(elem, list) for elem in doc_normal]):
                                for dnormal in doc_normal:
                                    doc_id = ed.path_to_docid(dnormal)
                                    earmarks_lis.append([earmark_id, doc_id, page, excerpt])
                            else:
                                doc_id = ed.path_to_docid(doc_normal)
                                earmarks_lis.append([earmark_id, doc_id, page, excerpt])
    earmarks_lis.sort()
    earmarks_lis = list(elis for elis,_ in itertools.groupby(elis))
    return earmarks_lis
                    
# extracts the document id from the dattabase for 2005 and 2008 files
with open('/mnt/data/sunlight/OMB/2005_app1.csv','rU') as f_obj:
    earmarks_2005 = csv_extractor05(f_obj)
with open('/mnt/data/sunlight/OMB/2008_app.csv','rU') as f_obj:
    earmarks_2008 = csv_extractor(f_obj)

## sends extracted data to the earmarks_documents table in the database 
earmarks_2005 = pd.path_to_docid05(earmarks_2005)
earmarks_2008 = pd.path_to_docid08(earmarks_2008)
rows = earmarks_2005+earmarks_2008
td.toDatabase(rows)
