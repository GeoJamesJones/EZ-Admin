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

app.config['BOOTSTRAP_SERVE_LOCAL'] = True

if not app.debug:
    if not os.path.exists('static/logs'):
        os.mkdir('static/logs')
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