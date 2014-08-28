import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import urllib
import zipfile
from util import configuration

omb_path = configuration.get_path_to_omb_data()

def download_and_extract(url):
    path_to_new_zip = os.path.join(omb_path,url.split("/")[-1])
    urllib.urlretrieve(url, path_to_new_zip)
    zfile = zipfile.ZipFile(path_to_new_zip)
    zfile.extractall(omb_path)

def get_2010_earmarks():
    url= "http://earmarks.omb.gov/earmarks-public/resources/downloads/2010-appropriation-earmark-extract.zip"
    download_and_extract(url)
    os.rename(os.path.join(omb_path, "2010-appropriations-earmark-extract.csv"), os.path.join(omb_path, "2010.csv"))

def get_2009_earmarks():
    url= "http://earmarks.omb.gov/earmarks-public/resources/downloads/2009-appropriations-earmark-extract.zip"
    download_and_extract(url)
    os.rename(os.path.join(omb_path, "2009-appropriations-earmark-extract.csv"), os.path.join(omb_path, "2009.csv"))

def get_2008_earmarks():
    url= "http://earmarks.omb.gov/earmarks-public/resources/downloads/2008-appropriation-earmark-extract.zip"
    download_and_extract(url)
    os.rename(os.path.join(omb_path, "database.csv"), os.path.join(omb_path, "2008.csv"))

def get_2005_earmarks():
    url= "http://earmarks.omb.gov/earmarks-public/resources/downloads/appropriation-earmark-extract.zip"
    download_and_extract(url)
    os.rename(os.path.join(omb_path, "database.csv"), os.path.join(omb_path, "2005.csv"))

def main():
    if not os.path.exists(omb_path):
        os.makedirs(omb_path)
    get_2010_earmarks()
    get_2009_earmarks()
    get_2008_earmarks()
    get_2005_earmarks()


if __name__ == "__main__":
    main()
