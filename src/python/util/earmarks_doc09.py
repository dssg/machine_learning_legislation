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

## processing the omb file ## 
#original = pd.read_csv("2010_app.csv",low_memory=False)
def csvTopandas(earmarks):
    earmark_ids = earmarks['earmark_id'].tolist()
    com_names = ['hc_f_cttn_reference_name','hf_f_cttn_reference_name','sc_f_cttn_reference_name','sf_f_cttn_reference_name', 'c_f_cttn_reference_name']
    meta_data = {'hc_f_cttn_reference_name':['hc_f_cttn_location','hc_f_cttn_excerpt','hc_earmarks_total'],
             'hf_f_cttn_reference_name':['hf_f_cttn_location','hf_f_cttn_excerpt','hf_earmarks_total'],
             'sc_f_cttn_reference_name': ['sc_f_cttn_location','sc_f_cttn_excerpt','sc_earmarks_total'],
             'sf_f_cttn_reference_name': ['sf_f_cttn_location','sf_f_cttn_excerpt','sf_earmarks_total'],
             'c_f_cttn_reference_name' : ['c_f_cttn_location','c_f_cttn_excerpt','c_earmarks_total']
             }
    em_df = []
    rows = earmarks.shape[0]
    for i in range(rows): 
        for name in com_names:
            if not pd.isnull(earmarks.ix[i,name]):
                em_df.append([earmarks.ix[i,'earmark_id'],earmarks.ix[i,name],earmarks.ix[i,meta_data[name][0]],earmarks.ix[i,meta_data[name][1]],earmarks.ix[i,meta_data[name][2]]])
    
    em_dframe = pd.DataFrame(columns = ['earmark_id','doc_name','page_location','excerpt','earmarks_total'],index=np.arange(len(em_df)))
    
    for value in range(len(em_df)):
        em_dframe.ix[value] = em_df[value]
    
    grouped = em_dframe.groupby(['earmark_id','doc_name'])
    
    index = [group_values[0] for group_values in grouped.groups.values()]
    
    unique_grouped = em_dframe.reindex(index)
    
    return unique_grouped 

#earmarks_2009 = pd.read_csv("2009_app.csv",low_memory=False)
unique_grouped09 = csvTopandas(original)
unique_grouped09['path'] = ''
for i in unique_grouped09.iterrows():
    value = list(i[1])[1]
    if len(re.findall('\d+',value))>0:
        poc = value[0:value.index(re.findall('\d+',value)[0])]
        
        if 'Div. ' in poc:
            if 'Defense' in value or 'Homeland Security' in value or 'Military Construction' in value:
                unique_grouped09.ix[i[0],'path'] = [110,'bill','house','hr2638']
            else:
                unique_grouped09.ix[i[0],'path'] = [111,'bill','house', 'hr1105']
        
        elif 'Report' in poc: 
            rep = re.findall('\d+', value)[1]
            if 'H. Report' in poc: 
                path = [111,'report', 'house', rep]
            else: 
                path = [111,'report', 'senate', rep]
            
            unique_grouped09.ix[i[0],'path'] = path
        
        elif 'S. ' in poc and 'Report' not in poc: 
            bi = 's'+str(re.findall('\d+', value)[0])
            path = [111,'bill', 'senate', bi]
            unique_grouped09.ix[i[0],'path'] = path



unique_grouped09.to_csv("2009_pd.csv"

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
