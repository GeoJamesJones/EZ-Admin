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
    ELASTICSEARCH_URL = 'http://localhost:9200'
    POSTS_PER_PAGE = 25
    
    # ArcGIS Enterprise or ArcGIS Online Configuration Options
    GIS_URL = 'https://wdcdefense.esri.com/portal'
    GIS_USERNAME = "james_jones"
    GIS_PASSWORD = "QWerty654321@!"

    # Microsoft Cognitive Services Faces API Affiliated Configuration Options
    ACS_FACE_API_KEY="53242be6635c420c807d15a44a7015cf"
    ACS_CV_API_KEY="b5c56de0406947f5a5ef90c6f32e0665"
    IMAGE_BASE_URL='http://wdc-integration.eastus.cloudapp.azure.com/static/images/'
    MARKUP_BASE_URL='http://wdc-integration.eastus.cloudapp.azure.com/static/markup/'
    FACES_GE_URL = 'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/api-faces-in'
    
    # NetOwl Affiliated Configuration Options
    NETOWL_KEY='netowl ff5e6185-5d63-459b-9765-4ebb905affc8'
    NETOWL_FINAL_FOLDER = os.getcwd() + '/static/temp'
    NETOWL_INT_FOLDER = os.getcwd() + '/static/temp'
    NETOWL_GE_SE = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-features-in'
    NETOWL_GE_LINKS = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-links-in'
    NETOWL_GE_EVENTS = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-events-in'
    NETOWL_GE_ENTITIES = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-entities-in'
    NETOWL_GE_ARTICLE = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-article-in'
    GEOEVENT_URL = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/ca-query-in'
    #INVESTIGATION_REPORTS = '/Users/jame9353/Documents/GitHub/SampleData/incident reports'
    INVESTIGATION_REPORTS = '/home/dif_user/SampleData/incident reports'
    EARLY_BIRD = '/home/dif_user/SampleData/Early_Bird_Docs'
    
