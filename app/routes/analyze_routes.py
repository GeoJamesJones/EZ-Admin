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
from app.scripts import detect_faces
from app.scripts.geoevent import post_to_geoevent, put_to_geoevent
from app.forms.forms import DetectFaces
from app.models.models import User, Post
from app.search import add_to_index

from config import Config

# Disables warnings generated by non-HTTPS communication.
# Makes the resulting response much cleaner.
urllib3.disable_warnings()

# Receives an image from an HTTPS POST operation and detects faces
# using the Microsoft Cognitive Services Detect Faces API
# Bulk of code is stored in detect_faces.py located in the ../Scripts folder

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
        try:

            # Main function that will actually process the image and return the results as two lists of dictionary objects.
            # Faces object represents the formalized summary of total number of faces that were detected and if any weapons were
            # observed.
            # Report object represents the raw response from the Microsoft Cognitive Services Detect Faces API.
            # Both objects will be indexed via Elasticsearch, however the individual Report objects will be stored seperately.
            faces, report = detect_faces.main(image_url, lat, lon)
        except Exception as e:
            print(faces)
            return str(e), 400
        try:

            # Stores the formalized Faces object report in an Elasticsearch index
            es = app.elasticsearch.index(index='detect-faces',doc_type='detect-faces', body=json.dumps(faces))
            faces['id'] = es['_id']
            for r in report:

                # Stores the individual reports generated from the Detect Faces API as seperarate objects.
                app.elasticsearch.index(index='face-reports',doc_type='face-report', body=json.dumps(r))
            print(str(es['_id']))
        except Exception as e:
            print("es error")
            return str(e), 400
        try:

            # Posts the formal Faces object summary to the Configuration specified GeoEvent server.
            post_to_geoevent(json.dumps(faces), app.config['FACES_GE_URL'])
        except Exception as e:
            print("post to geoevent error")
            return str(e), 400

        return jsonify(faces)

    return render_template('detect-faces-geo.html', form=form)