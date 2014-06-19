import os, sys
import json

class BillPathUtils:
    
    def __init__(self, path="", rootDir="/mnt/data/sunlight/bills/"):
        self.path = path
        self.rootDir = rootDir
        if not self.rootDir.endswith('/'):
            self.rootDir += '/'
            
        
    def congress(self):
        return int(self.path[len(self.rootDir):len(self.rootDir)+3])
        
    def chamber(self):
        subpath = self.path[len(self.rootDir):]
        if subpath[10] =="s":
            return "senate"
        else:
            return "house"
        
    def bill_number(self):
        subpath = self.path[len(self.rootDir):]
        parts= subpath.split('/')
        return parts[3]
        
    def version(self):
         subpath = self.path[len(self.rootDir):]
         parts= subpath.split('/')
         return parts[5]
         
    def bill_date(self):
        date = json.load(open(os.path.join(self.path, 'data.json')))
        return date['issued_on']
        
    def get_bill_path(self, congress, number, version):
        """
        returns the path to a bill using the information provided
        congress: integer for congress number, example: 111
        number: bill number, example hr2244 or s154. Note it's a string
        version: string version, example ih, rs
        """
        chars = "".join([ch for ch in number if ch.isalpha()])
        return "%s%d/bills/%s/%s/text-versions/%s/" %(self.rootDir, congress, chars,number,version )
        
    def get_all_versions(self, path_to_bill):
        """
        returns the name of the available versions for a current bill
        path_to_bill: absolute path to a bill. Assumes no versions in the path
        example: /mnt/data/sunlight/bills/111/bills/s/s100/
        """
        return os.listdir(os.path.join(path_to_bill, 'text-versions') )
        
class ReportPathUtils():
    
    def __init__(self, path="", rootDir="/mnt/data/sunlight/congress_reports/"):
        self.path = path
        self.rootDir = rootDir
        if not self.rootDir.endswith('/'):
            self.rootDir += '/'
        self.pathParts = self.path[len(self.rootDir):].split('/')
    
    def congress(self):
        return int(self.path[len(self.rootDir):len(self.rootDir)+3])
        
    def chamber(self):
        return pathParts[1]
        
    def report_number(self):
        return pathParts[2]
        
    def version_number(self):
        return pathParts[-1]
        
    def get_report_path(self, congress, chamber, number, version):
        return "%s%d/%s/%d/%s"%(self.rootDir, congress, chamber, number, version)
        
    def get_all_versions(self, path_to_report):
        """
        get all the versions of the report
        note that report has only one version, however some reports are split into 
        parts and we modle a part as a version
        path_to_report: absolute path to the report directory
        """
        return [ fname for fnmae in os.listdir(path_to_report) if fname != 'mods.xml']
            
    
