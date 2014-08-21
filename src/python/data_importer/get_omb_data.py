import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
import urllib
import zipfile
from util import configuration

def main():
    if not os.path.exists(configuration.get_path_to_omb_data()):
        os.makedirs(configuration.get_path_to_omb_data())

    paths_to_files = ["http://earmarks.omb.gov/earmarks-public/resources/downloads/2010-appropriation-earmark-extract.zip",
                    "http://earmarks.omb.gov/earmarks-public/resources/downloads/2009-appropriations-earmark-extract.zip",
                    "http://earmarks.omb.gov/earmarks-public/resources/downloads/2008-appropriation-earmark-extract.zip",
                    "http://earmarks.omb.gov/earmarks-public/resources/downloads/appropriation-earmark-extract.zip"]

    for path in paths_to_files:
        urllib.urlretrieve(path, os.path.join(configuration.get_path_to_omb_data(), path.split("/")[-1]))
        zfile = zipfile.ZipFile(os.path.join(configuration.get_path_to_omb_data(), path.split("/")[-1]))
        zfile.extractall(configuration.get_path_to_omb_data())

if __name__ == "__main__":
    main()
