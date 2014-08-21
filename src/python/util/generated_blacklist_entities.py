import os, sys
import psycopg2
import argparse

import configuration
CONN_STRING =  configuration.get_connection_string()

def get_entities(max_occurence):
        conn = psycopg2.connect(CONN_STRING)
    #try:
        cmd = "select entity_text, entity_inferred_name, count(*) c from entities \
        where entity_type != 'Currency' group by entity_text, \
        entity_inferred_name having count(*) > %s  order by c desc"
        entities = set()
        cur = conn.cursor()
        cur.execute(cmd, (max_occurence,))
        records = cur.fetchall()
        for r in records:
            entities.add(r[0])
            entities.add(r[1])
        return entities
    #except Exception as ex:
        #print ex
        #raise ex
    #finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='find entities with occurance more than X')
    parser.add_argument('--max', required=True, type=int, help='maximum allowed occurance')
    args = parser.parse_args()
    #print args.max
    entities = get_entities(args.max)
    for e in entities:
        print e
    

if __name__=="__main__":
    main()
