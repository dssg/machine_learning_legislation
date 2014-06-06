import os, sys
from sunlight import congress
from  sunlight.services.congress import Congress
from sunlight.pagination import PagingService
import pickle
import codecs, urllib2

USAGE = "python %s <output-dir> |<bills-pickled-data-file>|"%(sys.argv[0])

def fetch_bills_info():
    """
    downlaods bill metadata from the sunlight api
    currently it downloads all the bills available in sunlight api
    consider supporting other filters in the future, like time ..etc
    """
    congress = Congress()
    congress = PagingService(congress)
    results = list (congress.bills(fields="versions,history,title,urls,id" ,limit=sys.maxint  ) )
    return results
    #pickle.dump(results, open('bills.dat','wb'))
    
    
def download_bill_version(url):
    """
    downlaod a version of a bill given at the url
    """
    response = urllib2.urlopen(url)
    content = response.read()
    return content.decode('utf8')
    
def write_bill_version(path, content):
    """
    writes the content of a bill to a given path
    """
    f = codecs.open(path,'w','utf8')
    f.write(content)
    f.close()
    
def handle_bill(bill, output_folder):
    """
    handles a bill after its metadata was downloaded from sunlight
    fetch all versions and write them to the disk
    bill: object fetched from sunlight api
    output_folder: the root folder in which the data will be written
    """
    bill_id = bill['bill_id']
    if not bill.has_key('versions'):
        print "Passing on bill %s as no versions are available" %(bill_id)
    else:
        versions = bill['versions']
        bill_folder = os.path.join(output_folder, bill_id)
        if not os.path.exists( bill_folder):
            os.mkdir( bill_folder )
        for v in versions:
            version_code = v['version_code']
            bill_version_id = v['bill_version_id']
            url = v['urls']['html']
            version_folder = os.path.join(bill_folder, version_code)
            if not os.path.exists(version_folder):
                os.mkdir(version_folder)
            v_content = download_bill_version(url)
            version_path = os.path.join(version_folder, bill_version_id)
            write_bill_version(version_path, v_content)
    
    
def main():
    """
    main function
    """
    if len(sys.argv) == 3:
        bills = pickle.load(open(sys.argv[2],'rb'))
    else:
        bills = fetch_bills_info()
    #print bills[100]
    #with_version = len([ b for b in bills if b.has_key('versions') ])
    #print "%d bills were fetched, of which %d have versions"%(len(bills), with_version)
    for i in range(len( bills)):
        try:
            handle_bill(bills[i], sys.argv[1])
        except Exception as exp:
            print "failed to process bill %d"%(i), exp
        
    
    
    
if __name__=="__main__":
    if len(sys.argv) < 2:
        print USAGE
    else: 
        main()


