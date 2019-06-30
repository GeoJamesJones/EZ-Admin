import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI =  'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NETOWL_INT_FOLDER = os.getcwd() + '/static/temp'
    UPLOAD_FOLDER = os.getcwd() + '/static/uploads'
    IMAGE_FOLDER = os.getcwd() + '/static/images'
    MARKUP_FOLDER = os.getcwd() + '/static/markup'
    NETOWL_FINAL_FOLDER = os.getcwd() + '/static/temp'
    GIS_PASSWORD = os.environ.get('gis_password')
    GEOEVENT_URL = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/ca-query-in'
    GIS_URL = 'https://wdcdefense.esri.com/portal'
    GIS_USERNAME = "james_jones"
    GIS_PASSWORD = "QWerty654321@!"
    NETOWL_KEY='netowl ff5e6185-5d63-459b-9765-4ebb905affc8'
    POSTGRES_URL="wdcdefense.esri.com:5432"
    POSTGRES_USER="postgres"
    POSTGRES_PW="H0neyBadger5"
    POSTGRES_DB="jones"
    ACS_FACE_API_KEY="53242be6635c420c807d15a44a7015cf"
    ACS_CV_API_KEY="b5c56de0406947f5a5ef90c6f32e0665"
    IMAGE_BASE_URL='http://wdc-integration.eastus.cloudapp.azure.com/static/images/'
    MARKUP_BASE_URL='http://wdc-integration.eastus.cloudapp.azure.com/static/markup/'
    FACES_GE_URL = 'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/api-faces-in'
