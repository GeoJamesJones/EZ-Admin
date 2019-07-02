from app import app, db

from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.utils import secure_filename

from app.scripts import detect_faces

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

@app.route('/api/v1.0/detect-faces', methods=['POST', 'GET'])
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
