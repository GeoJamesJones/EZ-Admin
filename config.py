import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # System Configuration Options
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI =  'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = r'C:\Users\arcgis\Documents\GitHub\wdc-integration\static\temp'
    IMAGE_FOLDER =  r'C:\xampp\htdocs\camera\streamMobile\uploads'
    MARKUP_FOLDER = r'C:\xampp\htdocs\camera\Image_MarkUp'
    ELASTICSEARCH_URL = 'http://localhost:9200'
    POSTS_PER_PAGE = 25

    # CMB Upload Specific Information
    SHAPE_FINAL_FOLDER = r'C:\services\data\shapes'
    ELEV1_FINAL_FOLDER = r'C:\services\data\elevation\DTED_1'
    ELEV2_FINAL_FOLDER = r'C:\services\data\elevation\DTED_2'
    ELEV_FINAL_FOLDER = r'C:\services\data\elevation'
    CADRG_FINAL_FOLDER = r'C:\services\data\cadrg'
    CIB_FINAL_FOLDER = r'C:\services\data\cib'
    IMAGERY_FINAL_FOLDER = r'C:\services\data\imagery'
    ELEVATION1_MOSAIC = r"C:\services\mosaics\geodata.gdb\DTED1"
    ELEVATION2_MOSAIC = r'C:\services\mosaics\geodata.gdb\DTED2'
    CADRG_MOSAIC = r'C:\services\mosaics\geodata.gdb\CADRG'
    CIB_MOSAIC = r'C:\services\mosaics\geodata.gdb\CIB'
    IMAGERY_MOSAIC = r'C:\services\mosaics\geodata.gdb\IMAGERY'

    # Microsoft Cognitive Services Affiliated Configuration Options
    ACS_FACE_API_KEY=os.environ['ACS_FACE_API_KEY']
    ACS_CV_API_KEY=os.environ['ACS_CV_API_KEY']
    TRANSLATOR_TEXT_KEY = os.environ['TRANSLATOR_TEXT_KEY']
    TEXT_API_KEY = os.environ['TEXT_API_KEY']
    CONTENT_MODERATION_KEY = os.environ['CONTENT_MODERATION_KEY']
    IMAGE_BASE_URL='http://dif.eastus.cloudapp.azure.com/camera/streamMobile/uploads/'
    MARKUP_BASE_URL='http://dif.eastus.cloudapp.azure.com/camera/Image_MarkUp/'
    FACES_GE_URL = 'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/api-faces-in'
    TWEETS_GE_URL = 'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/azure-tweets-in'
    TWEETS_GE_ALT_URL = 'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/azure-tweets-in'
    TWEETS_ENTITIES_URL = 'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/azure-twitter-entities-in'
    TWEETS_SE_URL = 'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/azure-twitter-se-in'
    
    
    # NetOwl Affiliated Configuration Options
    NETOWL_KEY=os.environ['NETOWL_KEY']
    NETOWL_FINAL_FOLDER = os.getcwd() + r'\static\temp'
    NETOWL_INT_FOLDER = os.getcwd() + r'\static\temp'
    NETOWL_GE_SE = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-features-in'
    NETOWL_GE_LINKS = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-links-in'
    NETOWL_GE_EVENTS = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-events-in'
    NETOWL_GE_ENTITIES = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-entities-in'
    NETOWL_GE_ARTICLE = r'https://wdcrealtime.esri.com:6143/geoevent/rest/receiver/netowl-article-in'
    GEOEVENT_URL = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/ca-query-in'
    #INVESTIGATION_REPORTS = '/Users/jame9353/Documents/GitHub/SampleData/incident reports'
    INVESTIGATION_REPORTS = '/home/dif_user/SampleData/incident reports'
    EARLY_BIRD = '/home/dif_user/SampleData/Early_Bird_Docs'
    NETOWL_GE_ALT_ENTITIES = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/netowl-entities-in'
    NETOWL_GE_ALT_EVENTS = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/netowl-events-in'
    NETOWL_GE_ALT_SE = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/netowl-features-in'
    NETOWL_GE_ALT_LINKS = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/netowl-links-in'
    NETOWL_GE_ALT_ARTICLES = r'https://wdcrealtimeevents.esri.com:6143/geoevent/rest/receiver/netowl-ge-articles-in'