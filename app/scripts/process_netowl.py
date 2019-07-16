import requests
import os
import json
import string
import urllib3
import sys
import time
import copy

from elasticsearch import Elasticsearch
from app import app, db

# NetOwl Class Objects
class Text_Item:
    """Class to hold text content derived from NetOwl API"""
    
    
    def __init__(self, doc_id=None, text_content=None): 
        """Docstring."""
        self.id = doc_id
        self.content = text_content

class NetOwl_Entity:
    """Class to hold entities extracted from NetOwl API"""
    
    def __init__(self, value_dict=None): 
        """Docstring."""

        if 'id' in value_dict:
            self.id = value_dict['id']
        if 'ontology' in value_dict:
            self.ontology = value_dict['ontology']
        if 'value' in value_dict:
            self.value = value_dict['value']
        if 'norm' in value_dict:
            self.norm = value_dict['norm']
        if 'head' in value_dict:
            self.pre_text = value_dict['head']
        if 'tail' in value_dict:
            self.post_text = value_dict['tail']
        if 'doc_link' in value_dict:
            self.doc_link = value_dict['doc_link']
        if 'query' in value_dict:
            self.query = value_dict['query']
        if 'category' in value_dict:
            self.category = value_dict['category']
        if 'netowl-doc' in value_dict:
            self.document = value_dict['netowl-doc']

        if 'geo_entity' in value_dict:
            self.geo_entity = value_dict['geo_entity']
            self.loc = [value_dict['long'], value_dict['lat']]
            self.lat = value_dict['lat']
            self.long = value_dict['long']
            self.geo_type = value_dict['geo_type']
            self.geo_subtype = value_dict['geo_subtype']
        else:
            self.geo_entity = False

class NetOwl_Link:
    """Class to hold links extracted from NetOwl API"""
    
    def __init__(self, value_dict=None): 
        """Docstring."""
        
        if 'value' in value_dict:
            self.value = value_dict['value']
        if 'norm' in value_dict:
            self.norm = value_dict['norm']
        if 'ontology' in value_dict:
            self.ontology = value_dict['ontology']
        if 'role' in value_dict:
            self.role = value_dict['role']
        if 'role-type' in value_dict:
            self.role_type = value_dict['role-type']
        if 'role' in value_dict:
            self.link_role = value_dict['link-role']
        if 'role-type' in value_dict:
            self.link_role_type = value_dict['link-role-type']
        if 'value' in value_dict:
            self.link_value = value_dict['link-value']
        if 'value-type' in value_dict:
            self.link_value_type = value_dict['link-value-type']
        if 'idref' in value_dict:
            self.link_id = value_dict['link-id']
        if 'ent-ontology' in value_dict:
            self.ent_ontology = value_dict['ent-ontology']
        if 'link-ontology' in value_dict:
            self.link_ontology = value_dict['link-ontology']
        if 'netowl-doc' in value_dict:
            self.document = value_dict['netowl-doc']

class NetOwl_Event:
    """Class object to hold events extracted by the NetOwl API"""
    
    def __init__(self, value_dict=None): 
        """Docstring."""
        
        self.event_role = value_dict['event-role']
        self.event_value = value_dict['event-value']
        self.event_value_type = value_dict['event-value-type']
        self.event_id = value_dict['event-id']
        self.predicate = value_dict['predicate']
        self.ent_ontology = value_dict['ent-ontology']
        if 'netowl-doc' in value_dict:
            self.document = value_dict['netowl-doc']
            
        if 'triple' in value_dict:
            self.arg_role = value_dict['arg-role']
            self.arg_value = value_dict['arg-value']
            self.arg_value_type = value_dict['arg-value-type']
            self.arg_id = value_dict['arg-id']
            self.arg_ontology = value_dict['arg-ontology']
            self.triple = value_dict['triple']
        else:
            self.triple = False

# Functions to help in the process of a derived NetOwl JSON returned from the NetOwl API

# Abbreviated function that just processes the Entity objects derived from a process using the NetOwl API
def process_netowl_json(document_file, json_data):
    doc_entities = []
    doc_links = []
    doc_events = []
    
    # Open main portion of output NetOwl JSON
    if 'document' in json_data:
        document = json_data['document'][0]

        if 'text' in document:
            content = document['text'][0]['content']
                        
        if 'entity' in document:
            # Build entity objects
            ents = (document['entity'])  # gets all entities in doc

            # Iterates through entities in the document
            for e in ents:
                base_entity = {}

                # gather data from each entity
                rdfvalue = cleanup_text(e['value'])  # value (ie name)
                rdfid = e['id']
                rdfid = document_file.split(".")[0] + "_e_" + rdfid  # unique to each entity
                e['id'] = rdfid

                base_entity['id'] = rdfid

                if 'ontology' in e:
                    base_entity['ontology'] = e['ontology']
                if 'value' in e:
                    base_entity['value'] = e['value']
                if 'norm' in e:
                    base_entity['norm'] = e['norm']

                if 'geodetic' in e:
                    base_entity['geo_entity'] = True
                    base_entity['lat'] = float(e['geodetic']['latitude'])
                    base_entity['long'] = float(e['geodetic']['longitude'])

                # check for addresses
                if e['ontology'] == "entity:address:mail":
                    address = e['value']
                    location = geocode_address(address)  # returns x,y

                    base_entity['geo_entity'] = True
                    base_entity['lat'] = location['y']
                    base_entity['long'] = location['x']
                    
                # Sets the type of the geo-entity to allow for better symbology

                if 'geo_entity' in base_entity:
                    base_entity['geo_type'] = "placename"
                    base_entity['geo_subtype'] = "unknown"

                    if e['ontology'] == "entity:place:city":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "city"
                    if e['ontology'] == "entity:place:country":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "country"
                    if e['ontology'] == "entity:place:province":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "province"
                    if e['ontology'] == "entity:place:continent":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "continent"
                    if e['ontology'] == "entity:numeric:coordinate:mgrs":
                        base_entity['geo_type'] = "coordinate"
                        base_entity['geo_subtype'] = "MGRS"
                    if e['ontology'] == "entity:numeric:coordinate:latlong":
                        base_entity['geo_type'] = "coordinate"
                        base_entity['geo_subtype'] = "latlong"
                    if e['ontology'] == "entity:address:mail":
                        base_entity['geo_type'] = "address"
                        base_entity['geo_subtype'] = "mail"
                    if e['ontology'] == "entity:place:other":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "descriptor"
                    if e['ontology'] == "entity:place:landform":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "landform"
                    if e['ontology'] == "entity:organization:facility":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "facility"
                    if e['ontology'] == "entity:place:water":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "water"
                    if e['ontology'] == "entity:place:county":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "county"
                
                if 'entity-mention' in e:
                    em = e['entity-mention'][0]
                    if 'head' in em:
                        base_entity['head'] = get_head(content, int(em['head']), 255)
                    if 'tail' in em:
                        base_entity['tail'] = get_tail(content, int(em['tail']), 255)


                # Turns entity information into a class object for storage and transformation
                netowl_entity_object = NetOwl_Entity(base_entity)
                doc_entities.append(netowl_entity_object)
                
        return doc_entities

def netowl_curl(infile, outpath, outextension, netowl_key):
    """Do James Jones code to query NetOwl API."""
    headers = {
        'accept': 'application/json',  # 'application/rdf+xml',
        'Authorization': netowl_key,
    }

    if infile.endswith(".txt"):
        headers['Content-Type'] = 'text/plain'
    elif infile.endswith(".pdf"):
        headers['Content-Type'] = 'application/pdf'
    elif infile.endswith(".docx"):
        headers['Content-Type'] = 'application/msword'

    params = {"language": "english", "text": "", "mentions": ""}

    data = open(infile, 'rb').read()
    response = requests.post('https://api.netowl.com/api/v2/_process',
                             headers=headers, params=params, data=data,
                             verify=False)

    r = response.text
    outpath = outpath
    filename = os.path.split(infile)[1]
    if os.path.exists(outpath) is False:
        os.mkdir(outpath, mode=0o777, )
    outfile = os.path.join(outpath, filename + outextension)
    open(outfile, "w", encoding="utf-8").write(r)

def cleanup_text(intext):
    """Function to remove funky chars."""
    printable = set(string.printable)
    p = ''.join(filter(lambda x: x in printable, intext))
    g = p.replace('"', "")
    return g

def geocode_address(address):
    """Use World Geocoder to get XY for one address at a time."""
    querystring = {
        "f": "json",
        "singleLine": address}
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"  # noqa: E501
    response = requests.request("GET", url, params=querystring)
    p = response.text
    j = json.loads(p)
    location = j['candidates'][0]['location']  # returns first location as X, Y
    return location

def get_head(text, headpos, numchars):
    """Return text before start of entity."""
    wheretostart = headpos - numchars
    if wheretostart < 0:
        wheretostart = 0
    thehead = text[wheretostart: headpos]
    return thehead

def get_tail(text, tailpos, numchars):
    """Return text at end of entity."""
    wheretoend = tailpos + numchars
    if wheretoend > len(text):
        wheretoend = len(text)
    thetail = text[tailpos: wheretoend]
    return thetail

# Full NetOwl JSON Conversion
def process_netowl_full_json(document_file, json_data, document_id):
    doc_entities = []
    doc_links = []
    doc_events = []
    
    # Open main portion of output NetOwl JSON
    if 'document' in json_data:
        document = json_data['document'][0]
                    
        # Extract source text that is embedded in NetOwl JSON and save it as a Text_Item class object
        if 'text' in document:
            content = document['text'][0]['content']
                        
            content_object = Text_Item(doc_id=document_file, text_content=content)
                        
        if 'entity' in document:
            # Build entity objects
            ents = (document['entity'])  # gets all entities in doc

            # Iterates through entities in the document
            for e in ents:
                base_entity = {}

                web_path = r"http://40.76.87.212/camera/docs/" + os.path.split(document_file)[1]
                base_entity['url'] = web_path

                # gather data from each entity
                rdfvalue = cleanup_text(e['value'])  # value (ie name)
                rdfid = e['id']
                rdfid = document_file.split(".")[0] + "_e_" + rdfid  # unique to each entity
                e['id'] = rdfid

                base_entity['id'] = rdfid
                base_entity['netowl-doc'] = document_id

                if 'ontology' in e:
                    base_entity['ontology'] = e['ontology']
                if 'value' in e:
                    base_entity['value'] = e['value']
                if 'norm' in e:
                    base_entity['norm'] = e['norm']

                if 'geodetic' in e:
                    base_entity['geo_entity'] = True
                    base_entity['lat'] = float(e['geodetic']['latitude'])
                    base_entity['long'] = float(e['geodetic']['longitude'])

                # check for addresses
                if e['ontology'] == "entity:address:mail":
                    address = e['value']
                    location = geocode_address(address)  # returns x,y

                    base_entity['geo_entity'] = True
                    base_entity['lat'] = location['y']
                    base_entity['long'] = location['x']
                    
                # Sets the type of the geo-entity to allow for better symbology

                if 'geo_entity' in base_entity:
                    base_entity['geo_type'] = "placename"
                    base_entity['geo_subtype'] = "unknown"

                    if e['ontology'] == "entity:place:city":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "city"
                    if e['ontology'] == "entity:place:country":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "country"
                    if e['ontology'] == "entity:place:province":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "province"
                    if e['ontology'] == "entity:place:continent":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "continent"
                    if e['ontology'] == "entity:numeric:coordinate:mgrs":
                        base_entity['geo_type'] = "coordinate"
                        base_entity['geo_subtype'] = "MGRS"
                    if e['ontology'] == "entity:numeric:coordinate:latlong":
                        base_entity['geo_type'] = "coordinate"
                        base_entity['geo_subtype'] = "latlong"
                    if e['ontology'] == "entity:address:mail":
                        base_entity['geo_type'] = "address"
                        base_entity['geo_subtype'] = "mail"
                    if e['ontology'] == "entity:place:other":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "descriptor"
                    if e['ontology'] == "entity:place:landform":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "landform"
                    if e['ontology'] == "entity:organization:facility":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "facility"
                    if e['ontology'] == "entity:place:water":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "water"
                    if e['ontology'] == "entity:place:county":
                        base_entity['geo_type'] = "placename"
                        base_entity['geo_subtype'] = "county"

                if 'entity-mention' in e:
                    em = e['entity-mention'][0]
                    if 'head' in em:
                        base_entity['head'] = get_head(content, int(em['head']), 255)
                    if 'tail' in em:
                        base_entity['tail'] = get_tail(content, int(em['tail']), 255)

                # Turns entity information into a class object for storage and transformation
                #netowl_entity_object = NetOwl_Entity(base_entity)
                doc_entities.append(base_entity)

                # Returns extracted links from the entity
                if 'link-ref' in e:
                    base_entity['has_links'] = True

                    base_link = {}

                    base_link['id'] = rdfid
                    base_link['netowl-doc'] = document_id

                    if 'value' in e:
                        base_link['value'] = e['value']
                    if 'norm' in e:
                        base_link['norm'] = e['norm']
                    link_ref = e['link-ref']
                    for link in link_ref:
                        copy_link = copy.deepcopy(base_link)
                        if 'ontology' in link:
                            copy_link['ontology'] = link['ontology']
                        if 'role' in link:
                            copy_link['role'] = link['role']
                        if 'role-type' in link:
                            copy_link['role-type'] = link['role-type']
                        if 'role' in link['entity-arg'][0]:
                            copy_link['link-role'] = link['entity-arg'][0]['role']
                        if 'role-type' in link['entity-arg'][0]:
                            copy_link['link-role-type'] = link['entity-arg'][0]['role-type']
                        if 'value' in link['entity-arg'][0]:
                            copy_link['link-value'] = link['entity-arg'][0]['value']
                        if 'value-type' in link['entity-arg'][0]:
                            copy_link['link-value-type'] = link['entity-arg'][0]['value-type']
                        if 'idref' in link['entity-arg'][0]:
                            copy_link['link-id'] = document_file.split(".")[0] + "_e_" + link['entity-arg'][0]['idref']
                        if 'ontology' in link:
                            copy_link['link-ontology'] = link['entity-arg'][0]['ontology']
                            copy_link['ent-ontology'] = e['ontology']

                            netowl_link_object = NetOwl_Link(copy_link)
                            doc_links.append(copy_link)
            
        # Determines if there are extracted links in the document
        if 'link' in document:
            links = (document['link'])
            for link in links:
                base_link = {}

                base_link['netowl-doc'] = document_id
                base_link['ontology'] = link['ontology']
                entity_arg1 = link['entity-arg'][0]
                entity_arg2 = link['entity-arg'][1]
                
                base_link['role'] = entity_arg1['role']
                base_link['role-type'] = entity_arg1['role-type']
                base_link['value'] = entity_arg1['value']
                base_link['role'] = entity_arg1['role']
                base_link['id'] = document_file.split(".")[0] + "_e_" + entity_arg1['idref']
                base_link['ent-ontology'] = entity_arg1['ontology']
                base_link['link-role'] = entity_arg2['role']
                base_link['link-role-type'] = entity_arg2['role']
                base_link['link-value'] = entity_arg2['value']
                base_link['link-value-type'] = entity_arg2['value-type']
                base_link['link-id'] = document_file.split(".")[0] + "_e_" + entity_arg2['idref']
                base_link['link-ontology'] = entity_arg2['ontology']
                
                #netowl_link_object = NetOwl_Link(base_link)
                doc_links.append(netowl_link_object)

        # Determines if there are extracted events in the document
        if 'event' in document:
            events = (document['event'])
            for event in events:
                base_event = {}
                
                base_event['netowl-doc'] = document_id
                event_args = event['entity-arg']
                event_properties = event['property'][0]
                    
                
                base_event['event-role'] = event_args[0]['role']
                base_event['event-value'] = event_args[0]['value']
                base_event['event-value-type'] = event_args[0]['value-type']
                base_event['event-id'] = document_file.split(".")[0] + "_e_" + event_args[0]['idref']
                base_event['ent-ontology'] = event_args[0]['ontology']
                base_event['predicate'] = event_properties['value']
                
                if len(event['entity-arg']) > 1:
                    count = 0
                    for arg in event_args:
                        count +=1
                        if count == 1:
                            pass
                        else:
                            arg_dict = base_event.copy()
                            event_arg = event['entity-arg'][1]
                            arg_dict['arg-role'] = arg['role']
                            arg_dict['arg-value'] = arg['value']
                            arg_dict['arg-value-type'] = arg['value-type']
                            arg_dict['arg-id'] = document_file.split(".")[0] + "_e_" + arg['idref']
                            arg_dict['arg-ontology'] = arg['ontology']
                            arg_dict['triple'] = True
                    
                            netowl_event_object = NetOwl_Event(arg_dict)
                            doc_events.append(netowl_event_object)

                else:
                    #netowl_event_object = NetOwl_Event(base_event)
                    doc_events.append(base_event)
                
        return doc_entities, doc_links, doc_events

def create_node_relationship(node_a, node_a_type, node_b, node_b_type, relationship_type, graph_object):
    a = Node(node_a_type, name=node_a)
    a.__primarylabel__ = node_a_type
    a.__primarykey__ = "name"
    b = Node('Entity', name=node_b)
    b.__primarylabel__ = node_b_type
    b.__primarykey__ = "name"
    relationship = Relationship.type(relationship_type)
    graph_object.merge(relationship(a,b))

def create_node_watchlist(entity, entity_type, watchlist_name, graph_object):
    a = Node(entity_type, name=entity)
    a.__primarylabel__ = entity_type
    a.__primarykey__ = "name"
    c = Node("Watchlist", name=watchlist_name)
    c.__primarylabel__ = "Watchlist"
    c.__primarykey__ = "name"
    WORKS_FOR = Relationship.type("ON_WATCHLIST")
    graph_object.merge(WORKS_FOR(a, c))

def create_spatially_enabled_df(gis_connection, portal_item_id, item_layer_postion):
    item = gis_connection.content.get(portal_item_id)
    flayer = item.layers[item_layer_postion]
    spatially_enabled_df = pd.DataFrame.spatial.from_layer(flayer)

    return spatially_enabled_df

def netowl_pipeline(file):
    directory = app.config['NETOWL_INT_FOLDER']
    netowl_key = app.config['NETOWL_KEY']

    start_time = time.time()

    print("Processing {}".format(file))

    if os.path.exists(file):

        try:

            netowl_curl(file, directory, '.json', netowl_key)

            with open(os.path.join(directory, os.path.split(file)[1] +'.json'), 'rb') as json_file:
                data = json.load(json_file)

                es = app.elasticsearch.index(index='netowl',doc_type='document', body=data)
                doc_id = es['_id']

                entity_list, links_list, events_list = process_netowl_full_json(file, data, doc_id)

            end_time = time.time()
            total_time = end_time - start_time
            print("Document had {0} entities, {1} links, and {2} events.".format(str(len(entity_list)), str(len(links_list)), str(len(events_list))))
            print("Successfully processsed " + str(file))
            print("Process took {} seconds.".format(str(total_time)))
            print("-----------------------------------------------------------")

            return entity_list, links_list, events_list
        
        except Exception as e:
            return "Error", str(e), ""

