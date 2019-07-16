import logging
import os
import rq
from elasticsearch import Elasticsearch

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler
from redis import Redis
from arcgis.gis import GIS

from config import Config

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

gis_username = app.config['GIS_USERNAME']
target_password = app.config['GIS_PASSWORD']
gis_url = app.config['GIS_URL']

app.target_portal = GIS(gis_url, gis_username, target_password)

tweets_fs = app.target_portal.content.get('e656ae3cfbe54a5d9fe06ac6c6e9a2c3')
app.tweets_flayer = tweets_fs.layers[0]
tweets_fset = app.tweets_flayer.query()
all_features = tweets_fset.features
app._tweet_original_feature = [f for f in all_features if f.attributes['handle'] == 'DerSPIEGEL'][0]

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
    app.redis = ""
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

from app.routes import routes, errors, query_routes, api_routes, admin_routes, upload_routes, analyze_routes
from app.models import models