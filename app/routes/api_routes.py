from app import app, db

from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from random import randint
from copy import deepcopy
from arcgis.gis import GIS


from app.scripts import detect_faces
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
            return jsonify(entities) 

            entity_list = []
            links_list = []
            events_list = []
            se_list = []
            document = ''

            try:
                for entity in entities:
                    entity_list.append(entity)
                    document = entity.document
                    if entity.geo_entity == True:
                        se_list.append(vars(entity))
                        
                    if entity.ontology == "entity:address:mail":
                        pass
                
                for link in links:
                    links_list.append(link)

                for event in events:
                    events_list.append(event)

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
                post_to_geoevent(json.dumps(entity_list), app.config['NETOWL_GE_ALT_ENTITIES'])
                post_to_geoevent(json.dumps(se_list), app.config['NETOWL_GE_ALT_SE'])
                post_to_geoevent(json.dumps(links_list), app.config['NETOWL_GE_ALT_LINKS'])
                post_to_geoevent(json.dumps(events_list), app.config['NETOWL_GE_ALT_EVENTS'])
                post_to_geoevent(json.dumps(article), app.config['NETOWL_GE_ALT_ARTICLE'])
                return jsonify(article), 201
            except:
                post_to_geoevent(json.dumps(entity_list), app.config['NETOWL_GE_ENTITIES'])
                post_to_geoevent(json.dumps(se_list), app.config['NETOWL_GE_SE'])
                post_to_geoevent(json.dumps(links_list), app.config['NETOWL_GE_LINKS'])
                post_to_geoevent(json.dumps(events_list), app.config['NETOWL_GE_EVENTS'])
                post_to_geoevent(json.dumps(article), app.config['NETOWL_GE_ARTICLE'])
                return jsonify(article), 201
            else:
                return jsonify({"Error":"GeoEvent Sucks hard..."})
                



@app.route('/api/twitter', methods=['POST'])
def twitter():
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "Twitter"
    if request.method == 'POST':
        try:        
            content = request.get_json()
            if content['language'] is not 'en':
                translate_key = app.config['TRANSLATOR_TEXT_KEY']
                base_url = 'https://api.cognitive.microsofttranslator.com'
                detect_path = '/detect?api-version=3.0'
                detect_constructed_url = base_url + detect_path

                headers = {
                    'Ocp-Apim-Subscription-Key': translate_key,
                    'Content-type': 'application/json',
                    'X-ClientTraceId': str(uuid.uuid4())
                }

                body = [{
                    'text': content['text']
                }]

                detect_request = requests.post(detect_constructed_url, headers=headers, json=body)
                detect_response = detect_request.json()
                if detect_response[0]["isTranslationSupported"] == True:
                    language = detect_response[0]["language"]
                    score = detect_response[0]["score"]
                    content['language'] = language
                    content['language-confidence'] = score

                    trans_path = '/translate?api-version=3.0'
                    params = '&to=en'
                    trans_constructed_url = base_url + trans_path + params

                    trans_request = requests.post(trans_constructed_url, headers=headers, json=body)
                    trans_response = trans_request.json()

                    translated_text = trans_response[0]["translations"][0]["text"]
                    content['original-text'] = content['text']
                    content['text'] = translated_text

                    body = [{
                        'text': translated_text
                    }]

            text_subscription_key = app.config['TEXT_API_KEY']
            text_analytics_base_url = "https://eastus.api.cognitive.microsoft.com/text/analytics/v2.1"
            sentiment_url = text_analytics_base_url + "/sentiment"
            entities_url = text_analytics_base_url + "/entities"

            text_headers   = {"Ocp-Apim-Subscription-Key": text_subscription_key}

            documents = {"documents" : [
            {"id": "1", "language": "en", "text": content['text']}
            ]}

            sentiment_response  = requests.post(sentiment_url, headers=text_headers, json=documents)
            sentiments = sentiment_response.json()

            entities_response  = requests.post(entities_url, headers=text_headers, json=documents)
            entities = entities_response.json()

            sentiment_score = sentiments["documents"][0]["score"]
            content["sentiment"] = sentiment_score

            elastic_content = deepcopy(content)
            elastic_content['entities'] = entities["documents"][0]['entities']

            es = app.elasticsearch.index(index='twitter',doc_type='document', body=elastic_content)

            content['elastic_id'] = es['_id']

            for e in entities["documents"][0]['entities']:
                e['elastic-id'] = es['_id']
                try:e["entityTypeScore"] = e['matches'][0]["entityTypeScore"]
                except:pass
                try: e["length"] = e['matches'][0]["length"]
                except:pass
                try: e["offset"] = e['matches'][0]["offset"]
                except:pass
                try: e["text"] = e['matches'][0]["text"]
                except:pass
                try: e["wikipediaScore"] = e['matches'][0]["wikipediaScore"]
                except:pass
                
                del e['matches']

                try:
                    if e['type'] == 'Location':
                            location = geocode_address(e['name'])  # returns x,y
                            e['geo_entity'] = True
                            e['lat'] = location['y']
                            e['long'] = location['x']
                            e['elastic-id'] = es['_id']
                            #post_to_geoevent(json.dumps(e), app.config['TWEETS_SE_URL'])

                    #post_to_geoevent(json.dumps(e), app.config['TWEETS_ENTITIES_URL'])
                    
                except:
                    pass

            try:

                gis_username = app.config['GIS_USERNAME']
                target_password = app.config['GIS_PASSWORD']
                gis_url = app.config['GIS_URL']

                target_portal = GIS(gis_url, gis_username, target_password)

                tweets_fs = target_portal.content.get('e656ae3cfbe54a5d9fe06ac6c6e9a2c3')
                tweets_flayer = tweets_fs.layers[0]
                tweets_fset = tweets_flayer.query()
                all_features = tweets_fset.features
                _tweet_original_feature = [f for f in all_features if f.attributes['handle'] == 'DerSPIEGEL'][0]
                features_to_be_added = []
                template = deepcopy(_tweet_original_feature)

                template.attributes['name'] = content['name']
                template.attributes['elastic_id'] = content['elastic_id']
                template.attributes['tweet-id'] = content['tweet-id']
                template.attributes['url'] = content['url']
                template.attributes['language-confidence'] = content['language-confidence']
                template.attributes['sentiment'] = content['sentiment']
                template.attributes['created-at'] = datetime.datetime.now()
                template.attributes['text'] = content['text']
                template.attributes['user-location'] = content['user-location']
                template.attributes['language'] = content['language']
                template.attributes['original-text'] = content['original-text']
                template.attributes['handle'] = content['handle']

                features_to_be_added.append(template)
                tweets_flayer.edit_features(adds=features_to_be_added)
                return str(features_to_be_added)
            except Exception as e:
                return jsonify({"Error": "Failed to post to GeoEvent Server", "message":str(e)}), 501
                
            return jsonify(content), 201
        except Exception as e:
            return jsonify({"Error": str(e)}), 400