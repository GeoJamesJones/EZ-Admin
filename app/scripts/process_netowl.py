import requests
import os
import json
import string
import urllib3
import sys

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

        if 'geo_entity' in value_dict:
            self.geo_entity = value_dict['geo_entity']
            self.loc = [value_dict['long'], value_dict['lat']]
            self.lat = value_dict['lat']
            self.long = value_dict['long']
            self.geo_type = value_dict['geo_type']
            self.geo_subtype = value_dict['geo_subtype']
        else:
            self.geo_entity = False

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