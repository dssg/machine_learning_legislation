from path_tools import *
import argparse


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='identify tables and paragrapghs in bills')
    parser.add_argument('--id', required=True, type = int)
    args = parser.parse_args()
    id = args.id


print BillPathUtils().get_path_from_doc_id(id)

print ReportPathUtils().get_path_from_doc_id(id)
