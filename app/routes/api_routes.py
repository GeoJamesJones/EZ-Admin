from app import app, db

from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from googlesearch import search
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from arcgis.gis import GIS
from arcgis.mapping import WebMap

from app.scripts import unzip
from app.scripts import move_files
#from app.scripts import consolidate_elevation
from app.forms.forms import UploadShapes
from app.models.models import Post

import requests
import os
import json
import string
import urllib3
import sys

ALLOWED_EXTENSIONS = set(['zip'])

gis_username = os.environ.get('gis_username')
target_password = os.environ.get('gis_password')
gis_url = os.environ.get('gis_url')

target_portal = GIS(gis_url, gis_username, target_password)

jobs = {}

@app.route('/api/v1.0/job-info', methods=['GET'])
def job_info():
    return jsonify(jobs)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/v1.0/upload-shapes', methods=['POST', 'GET'])
def upload_shape():
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "Job Recieved"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            copied_shapes = 'Please submit files as a ZIP file.'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            copied_shapes = 'error'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            final_folder = app.config['SHAPE_FINAL_FOLDER']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename.endswith(".zip"):
                dirname = unzip.unzip_file(filename)
                copied_shapes = move_files.copy_directory(dirname,final_folder, "Upload Shapefiles")

        else:
            copied_shapes = 'error'

    elif request.method == 'GET':
        copied_shapes = 'unknown redirect'

    jobs[job_number] = copied_shapes
    return jsonify(copied_shapes)

@app.route('/api/v1.0/upload-elevation', methods=['POST'])
def upload_elev():
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "Job Recieved"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename.endswith(".zip"):
                final_folder = app.config['ELEV_FINAL_FOLDER']
                dirname = unzip.unzip_file(filename)
                copied_elev = move_files.copy_directory(dirname,final_folder, "Upload Elevation")
                #copied_elev = consolidate_elevation.consolidate_elevation(dirname, )


    jobs[job_number] = copied_elev
    return jsonify(copied_elev)

@app.route('/api/v1.0/upload-raster', methods=['POST'])
def upload_raster():
    job_number = int(len(jobs) + 1)
    jobs[job_number] = "Job Recieved"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename.endswith(".zip"):
                final_folder = '/Users/jame9353/Documents/temp_data/bucketize/raster'
                dirname = unzip.unzip_file(filename)
                copied_raster = move_files.copy_directory(dirname,final_folder, "Upload Raster")

        jobs[job_number] = copied_raster
        return jsonify(copied_raster)

@app.route('/api/v1.0/add-user', methods=['POST'])
def add_user():
    # See if the user has firstName and lastName properties

    try:
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        organization = request.form['organization']

        # create user
        target_user = target_portal.users.create(username, password, first_name, 
                                                 last_name, email, role)

        if organization == 'EUCOM':
            group = target_portal.groups.search("DC Crime Analysis")[0]
            group.add_users(target_user.username)

        # update user properties
        return "{} successfully added!".format(username)
    
    except Exception as e:
        return str(e)

@app.route('/api/v1.0/get-users', methods=['GET'])
def get_users():
    try:
        users = {}
        source_users = target_portal.users.search('!esri_ & !admin')
        for user in source_users:
            users[user.username] = user.role

        return jsonify(users)
        
    except Exception as e:
        return str(e)

@app.route('/api/v1.0/get-groups', methods=['GET'])
def get_groups():
    try:
        groups = {}
        source_groups = target_portal.groups.search("!owner:esri_* & !Basemaps")
        for group in source_groups:
            groups[group.title] = group.owner

        return jsonify(groups)
        
    except Exception as e:
        return str(e)

@app.route('/api/v1.0/remove-user', methods=['DELETE'])
def remove_user():
    try:
        target_user = target_portal.users.get(request.form['username'])
        if target_user is not None:
            print('Deleting user: ' + target_user.fullName)
            target_user.reassign_to(request.form['reassign-data-to'])
            target_user.delete()
        return "Successfully removed {}".format(request.form['username'])
    except Exception as e:
        return str(e)
        #return 'User {} does not exist in Target Portal'.format(request.form['username'])

ALLOWED_EXTENSIONS = set(['doc', 'docx', 'txt', 'htm', 'html', 'pdf'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/v1.0/netowl-doc', methods=['POST'])
def netowl_doc():
    try:
        job_number = int(len(jobs) + 1)
        jobs[job_number] = "Job Recieved"
        if request.method == 'POST':

            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                final_folder = '/Users/jame9353/Documents/temp_data/bucketize/json'
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                process_netowl.netowl_curl(uploaded_file, final_folder, ".json", netowl_key)
                with open(os.path.join(final_folder, filename +'.json'), 'rb') as json_file:
                    data = json.load(json_file)

                entity_list = process_netowl.process_netowl_json(file.filename, data)

                spatial_entities = []
                nonspatial_entities = []

                for entity in entity_list:
                    if entity.geo_entity == True:
                        spatial_entities.append(vars(entity))
                    else:
                        nonspatial_entities.append(vars(entity))

                return jsonify(spatial_entities)

                os.remove(uploaded_file)
                os.remove(os.path.join(final_folder, filename +'.json'))
                
    except Exception as e:
        return str(e)

@app.route('/api/v1.0/google-netowl', methods=['POST'])
def google_netowl():
    try:
        for j in search(request.form['query'], tld="com", num=int(request.form['results']), stop=10, pause=2):
            r = requests.get(j)
            soup = BeautifulSoup(r.content, features="html.parser")

            soup_list = [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
            visible_text = soup.getText()

            final_folder = '/Users/jame9353/Documents/temp_data/bucketize/json'
            filename = request.form['query'].replace(" ", "_") + str(randint(1,1000))
            text_file_path = os.path.join(final_folder, filename + '.txt')
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                print_text = process_netowl.cleanup_text(visible_text)
                text_file.write(print_text)
                text_file.close()

            process_netowl.netowl_curl(text_file_path, final_folder, ".json", netowl_key)

            with open(text_file_path + ".json", 'rb') as json_file:
                data = json.load(json_file)

                entity_list = process_netowl.process_netowl_json(filename, data)

                spatial_entities = []
                nonspatial_entities = []

                for entity in entity_list:
                    if entity.geo_entity == True:
                        spatial_entities.append(vars(entity))
                    else:
                        nonspatial_entities.append(vars(entity))

                return jsonify(spatial_entities)

            os.remove(text_file_path)
            os.remove(text_file_path + ".json")

    except Exception as e:
        return str(e) 
