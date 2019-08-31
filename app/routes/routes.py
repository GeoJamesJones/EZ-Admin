import os
import urllib3
import json
import shutil
import subprocess

from datetime import datetime
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template, g
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app.forms.forms import SearchForm

from app import app, db
from app.scripts import process_netowl, unzip, move_files, bucketizebing, bucketizenews
from app.forms.forms import LoginForm, RegistrationForm, SearchForm
from app.models.models import User, Post, NetOwl_Entity

from config import Config

# Creates a function that occurs before any process is ran that 
# updates the 'last_seen' variable inside of the user profile.
# Also adds the search form to the layout. 

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

# Login process
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('simple_form.html', title='Sign In', form=form)

# Logout process
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Allows a user to create an account
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('simple_form.html', title='Register', form=form)

# Homepage
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='WDC Integration API')

# User profile
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc())
    return render_template('user.html', user=user, posts=posts)

# Search function
@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    if g.search_form.validate():
        query = g.search_form.q.data
        res = app.elasticsearch.search(index="_all", body={"query": {"match": {"document": query}}})
        return jsonify(res['hits']['hits'])


