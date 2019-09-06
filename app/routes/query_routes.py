import os
import urllib3
import json

from datetime import datetime
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from arcgis.gis import GIS
from arcgis import features

from app import app, db
from app.scripts import bucketizebing, bucketizenews
from app.forms.forms import QueryWeb, QueryNews, GetBrokenLinks
from app.models.models import User, Post

from config import Config

# Disables warnings generated by non-HTTPS communication.
# Makes the resulting response much cleaner.
urllib3.disable_warnings()

# Handles requests from a Microsoft Flow Webhook watching a Survey123
# form that is associated with a specific operations dashboard.  
# Process leverages a script located in the ../Scripts folder call bucketizebing.py
# which leverages the Google Search and Bing Search APIs to allow a user to search the 
# open internet on topics associated with the categories listed below in the 'categories'
# variable. 
# Process does require access to the open internet to conduct the queries. 
# API Keys are stored in the Config file. 

@app.route('/embed/web', methods=['POST', 'GET'])
def embed_query_web():
    if request.method == 'POST':
        # turns HTTP POST request into a JSON object
        content = request.get_json()

        # Extracts the query and the category from the Survey123 request and turns them into
        # variables
        # Categories used to sort the results into usable feature class layers
        # Based on information obtained from Lynn Copeland
        query = content['applyEdits'][0]['adds'][0]['attributes']['query_term']
        cat = content['applyEdits'][0]['adds'][0]['attributes']['category']
        category = cat.title().replace("_", " ")
        print(query, category)

        # Runs the main script, which will in turn POST the results to GeoEvent Server.
        bucketizebing.main(query, category)
        return "Success!", 201

# Allows for the query of the Bing News and Google News APIs. 
# This process will be updated.
# The majority of the script is located in ../Scripts/bucketizenews.py
# Requries access to the open internet. 
# API Keys are stored in the Config file. 

@app.route('/embed/news', methods=['POST', 'GET'])
def embed_query_news():
    form = QueryNews()
    title = "Query News"
    if form.validate_on_submit():
        query = form.query.data
        flash("Searching...")
        bucketizenews.main(query, "News Query")
        flash("Success!")
        return "Success!"
    return render_template('simple_form.html', form=form, title=title)

# Cleans up excess features from the /embed/web process. 
# This process will be updated to match the same configuration options as 
# the /embed/web process (Survey123 feeding a Microsoft Flow webhook to initiate process)
# Currently, the process is hardcoded to one specific feature inside of the Esri Federal AGOL
# Organization.  

@app.route('/query/clean-fc', methods=['GET', 'POST'])
@login_required
def clean_pai_fc():
    form = GetBrokenLinks()
    if form.validate_on_submit():
        print("Connecting to GIS")
        # Makes a secure connection to ArcGIS Online
        gis = GIS("https://esrifederal.maps.arcgis.com", "james_jones_federal", os.environ['ESRI_FEDERAL_PASS'])
        
        # Queries for the specific layer
        print("Querying for content")
        item = gis.content.get("bea68adc5bc0491cb0091a4f9dbc3bf1")
        item_flayer = item.layers[0]
        item_fset = item_flayer.query()
        all_features = item_fset.features

        # Deletes all features within layer.
        print("Deleting features")
        results = item_flayer.delete_features(where='1=1')

        print(results)        

    title = 'Delete Features from PAI Query Feature Layer'
    return render_template('simple_form.html', form=form, title=title)
    
    