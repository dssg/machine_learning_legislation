import os, sys
from calais import Calais
import codecs
import random
import psycopg2

USAGE = "python %s <bill-version-file>"
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
            for instance in calais_entity['instances']:
                e = Entity()
                e.name = e_name
                e.type = e_type
                e.offset = offset + instance['offset']
                e.length = instance['length']
                e.text = instance['exact']
                entities.append(e)
        return entities
            
    except Exception as exp:
        print exp
        return []
    
    
def handle_file(bill_id, content):
    clean_content = content[17:]
    offset = 17
    chunks = chunk_file(clean_content)
    entities = []
    for chunk in chunks:
        entities = entities + extract_entities(chunk, offset)
        offset += len(chunk)
    insert_entities_to_db(entities, bill_id)
    
        
    
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
    
def insert_entities_to_db(entities, bill_id):
    conn = psycopg2.connect(CONN_STRING)
    cmd = "insert into billentities (entity_text, entity_type, entity_offset, \
    entity_length, entity_name, bill_id) values (%s, %s, %s, %s, %s, %s)"
    params = [(e.text, e.type, e.offset, e.length, e.name, bill_id) for e in entities]
    cur = conn.cursor()
    cur.executemany(cmd, params)
    conn.commit()
    conn.close()
    
def main():
    content = read_file(sys.argv[1])
    bill_id = sys.argv[1].split('/')[-1]
    handle_file(bill_id,content)
    
if __name__=="__main__":
    if len(sys.argv)<2:
        print USAGE
    else:
        main()
    
    

