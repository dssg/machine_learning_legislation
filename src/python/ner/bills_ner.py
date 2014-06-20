import os, sys, inspect
sys.path.insert(0, os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],".."))))
from calais import Calais
import codecs
import random
import psycopg2
from util import path_tools

USAGE = "python %s <bill-version-file> <bill|report>"
API_KEYS = ["wdbkpbpsksskkbm2rpqfm4xa", "mt5qu3e4jdrd6jpc9r9ecama",
"k9fb7rfh7hpbfp238whuggrr","55rared7un2pnjr23kjtctes"]
MAX_TEXT_LENGTH = 100000
calaises = [Calais(key, submitter="python-calais-demo") for key in API_KEYS]
CONN_STRING = "dbname=harrislight user=harrislight password=harrislight host=dssgsummer2014postgres.c5faqozfo86k.us-west-2.rds.amazonaws.com"



class Entity:
    def __str__(self):
        return "%s | %s | %s | %d:%d" %(self.text, self.name, 
        self.type, self.offset, self.offset + self.length)

def read_file(path):
    with codecs.open(path,'r','utf8') as f:
        content = f.read()
        return content
    
def extract_entities(text, offset=0):
    """
    extract entities from text, returns a list of Entity objects
    text: plain text, not html. typical congress bill starts with html tag which need to be stripped
    offset: the offset within the bill at which text start
    """
    try:
        entities = []
        calais = calaises[ random.randint(0, len(calaises)-1 ) ]
        result = calais.analyze(text)
        for calais_entity in result.entities:
            e_type = calais_entity['_type']
            e_name = calais_entity['name']
            e_url = None
            if calais_entity.has_key('resolutions'):
                e_url=calais_entity['resolutions']['id']
            for instance in calais_entity['instances']:
                e = Entity()
                e.name = e_name
                e.type = e_type
                e.url = e_url
                e.offset = offset + instance['offset']
                e.length = instance['length']
                e.text = instance['exact']
                entities.append(e)
        return entities
            
    except Exception as exp:
        print exp
        return []
    
    
def handle_file(document_path, content, doc_type):
    """
    doc_type: bill or report
    """
    clean_content = content
    offset = 0
    if doc_type == 'report':
        text_mark = "<body><pre>"
        i = clean_content.find(text_mark)
        if i > 0:
            clean_content = clean_content[i+len(text_mark):]
            offset = i + len(text_mark)
    chunks = chunk_file(clean_content)
    entities = []
    for chunk in chunks:
        entities = entities + extract_entities(chunk, offset)
        offset += len(chunk)
    insert_entities_to_db(entities, document_path, doc_type)
    
        
    
def chunk_file(content):
    """
    chunks the content of a file into multiple sections, each section 
    has at most 100,000 characters because opencalias has limit of 100k
    on the input text length
    """
    if len(content) < MAX_TEXT_LENGTH:
        return [content,]
    else:
        chunks = []
        while len(content) > MAX_TEXT_LENGTH:
            chunk = get_chunk(content, MAX_TEXT_LENGTH)
            chunks.append(chunk)
            content = content[len(chunk):]
        chunks.append(content)
        return chunks

def get_chunk(text, limit):
    chunk = text = text[:limit]
    if chunk[-1] == '\n':
        return chunk
    else:
        return chunk[:chunk.rfind('\n') + 1]
    
def insert_entities_to_db(entities, document_path, doc_type):
    conn = psycopg2.connect(CONN_STRING)
    cmd = "insert into entities (entity_text, entity_type, entity_offset, \
    entity_length, entity_inferred_name, source,  document_id, entity_url) values (%s, %s, %s, %s, %s,'calais',%s, %s)"
    if doc_type =='senate':
        obj = path_tools.BillPathUtils(document_path)
    else:
        obj = path_tools.ReportPathUtils(document_path)
    doc_id = obj.get_db_document_id() 
    params = [(e.text, e.type, e.offset, e.length, e.name, doc_id, e.url) for e in entities]
    cur = conn.cursor()
    cur.executemany(cmd, params)
    conn.commit()
    conn.close()
    
def main():
    content = read_file(sys.argv[1])
    document_path = sys.argv[1]
    doc_type = sys.argv[2]
    handle_file(document_path,content, doc_type)
    
if __name__=="__main__":
    if len(sys.argv)<3:
        print USAGE
    else:
        main()
    
    

