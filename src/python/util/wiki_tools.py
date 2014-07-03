import MySQLdb
import sys
import os
import codecs
import urllib2
import json
import requests
import ConfigParser
from urlparse import *

db = MySQLdb.connect(host="sunlight.c5faqozfo86k.us-west-2.rds.amazonaws.com",user="sunlight", passwd="govtrack", db="wikipedia")

def get_category_hierarchy(page_name, depth=1):
    """
    given a Wikipedia page name, return a list of its categories
    at the given depth
    """
    results = []
    results.append(get_categories(page_name))
    for i in range(1,depth):
        categories = []
        for category in results[i-1]:
            parent_categories = get_categories(category, True)
            categories = categories + parent_categories
        results.append(categories)

    return results


def get_categories(page_name, is_category=False):
    """
    given a Wikipedia page name, return a list of its categories
    """
    cur = db.cursor()
    namespace = 0
    if is_category:
        namespace = 14
    cur.execute("""SELECT cl_to FROM categorylinks cl
                JOIN page p ON cl.cl_from = p.page_id
                WHERE p.page_title="%s" AND page_namespace=%s;
            """ % (page_name, namespace))
    categories = [result[0] for result in cur.fetchall()]
    return categories

def get_wiki_urls_google(entity_name):
    query = "%s+site:en.wikipedia.org" % entity_name.replace(" ", "+")
    google_url = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % query
    r = requests.get(google_url)
    results = r.json()["responseData"]["results"]
    return [result["url"] for result in results]

def get_wiki_urls_bing(entity_name):
    bing_url = "https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web"
    key = get_key("bing")
    quoted_query = urllib2.quote("%s site:en.wikipedia.org" % entity_name)
    url = bing_url + r"?Query=%27" +quoted_query + r"%27&$format=json"
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url,key,key)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    content = urllib2.urlopen(url).read()
    j = json.loads(content)
    user_ids = []
    return [result["Url"] for result in j["d"]["results"]]

def get_key(key_type):
    cp = ConfigParser.ConfigParser()
    cp.read("./keys.cfg")
    return cp.get("keys", key_type)
