import os
import urllib3
import json
import requests

from datetime import datetime
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.scripts import detect_faces
#from app.scripts import consolidate_rasters
from app.forms.forms import DetectFaces
from app.models.models import User, Post, NetOwl_Entity

from config import Config

urllib3.disable_warnings()

def post_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    requests.post((geoevent_url), headers=headers, data=json_data, verify=False)

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

        print(app.config['IMAGE_BASE_URL'] + f.filename)
        image_url = app.config['IMAGE_BASE_URL'] + f.filename
        # image_url = 'http://wdc-integration.eastus.cloudapp.azure.com/static/images/image.jpg'
        try:
            faces = detect_faces.main(image_url, lat, lon)
            post_to_geoevent(json.dumps(faces), app.config['FACES_GE_URL'])
            return jsonify(faces)
        except Exception as e:
            return str(e)
    return render_template('detect_faces.html', form=form)
