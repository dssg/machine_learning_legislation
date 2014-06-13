import os, sys, io
import httplib
import argparse
import urllib2
import codecs
import zipfile
import shutil
import tempfile

def get_max_congress_report_number(congress, chamber="hrpt"):
    """
    given a congress id, and chamber, which can be senate or house, finds
    out the largest congressional report id for that congress
    congress: a congress number, ex: 113
    chamber: [hrpt | srpt] , s for senate, and h for house
    """
    path_format = "/fdsys/pkg/CRPT-%s%s%d/mods.xml"
    max_id = 2000
    min_id = 1
    while get_request_status(path_format%(congress, chamber, max_id)) == 200:
        min_id=max_id
        max_id = max_id * 2
    while max_id - min_id > 1:
        middle = (max_id + min_id) / 2
        result = get_request_status(path_format%(congress, chamber, middle))
        if result == 200:
            min_id = middle
        else:
            max_id = middle
    return min_id
    
    
def get_request_status(path, host="www.gpo.gov"):
    """
    sends header request to given path on a host and return a response
    """    
    try:
        #print "checking ", path
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD",path)
        res = conn.getresponse()
        conn.close()
        return res.status
    except Exception as ex:
        print ex
                
    
def setup_directories(root_dir, congresses):
    """
    creates the needed directories under the home path
    such that each congress has it's own sub folder
    """
    for congress in congresses:
        path = os.path.join(root_dir,str(congress))
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(os.path.join(path,"senate")):
            os.mkdir(os.path.join(path,"senate"))
        if not os.path.exists(os.path.join(path,"house")):
            os.mkdir(os.path.join(path,"house"))
        
    
def download_report(report_id):
    """
    downloads a congresisonal report identified by a report_id
    report_id:  example : 104hrpt883, first three numbers congress #, then hrpt|srpt, then report number
    """
    url = "http://www.gpo.gov/fdsys/pkg/CRPT-%s/html/CRPT-%s.htm"%(report_id, report_id)
    return download(url).decode('utf8')
    
def download_metadata(report_id):
    """
    downlaods metadata for report
    """
    url = "http://www.gpo.gov/fdsys/pkg/CRPT-%s/mods.xml"%(report_id)
    return download(url).decode('utf8')

def download_zipfile(report_id):
    url = "http://www.gpo.gov/fdsys/pkg/CRPT-%s.zip"%(report_id)
    return download(url) 
    
def download(url, retry_attempts=5):
    """
    downloads a given url and return the contet
    """
    for i in range(retry_attempts):
        try:
            return urllib2.urlopen(url).read()
        except Exception as exp:
            print "failed to fetch url %s, attempt %d" %(url,i), exp
    raise Exception("Failed to retrieve url %s"%(url) )

def construct_write_folder(base_dir, report_id):
    """
    returns the directory path into which the report given by report_id should be written to
    """
    congress = report_id[:3]
    if report_id.find("srpt") > 0:
        chamber = "senate"
    else:
        chamber = "house"
    report_number = report_id[7:]
    path = os.path.join(base_dir, congress)
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, chamber)
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, report_number)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def generate_reports_for_congress(congress, chamber="hrpt"):
    """
    congress: congress number, like 113
    chamber: hrpt | srpt, hrpt for house, srpt for senate
    """
    report_format = "%s%s%d"
    max_id = get_max_congress_report_number(congress, chamber)
    reports = [ report_format%(congress,chamber, i) for i in range(1,max_id+1) ]
    return reports

def write(path, content):
    """
    writes the content of a report id under the base_dir in the proper path
    content should be unicode, file is utf8 encoded
    """
    with codecs.open(path,'w','utf8') as f:
        f.write(content)
    
def print_congress_report_ids(congresses):
    """
    finds all the report ids in the given congresses and print them to std out
    """
    report_ids = []
    for congress in congresses:
        report_ids = report_ids + generate_reports_for_congress(congress, "hrpt")
        report_ids = report_ids + generate_reports_for_congress(congress, "srpt")
    for report in report_ids:
        print report

def download_and_write_report(report_id, base_dir):
    report_content = download_report(report_id)
    report_metadata = download_metadata(report_id)
    write_dir = construct_write_folder(base_dir, report_id)
    write(os.path.join(write_dir,report_id), report_content)
    write(os.path.join(write_dir,"mods.xml"), report_metadata)
    
def download_and_write_report_as_zip(report_id, base_dir):
    content = download_zipfile(report_id)
    bio = io.BytesIO(bytearray(content))
    zfile = zipfile.ZipFile(io.BufferedReader(bio))
    filenames = zfile.namelist()
    metadata_file = [name for name in filenames if name.endswith('mods.xml')][0]
    path = construct_write_folder(base_dir, report_id)
    tmp_dir = tempfile.gettempdir()
    htm_files = [name for name in filenames if name.endswith('htm')]
    zfile.extract(metadata_file, tmp_dir)
    metadata_file_name = metadata_file.split('/')[-1]
    shutil.move(os.path.join(tmp_dir, metadata_file), os.path.join(path, metadata_file_name))
    for htm_file in htm_files:
        htm_file_name = htm_file.split('/')[-1]
        zfile.extract(htm_file, tmp_dir)
        shutil.move(os.path.join(tmp_dir, htm_file), os.path.join(path, htm_file_name[5:-4]))# CRPT-107hrpt640-pt1.htm becomes 107hrpt640-pt1        
    shutil.rmtree(tmp_dir)
       
    
def find_missing_report_ids(reportsfile, outdir):
    with codecs.open(reportsfile,'r','utf8') as f:
        content = [line.strip() for line in f.readlines() if len(line) > 1]
    for rid in content:
        path = construct_write_folder(outdir, rid)
        if not os.path.exists(os.path.join(path,rid)) and not os.path.exists(os.path.join(path,rid+'-pt1')):
            print rid
    

def main():
    
    congresses = range(104,114)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_prepare = subparsers.add_parser('prepare', help='create folder strucutre')
    parser_prepare.add_argument('--outdir', required=True, help='root path under which files will be written')
    
    parser_print = subparsers.add_parser('print-ids', help='print out all report ids, \
     prepare need to be called before any fetch')
    
    parser_fetch = subparsers.add_parser('fetch', help='fetches report id and write it to path') 
    parser_fetch.add_argument('--outdir', required=True, help='root path under which files will be written')
    parser_fetch.add_argument('--reportid', required=True, help='the report id to be fetched')
    
    parser_diff = subparsers.add_parser('diff', help='finds the missing report ids that failed to download')
    parser_diff.add_argument('--outdir', required=True, help='the directory which hodls the downloaded reports')
    parser_diff.add_argument('--reportsfile', required=True, help='the file containing the report ids \
    which need to be checked')
    
    parser_fetch_zip = subparsers.add_parser('fetch-zip', help='fetches report id using the zip file and write ONLY the file and the metadata to path') 
    parser_fetch_zip.add_argument('--outdir', required=True, help='root path under which files will be written')
    parser_fetch_zip.add_argument('--reportid', required=True, help='the report id to be fetched')
    
    args = parser.parse_args()
    if args.subparser_name =="fetch":
        download_and_write_report(args.reportid, args.outdir)
    elif args.subparser_name == "print-ids":
        print_congress_report_ids(congresses)
    elif args.subparser_name == "prepare":
        setup_directories(args.outdir, congresses)
    elif args.subparser_name == "diff":
        find_missing_report_ids(args.reportsfile,args.outdir)
    elif args.subparser_name =="fetch-zip":
        download_and_write_report_as_zip(args.reportid, args.outdir)

if __name__ =="__main__":
    main()
    

    
