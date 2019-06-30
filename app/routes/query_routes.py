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

from app import app, db
from app.scripts import process_netowl, bucketizebing, bucketizenews
#from app.scripts import consolidate_rasters
from app.forms.forms import QueryWeb, QueryNews
from app.models.models import User, Post, NetOwl_Entity

from config import Config

urllib3.disable_warnings()

@app.route('/query/web', methods=['POST', 'GET'])
def form_query_web():
    form = QueryWeb()
    if form.validate_on_submit():
        query = form.query.data
        category = form.category.data
        flash("Searching...")
        bucketizebing.main(query, category)
        flash("Success!")
        return render_template('query_web_results.html')
    return render_template('query_web.html', form=form)

@app.route('/query/news', methods=['POST', 'GET'])
@login_required
def form_query_news():
    form = QueryNews()
    if form.validate_on_submit():
        query = form.query.data
        flash("Searching...")
        bucketizenews.main(query, "News Query")
        flash("Success!")
        return render_template('query_news_results.html')
    return render_template('query_news.html', form=form)   
