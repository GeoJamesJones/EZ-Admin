import logging
import os
from elasticsearch import Elasticsearch

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler

from config import Config

# Initializes the Flask application
# Pulls configuration from config.py located in the top level directory
# Uses SQLAlchemy to make a connection to a local (SQLite) database
# Makes connection to Elasticsearch Index
# Creates logs and log directory if they do not exist

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)

app.logger.info("Starting API...")

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None

app.config['BOOTSTRAP_SERVE_LOCAL'] = True

if not app.debug:
    if not os.path.exists('logs/'):
        os.mkdir('logs/')
    file_handler = RotatingFileHandler('logs/wdc_integration.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

# Imports the necessary modules from the Routes and Models folder.
# Import is at the end of this file due to the Routes and Models being reliant upon the Flask application
# that was created above.
# Prevents circular imports.
from app.models import models
from app.routes import routes, errors, query_routes, api_routes, admin_routes, upload_routes, analyze_routes