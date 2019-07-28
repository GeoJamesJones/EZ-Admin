import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # System Configuration Options
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI =  'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getcwd() + '/static/uploads'
    IMAGE_FOLDER = os.getcwd() + '/static/images'
    MARKUP_FOLDER = os.getcwd() + '/static/markup'
    POSTS_PER_PAGE = 25
    CADRG_FINAL_FOLDER = '/Users/jame9353/Documents/temp_data/data/cadrg'
    CIB_FINAL_FOLDER = '/Users/jame9353/Documents/temp_data/data/cib'
    ELEV_FINAL_FOLDER = '/Users/jame9353/Documents/temp_data/data/elev'
    IMAGERY_FINAL_FOLDER = '/Users/jame9353/Documents/temp_data/data/imagery'
    
    # ArcGIS Enterprise or ArcGIS Online Configuration Options
    GIS_URL = 'https://wdcdefense.esri.com/portal'
    GIS_USERNAME = "james_jones"
    GIS_PASSWORD = "QWerty654321@!"