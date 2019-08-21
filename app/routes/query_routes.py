import os
import urllib3
import json
import shutil
import subprocess

from datetime import datetime
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from arcgis.gis import GIS
from arcgis import features

from app import app, db
from app.scripts import process_netowl, bucketizebing, bucketizenews
#from app.scripts import consolidate_rasters
from app.forms.forms import QueryWeb, QueryNews, GetBrokenLinks
from app.models.models import User, Post, NetOwl_Entity

from config import Config

urllib3.disable_warnings()

@app.route('/query/web', methods=['POST', 'GET'])
@login_required
def form_query_web():
    form = QueryWeb()
    title = 'PAI Query'
    if form.validate_on_submit():
        query = form.query.data
        category = form.category.data
        post_body = "Query Web: " + query
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        bucketizebing.main(query, category)
        flash("Success!")
        return render_template('simple_form.html', form=form, title=title)
    return render_template('simple_form.html', form=form, title=title)

@app.route('/query/news', methods=['POST', 'GET'])
@login_required
def form_query_news():
    form = QueryNews()
    title = 'News Feed Query'
    if form.validate_on_submit():
        query = form.query.data
        post_body = "Query News: " + query
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        bucketizenews.main(query, "News Query")
        flash("Success!")
        return render_template('simple_form.html', form=form, title=title)
    return render_template('simple_form.html', form=form, title=title)

@app.route('/embed/web', methods=['POST', 'GET'])
def embed_query_web():
    if request.method == 'POST':
        categories = {
            "warehouses":"Warehouses",
            "commercial_food_distribution_center":"Commercial Food Distribution Center",
            "farms_or_ranches":"Farms or Ranches",
            "food_distribution_center":"Food Distribution Center",
            "food_production_center":"Food Production Center",
            "food_retail":"Food Retail",
            "grain_storage":"Grain Storage",
            "generation_station":"Generation Station",
            "natural_gas_facility":"Natural Gas Facility",
            "petroleum_facility":"Petroleum Facility",
            "propane_facility":"Propane Facility",
            "government_site_infrastructure":"Government Site Infrastructure",
            "hospitals":"Hospitals",
            "television_stations":"Television Stations"
        }

        content = request.get_json()
        query = content['applyEdits'][0]['adds'][0]['attributes']['query_term']
        cat = content['applyEdits'][0]['adds'][0]['attributes']['category']
        category = categories[cat]
        print(query, category)
        bucketizebing.main(query, category)
        return "Success!", 201

@app.route('/embed/news', methods=['POST', 'GET'])
def embed_query_news():
    form = QueryNews()
    if form.validate_on_submit():
        query = form.query.data
        flash("Searching...")
        bucketizenews.main(query, "News Query")
        flash("Success!")
        return render_template('query_news_clean.html', form=form)
    return render_template('query_news_clean.html', form=form)

@app.route('/query/clean-fc', methods=['GET', 'POST'])
@login_required
def clean_pai_fc():
    form = GetBrokenLinks()
    if form.validate_on_submit():
        print("Connecting to GIS")
        gis = GIS("https://esrifederal.maps.arcgis.com", "james_jones_federal", "QWerty654321@!")
        
        print("Querying for content")
        item = gis.content.get("bea68adc5bc0491cb0091a4f9dbc3bf1")
        item_flayer = item.layers[0]
        item_fset = item_flayer.query()
        all_features = item_fset.features

        print("Deleting features")
        results = item_flayer.delete_features(where='1=1')

        print(results)        

    title = 'Delete Features from PAI Query Feature Layer'
    return render_template('simple_form.html', form=form, title=title)
    
    