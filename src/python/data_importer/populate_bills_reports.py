from path_tools import BillPathUtils, ReportPathUtils

ids_file = open("bills_reports_ids.csv", "w")

for line in open("reports_bills.csv").readlines()[1:]:
    report_path, bill_path = [part.strip() for part in line.split(",")]
    print report_path, bill_path
    if len(report_path) and len(bill_path):
        report_util = ReportPathUtils(path=report_path)
        bill_util = BillPathUtils(path=bill_path)
        #report_id = bill_id = None
        #try:
        report_id = report_util.get_db_document_id()
        bill_id = bill_util.get_db_document_id()
        #except:
        #    pass
        if report_id and bill_id:
            ids_file.write("%s,%s\n" %  (bill_id, report_id))
