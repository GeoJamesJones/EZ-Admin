from app import app, db

from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from random import randint

from app.scripts import detect_faces
from app.models.models import User, Post, NetOwl_Entity
from app.scripts.process_netowl import cleanup_text, netowl_pipeline

import requests
import os
import json
import string
import urllib3
import sys

jobs = {}

def post_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    requests.post((geoevent_url), headers=headers, data=json_data, verify=False)

ALLOWED_EXTENSIONS = set(['doc', 'docx', 'txt', 'htm', 'html', 'pdf', 'jpg', 'png'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/v1.0/job-info', methods=['GET'])
def job_info():
    return jsonify(jobs)

@app.route('/api/detect-faces', methods=['POST', 'GET'])
def detect_face():
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "Detect Faces"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            copied_shapes = 'Please submit files as an image file.'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            copied_shapes = 'error'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            if filename.endswith(".jpg"):

                lat = request.form['Latitude']
                lon = request.form['Longitude']


                print(app.config['IMAGE_BASE_URL'] + file.filename)
                image_url = app.config['IMAGE_BASE_URL'] + file.filename
                #image_url = 'http://wdc-integration.eastus.cloudapp.azure.com/static/images/Wayne.jpg'
                try:
                    faces = detect_faces.main(image_url, lat, lon)
                    post_to_geoevent(json.dumps(faces), app.config['FACES_GE_URL'])
                    return jsonify(faces)
                    jobs[job_number] = faces
                except Exception as e:
                    jobs[job_number] = "Detect Faces: Failed"
                    return str(e)

    if request.method == 'GET':
        files = os.listdir(app.config['IMAGE_FOLDER'])
        return jsonify(files)

@app.route('/api/news-rss', methods=['POST'])
def news_rss():
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "News RSS"
    if request.method == 'POST':
        directory = app.config['NETOWL_INT_FOLDER']
        
        content = request.get_json()
        
        article_link = content["link"]
        published = content["published"]
        title = content["title"]
        updated = content["updated"]
        cright = content["copyright"]

        r = requests.get(article_link, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, features="html.parser")

        soup_list = [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        visible_text = soup.getText()

        filename = title.replace(" ", "_")
        text_file_path = os.path.join(directory, filename + '.txt')
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            print_text = cleanup_text(visible_text)
            text_file.write(print_text)
            text_file.close()


        if os.path.exists(text_file_path):
            print(text_file_path)
        
            entities, links, events = netowl_pipeline(text_file_path)

            entity_list = []
            links_list = []
            events_list = []
            se_list = []
            document = ''

            if type(entities).__name__ == 'list':

                for entity in entities:
                    entity_list.append(vars(entity))
                    document = entity.document
                    if entity.geo_entity == True:
                        se_list.append(vars(entity))
                        
                    if entity.ontology == "entity:address:mail":
                        pass
                
                for link in links:
                    links_list.append(vars(link))

                for event in events:
                    events_list.append(vars(event))

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

                post_to_geoevent(json.dumps(entity_list), app.config['NETOWL_GE_ENTITIES'])
                post_to_geoevent(json.dumps(se_list), app.config['NETOWL_GE_SE'])
                post_to_geoevent(json.dumps(links_list), app.config['NETOWL_GE_LINKS'])
                post_to_geoevent(json.dumps(events_list), app.config['NETOWL_GE_EVENTS'])
                post_to_geoevent(json.dumps(article), app.config['NETOWL_GE_ARTICLE'])
        
        return jsonify(article), 201
