from path_tools import *
import argparse


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='identify tables and paragrapghs in bills')
    parser.add_argument('--id', required=True, type = int)
    args = parser.parse_args()
    doc_id = args.id

    try:
    	print BillPathUtils().get_path_from_doc_id(doc_id)
    except:
    	pass
    try:
    	print ReportPathUtils().get_path_from_doc_id(doc_id)
    except:
    	pass
