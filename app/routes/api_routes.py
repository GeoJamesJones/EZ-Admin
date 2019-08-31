from app import app, db

from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from random import randint
from copy import deepcopy
from arcgis.gis import GIS

from app.scripts import detect_faces
from app.scripts.geoevent import post_to_geoevent, put_to_geoevent
from app.models.models import User, Post, NetOwl_Entity
from app.scripts.process_netowl import cleanup_text, netowl_pipeline, geocode_address

import requests
import os
import json
import string
import urllib3
import sys
import uuid
import datetime

# Temporary dictionary that will hold temporary Job status. 
# Eventually need to expand this functionality. 
jobs = {}

# Specifies the allowed file extensions for processing by the NetOwl Process. 
ALLOWED_EXTENSIONS = set(['doc', 'docx', 'txt', 'htm', 'html', 'pdf', 'jpg', 'png'])

# Helper function that defines the allowable files types for receipt on this API.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Allows for a quick query of jobs that have ran during this session. 
# Job info is stored in the jobs dictionary above.  
# Temporary solution, looking for longer term option...
@app.route('/api/v1.0/job-info', methods=['GET'])
def job_info():
    return jsonify(jobs)

# API Route that processes News Articles that are posted the Endpoint. 
# Current setup has data being fed to this process using a Microsoft Flow
# Webhook. 
# This Route has a dependency on being able to access a NetOwl NLP Service. 
# The response object for the NetOwl API is expected to be a JSON, and this process
# is tailored to process that data. 

@app.route('/api/news-rss', methods=['POST'])
def news_rss():
    """Expected POST form will contain the following items 'link', 'published', 'title',
    'updated', and 'copyright'. """
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "News RSS"
    if request.method == 'POST':
        directory = app.config['NETOWL_INT_FOLDER']
        
        # Converts POST form into a JSON object
        content = request.get_json()
        
        # Reads items from previous step into variables
        article_link = content["link"]
        published = content["published"]
        title = content["title"]
        updated = content["updated"]
        cright = content["copyright"]

        # Downloads the article and parses it so that it may be further processed.
        r = requests.get(article_link, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, features="html.parser")

        # Extracts the visible text from the article and stores it as plain text.
        soup_list = [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        visible_text = soup.getText()

        # Saves the extracted plain text as a text file in the temp directory specified in the Config file.
        filename = title.replace(" ", "_")
        text_file_path = os.path.join(directory, filename + '.txt')
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            print_text = cleanup_text(visible_text)
            text_file.write(print_text)
            text_file.close()


        if os.path.exists(text_file_path):
            print(text_file_path)
        
            # Main script that process the extracted, visible plain text using the NetOwl API
            # The script is stored in the ../Scripts folder in the process_netowl.py folder
            # Requires access to the NetOwl API. NetOwl API Key and URI is stored in Config file.
            # NetOwl Pipeline returns 3 lists of dictionary objects. 
            entities, links, events = netowl_pipeline(text_file_path) 

            entity_list = []
            links_list = []
            events_list = []
            se_list = []
            document = ''

            try:
                # Processes the Entities list, extracts GeoEntites
                # Spatial Entities are stored in the se_list
                # All entities are stored in the entities_list
                # This allows for the entire processed list to passed to the GeoEvent URL.
                for entity in entities:
                    entity_list.append(entity)
                    
                    document = entity["document"]
                    try:
                        if entity["geo_entity"] == True:
                            se_list.append(entity)
                    except Exception as e:
                        return jsonify(entity), 500
                
                for link in links:
                    links_list.append(link)

                for event in events:
                    events_list.append(event)

                # Builds an article summary that is passed to GeoEvent that is used as the main object
                # in the operations dashboard. 
                article = {"title":title,
                            "article-link":article_link,
                            "published":published,
                            "updated":updated,
                            "copyright": cright,
                            "spatial-entities":len(se_list),
                            "entities":len(entity_list),
                            "events":len(events_list),
                            "links":len(links_list), 
                            "document":document}

            except Exception as e:
                return jsonify({"Error": str(e)}), 400

            try:
                # POSTs the various lists to GeoEvent. 
                # Stored as a seperate Try/Except loop to allow for more fine tuned debugging of this process
                post_to_geoevent(json.dumps(entity_list), app.config['NETOWL_GE_ENTITIES'])
                post_to_geoevent(json.dumps(se_list), app.config['NETOWL_GE_SE'])
                post_to_geoevent(json.dumps(links_list), app.config['NETOWL_GE_LINKS'])
                post_to_geoevent(json.dumps(events_list), app.config['NETOWL_GE_EVENTS'])
                post_to_geoevent(json.dumps(article), app.config['NETOWL_GE_ARTICLE'])
                return jsonify(article), 201
            except Exception as e:
                return jsonify({"Error":"GeoEvent problem...", "Actual error message": str(e)})