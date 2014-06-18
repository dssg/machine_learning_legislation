import os, sys
import json

class BillPathUtils:
    
    def __init__(self, path="", rootDir="/mnt/data/sunlight/bills/"):
        self.path = path
        self.rootDir = rootDir
        if not self.rootDir.endswith('/'):
            self.rootDir += '/'
        
    def congress(self):
        return self.path[len(self.rootDir):len(self.rootDir)+3]
        
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
        
    def get_bill_path(self, congress, chamber, number, version):
        chars = "".join([ch for ch in number if ch.isalpha()])
        return "%s%d/bills/%s/%s/text-versions/%s/" %(self.rootDir, congress, chars,number,version )
        
class ReportPathUtils():
    
    def __init__(self, path="", rootDir="/mnt/data/sunlight/congress_reports/"):
        self.path = path
        self.rootDir = rootDir
        if not self.rootDir.endswith('/'):
            self.rootDir += '/'
        self.pathParts = self.path[len(self.rootDir):].split('/')
    
    def congress(self):
        return self.path[len(self.rootDir):len(self.rootDir)+3]
        
    def chamber(self):
        return pathParts[1]
        
    def report_number(self):
        return pathParts[2]
        
    def version_number(self):
        return pathParts[-1]
        
    def get_report_path(self, congress, chamber, number, version):
        return "%s%d/%s/%d/%s"%(self.rootDir, congress, chamber, number, version)
        
            
    
