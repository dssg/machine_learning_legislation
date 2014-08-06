

import multiprocessing as mp
from dao.Entity import Entity
from dao.Earmark import Earmark
from classification import instance
from entity_attributes import EntityAttributes
from earmark_attributes import EarmarkAttributes

def get_matching_instance(entity_attributes, earmark_attributes, target_class = 1):

    i = instance.Instance(target_class = target_class)
    i.attributes['entity'] =  entity_attributes
    i.attributes['earmark']=  earmark_attributes
    i.attributes['document_id'] = i.attributes['entity'].entity.document_id
    i.attributes['earmark_id'] = i.attributes['earmark'].earmark.earmark_id
    return i



def get_matching_instances(entity_ids, earmark_ids, earmark_entity_tuples, num_processes):

    earmark_attributes_dict = get_earmark_attributes_dict(earmark_ids,num_processes)
    entity_attributes_dict =  get_entity_attributes_dict(entity_ids, num_processes) 
    return [ get_matching_instance(entity_attributes_dict[t[0]], earmark_attributes_dict[t[1]], t[2]) for t in earmark_entity_tuples ] 



def get_entity_attributes_dict(entity_ids, num_processes):
    if num_processes == 1:
        d = {}
        for entity_id in entity_ids:
            d[entity_id] = get_entity_attribute(entity_id)[1]
        return d
    else:
        p = mp.Pool(num_processes)
        return dict(p.map(get_entity_attribute, entity_ids))


def get_earmark_attributes_dict(earmark_ids,num_processes):
    if num_processes == 1:
        d = {}
        for earmark_id in earmark_ids:
            d[earmark_id] = get_earmark_attribute(earmark_id)[1]
        return d
    else:
        p = mp.Pool(num_processes)
        return dict(p.map(get_earmark_attribute, earmark_ids))


def get_entity_attribute(entity_id):
    return (entity_id, EntityAttributes(Entity(entity_id)))


def get_earmark_attribute(earmark_id):
    return (earmark_id, EarmarkAttributes(Earmark(earmark_id)))