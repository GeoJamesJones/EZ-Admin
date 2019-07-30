import os
import urllib3
import json
import requests
import time
from elasticsearch import Elasticsearch

from datetime import datetime
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template, session
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.scripts import detect_faces, process_netowl
#from app.scripts import consolidate_rasters
from app.forms.forms import DetectFaces,SimulateNetOwl
from app.models.models import User, Post, NetOwl_Entity
from app.search import add_to_index

from config import Config

urllib3.disable_warnings()

def post_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    requests.post((geoevent_url), headers=headers, data=json_data, verify=False)

def put_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    requests.put((geoevent_url), headers=headers, data=json_data, verify=False)

@app.route('/analyze/detect-faces', methods=['POST', 'GET'])
@login_required
def form_detect_faces():
    form = DetectFaces()
    if form.validate_on_submit():
        f = form.upload.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.config['IMAGE_FOLDER'], filename
        ))

        lat = form.lat.data
        lon = form.lon.data

        post_body = "Detect Faces: " + filename
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()

        image_url = app.config['IMAGE_BASE_URL'] + f.filename
        #image_url = 'http://wdc-integration.eastus.cloudapp.azure.com/static/images/image.jpg'
        #image_url = 'http://wdc-integration.eastus.cloudapp.azure.com/static/images/Diverse-group-of-children.jpg'
        try:
            faces, report = detect_faces.main(image_url, lat, lon)
        except Exception as e:
            print(faces)
            return str(e), 400
        try:
            es = app.elasticsearch.index(index='detect-faces',doc_type='detect-faces', body=json.dumps(faces))
            faces['id'] = es['_id']
            for r in report:
                app.elasticsearch.index(index='face-reports',doc_type='face-report', body=json.dumps(r))
            print(str(es['_id']))
        except Exception as e:
            print("es error")
            return str(e), 400
        try:
            post_to_geoevent(json.dumps(faces), app.config['FACES_GE_URL'])
        except Exception as e:
            print("post to geoevent error")
            return str(e), 400

        return jsonify(faces)

    return render_template('detect_faces.html', form=form)

@app.route('/analyze/simulate-netowl-feed', methods=['POST', 'GET'])
@login_required
def simulate_netowl_feed():
    form = SimulateNetOwl()
    if form.validate_on_submit():
        folder = os.listdir(form.datatype.data)
        print(folder)

        for item in folder:
            item_path = os.path.join(form.datatype.data, item)
            if os.path.exists(item_path):
                print(item_path)
            
                entities, links, events = process_netowl.netowl_pipeline(item_path)

                entity_list = []
                links_list = []
                events_list = []
                se_list = []

                if type(entities).__name__ == 'list':

                    for entity in entities:
<<<<<<< HEAD
                        entity_list.append(vars(entity))
                        if entity.geo_entity == True:
                            se_list.append(vars(entity))
=======
                        entity_list.append(entity)
                        if entity.geo_entity == True:
                            se_list.append(entity)
>>>>>>> parent of 4b1554c... Further refinements to app
                        if entity.ontology == "entity:address:mail":
                            pass
                    
                    for link in links:
<<<<<<< HEAD
                        links_list.append(vars(link))

                    for event in events:
                        events_list.append(vars(event))
=======
                        links_list.append(link)

                    for event in events:
                        events_list.append(event)
>>>>>>> parent of 4b1554c... Further refinements to app

                    post_to_geoevent(json.dumps(entity_list), app.config['NETOWL_GE_ENTITIES'])
                    post_to_geoevent(json.dumps(se_list), app.config['NETOWL_GE_SE'])
                    post_to_geoevent(json.dumps(links_list), app.config['NETOWL_GE_LINKS'])
                    post_to_geoevent(json.dumps(events_list), app.config['NETOWL_GE_EVENTS'])
        
        post_body = "Simulate NetOwl Pipeline: " + form.datatype.data
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        
        flash("Success!")
        data = {"entities":len(entity_list), "links":len(links_list), "events":len(events_list)}
        return render_template('simulate_netowl_results.html', data=data)

    return render_template('simulate_netowl.html', form=form)

@app.route('/embed/detect-face', methods=['POST', 'GET'])
def embed_detect_face():
    print("I AM THINKING OF DOING SOMETHING")
    form = DetectFaces()
    try:
        if form.validate_on_submit():
        #if form.validate():
            if len(form.errors) < 1:
                print("I AM DOING SOMETHING")
                f = form.upload.data
                filename = secure_filename(f.filename)
                print(filename)
                f.save(os.path.join(
                    app.config['IMAGE_FOLDER'], filename
                ))

                lat = form.lat.data
                lon = form.lon.data

                image_url = app.config['IMAGE_BASE_URL'] + f.filename
                try:
                    faces, report = detect_faces.main(image_url, lat, lon)
                except Exception as e:
                    print(faces)
                    return str(e), 400
                try:
                    es = app.elasticsearch.index(index='detect-faces',doc_type='detect-faces', body=json.dumps(faces))
                    faces['id'] = es['_id']
                    for r in report:
                        app.elasticsearch.index(index='face-reports',doc_type='face-report', body=json.dumps(r))
                    print(str(es['_id']))
                except Exception as e:
                    print("es error")
                    return str(e), 400
                try:
                    post_to_geoevent(json.dumps(faces), app.config['FACES_GE_URL'])
                except Exception as e:
                    print("post to geoevent error")
                    return str(e), 400

                return jsonify(faces)
            else:
                return jsonify(form.errors)
        #print(vars(form))
    except Exception as e:
        return jsonify({"Error": str(e)})

    return render_template('detect-faces-geo.html', form=form)
