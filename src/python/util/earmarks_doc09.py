import pandas as pd, numpy as np
import time, re, os, ast, sys
from datetime import datetime, date
import path_tools as pt
import pickle

USAGE = "python %s <input-omb-file> <output-csv-to-be-imported-to-db>" %(sys.argv[0])

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
    #em_dframe[['doc_name', 'page_location', 'excerpt']].astype(str)
    for value in range(len(em_df)):
        #print value, em_df[value]
        em_dframe.ix[value] = em_df[value]
    
    grouped = em_dframe.groupby(['earmark_id','doc_name'])
    
    index = [group_values[0] for group_values in grouped.groups.values()]
    
    unique_grouped = em_dframe.reindex(index)
    
    return unique_grouped 


def parse_reference_doc(unique_grouped09):
    """
    find the normalized bill/report name from the reference in OMB file as represented in the frame
    unique_grouped09: panda frame
    """
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


def map_to_doc_id(earmarks09):
    """
    finds the doc id associated with each row in the panda frame earmarks09
    """
    earmarks09['doc_id'] = ' '
    bill_path = pt.BillPathUtils()
    report_path = pt.ReportPathUtils()
    for row in earmarks09.iterrows():
        path = row[1]['path']
        if isinstance(path, basestring) and len(path) > 0:
             print path
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

                 all_versions = bill_path.get_all_versions(pth)

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


def main():
    original = pd.read_csv(sys.argv[1], encoding='latin1')
    unique_grouped09 = csvTopandas(original)
    #pickle.dump(unique_grouped09, open('frame_dump.bin','wb'))
    #unique_grouped09 = pickle.load(open('frame_dump.bin','rb'))
    #return
    parse_reference_doc(unique_grouped09)
    map_to_doc_id(unique_grouped09)
    unique_grouped09.to_csv(sys.argv[2],sep=',',encoding='utf8')
    
    
if __name__ == "__main__":
    #print pd.__version__
    if len(sys.argv) < 3:
        print USAGE
    else:
        main()
