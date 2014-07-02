import os, sys
import argparse
import urllib2
import codecs
import shutil
import tempfile

import congress_report_downloader

def get_max_congress_plaw_number(congress):
    path_format = "/fdsys/pkg/PLAW-%dpubl%d/mods.xml"
    max_id=1000
    min_id=1
    while congress_report_downloader.get_request_status(path_format%(congress, max_id)) == 200:
        min_id=max_id
        max_id = max_id * 2
    while max_id - min_id > 1:
        middle = (max_id + min_id) / 2
        result = congress_report_downloader.get_request_status(path_format%(congress, middle))
        if result == 200:
            min_id = middle
        else:
            max_id = middle
    return min_id
    
def setup_directories(root_dir, congresses):
    """
    creates the needed directories under the home path
    such that each congress has it's own sub folder
    """
    for congress in congresses:
        path = os.path.join(root_dir,str(congress))
        if not os.path.exists(path):
            os.mkdir(path)

def download_metadata(congress, plaw_number):
    """
    downlaods metadata for plaw number given for congress
    """
    url = "http://www.gpo.gov/fdsys/pkg/PLAW-%dpubl%d/mods.xml"%(congress,plaw_number)
    return congress_report_downloader.download(url).decode('utf8')  
    
    
def construct_write_path(base_dir, congress, plaw_number):
    """
    returns the directory path into which the plaw file need to be written
    """
    path = os.path.join(base_dir, str(congress))
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, str(plaw_number))
    if not os.path.exists(path):
        os.mkdir(path)
    return path
    
def download_and_write_plaw(congress, plaw_number, base_dir):
    content = download_metadata(congress, plaw_number)
    write_dir = construct_write_path(base_dir, congress, plaw_number)
    congress_report_downloader.write(os.path.join(write_dir,"mods.xml"), content)
    
def main():
    #congresses = range(108,112)
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name' ,help='sub-command help')
    
    parser_prepare = subparsers.add_parser('prepare', help='create folder strucutre')
    parser_prepare.add_argument('--outdir', required=True, help='root path under which files will be written')
    parser_prepare.add_argument('--congresses', required=True, type=int, nargs='+',
    help='the congress numbers for which to operate')
    
    parser_fetch = subparsers.add_parser('fetch', help='fetches public laws for congresses') 
    parser_fetch.add_argument('--outdir', required=True, help='root path under which files will be written')
    parser_fetch.add_argument('--congresses', required=True, type=int, nargs='+',
    help='the congress numbers for which to operate')
    
    args = parser.parse_args()
    congresses = args.congresses
    if args.subparser_name =="fetch":
        for congress in congresses:
            max_plaw = get_max_congress_plaw_number(congress)
            print "==%d public laws to fetch for congress %d =="%(max_plaw, congress)
            for i in range(1,max_plaw+1):
                print 'Fetching PLaw %d-%d'%(congress, i)
                download_and_write_plaw(congress, i, args.outdir)
    elif args.subparser_name == "prepare":
        setup_directories(args.outdir, congresses)
        
    
if __name__=="__main__":
    main()
                
    