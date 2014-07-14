import MySQLdb
import sys
import os
import codecs
import urllib
import urllib2
import json
import requests
import ConfigParser
from urlparse import *
import time

db = MySQLdb.connect(host="sunlight.c5faqozfo86k.us-west-2.rds.amazonaws.com",user="sunlight", passwd="govtrack", db="wikipedia")

def get_category_hierarchy(page_name, depth=1):
    """
    given a Wikipedia page name, return a list of its categories
    up to the given depth
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

def get_wiki_page_title_google(entity_name, max_tries = 5):
    query = '%s site:en.wikipedia.org' % (entity_name)
    query = urllib.quote(query)
    google_url = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % query
    wait_time = 3
    for i in range(max_tries):
        try:
            print i
            r = requests.get(google_url)
            results = r.json()["responseData"]["results"]
            if len(results) > 0:
                return [result["url"].split("/")[-1] for result in results]
            else:
                return []
        except Exception as ex:
            time.sleep(wait_time)
            wait_time = wait_time * 2
            pass
    print "Warning: max retries reached with query %s" %(entity_name)
    return []
    
def get_wiki_page_title_google_cse(entity_name, max_tries = 5):
    """
    MAKE SURE TO DELETE THIS FUNCTION BEFORE OPEN SOURCING THE CODE
    here no need to filter with wikipedia, cse already filters for wikipedia
    """
    pass
    query = urllib.quote(entity_name)
    google_url = "https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=10&hl=en&prettyPrint=false&source=gcsc&gss=.com&cx=016849338463251080306:gukdipzeymu&sort=&googlehost=www.google.com&oq=a&q=%s" % query
    wait_time = 3
    for i in range(max_tries):
        try:
            r = requests.get(google_url)
            results = r.json()["results"]
            if len(results) > 0:
                return [result["url"].split("/")[-1] for result in results]
            else:
                return []
        except Exception as ex:
            print "error in try %d for query %s" %(i, entity_name),  ex
            time.sleep(wait_time)
            pass
    print "Warning: max retries reached with query %s" %(entity_name)
    return []

def get_wiki_page_title_bing(entity_name, max_tries = 5):
    bing_url = "https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web"
    key = "WGFuNGBlImIYGVdsYsCUHzDA3oX/4CEgYhuYOF0UrE0"#get_key("bing")
    quoted_query = urllib2.quote('%s site:en.wikipedia.org' % entity_name)
    url = bing_url + r"?Query=%27" +quoted_query + r"%27&$format=json"
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url,key,key)
    urls = []
    for i in range(max_tries):
        try:
            handler = urllib2.HTTPBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)
            content = urllib2.urlopen(url).read()
            j = json.loads(content)
            user_ids = []
            if j.has_key("d"):
                if j["d"].has_key("results"):
                    if len(j["d"]["results"]) > 0:
                        urls= [result["Url"].split("/")[-1] for result in j["d"]["results"]]
                        return urls
        except Exception as ex:
            pass
    return urls            

def get_key(key_type):
    cp = ConfigParser.ConfigParser()
    cp.read("./keys.cfg")
    return cp.get("keys", key_type)
