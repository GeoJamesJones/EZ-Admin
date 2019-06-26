import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    POSTGRES_URL = os.environ.get('POSTGRES_URL')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PW = os.environ.get('POSTGRES_PW')
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NETOWL_KEY = os.environ.get('NETOWL_KEY')
    ACS_FACE_API_KEY = os.environ.get('ACS_FACE_API_KEY')
    ACS_CV_API_KEY = os.environ.get('ACS_CV_API_KEY')
    NETOWL_INT_FOLDER = '/static/temp'
    UPLOAD_FOLDER = '/static/uploads'
    NETOWL_FINAL_FOLDER = '/static/temp'
    GIS_USERNAME = os.environ.get('gis_username')
    GIS_PASSWORD = os.environ.get('gis_password')
    GIS_URL = os.environ.get('gis_url')
    GEOEVENT_URL = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/ca-query-in'
    