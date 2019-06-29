import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NETOWL_INT_FOLDER = os.getcwd() + '/static/temp'
    UPLOAD_FOLDER = os.getcwd() + '/static/uploads'
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
    # SQLALCHEMY_DATABASE_URI =  'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    
