from app import app, db

import arcgis
import csv
import io
import json
import os
import PIL
import requests
import datetime
import time

import cognitive_face as CF
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from arcgis import geometry
from arcgis.gis import GIS
from copy import deepcopy
from IPython.display import HTML
from io import BytesIO
from matplotlib import patches
from PIL import Image

from azure_cognitive import ComputerVision

subscription_key = '53242be6635c420c807d15a44a7015cf'
assert subscription_key

cv_subscription = 'b5c56de0406947f5a5ef90c6f32e0665'
cv_region = 'eastus'

# Sets the Base URL that will be passed to the 
base_url = 'https://eastus.api.cognitive.microsoft.com/face/v1.0/'

# Passes the subscription key and the Base URL to the Cognitive Faces SDK
CF.Key.set(subscription_key)
CF.BaseUrl.set(base_url)

# Sets the base URL for the Detect Faces tool from
face_api_url = base_url + 'detect'

# Headers and Parameters for the Faces API Requests Call
mcs_headers = { 'Ocp-Apim-Subscription-Key': subscription_key }
    
mcs_params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
}

geoevent_headers = {
    'Content-Type': 'application/json',
}

# Location of source images
img_Locs = r'C:\xampp1\htdocs\camera\streamMobile\uploads'

# Output location for marked up images
markUp = r'C:\xampp1\htdocs\camera\Image_MarkUp'

# Base web end point for the hosted images
baseWeb = 'http://40.76.87.212/camera/'

# Hosted location for the marked up images
web_markUp = baseWeb + 'Image_MarkUp/'

# Hosted location for the source images
web_Source = baseWeb + 'streamMobile/uploads/'

# Location of output JSON Files
responseFP = r'C:\Users\dif_user\Documents\Cognitive-Facial-Recognition\JSON'

# Location of GeoEvent JSON REST endpoint
geoevent_json_path = r'C:\Data\faces'
geoevent_url = r'https://esri-ge.mstacticalcloud.net/geoevent/rest/receiver/rest-faces-in'


def process_image(image_file):
    img_path = os.path.join(img_Locs, image_file)
    im = Image.open(img_path)
    width, height = im.size
    if img.split("_")[0] == 'EsriUC':
        pass
    else:
        if width > height:
            im1 = im.rotate(-90)
            im1.save(img_path)

    image_url = web_Source + "/" + image_file

    # Allows the computer to read the image and process it
    image_file = BytesIO(requests.get(image_url).content)
    image = Image.open(image_file)
        
    return image, image_url

def get_spatial_info(csv_file_path):
    with open(csv_file_path) as csvfile:
        readCSV = csv.reader(csvfile)
        for row in readCSV:
            sRow = row[0].split('|')
            #print(sRow)
            feature_name = sRow[0]
            latitude = sRow[1]
            longitude = sRow[2]
            feature_time = sRow[3]
            group = 1
            #print("get_Spatial_info:Group:" + group)

    return feature_name, latitude, longitude, feature_time, group

def is_weapon(image, subscription_key, region_code):
    weapon_tags = ['weapon', 'gun', 'knife', 'axe']
    vision = ComputerVision(subscription_key, region_code)
    resp = vision.submit(image)
    #return resp
    return not set(weapon_tags).isdisjoint(resp['description']['tags'])

def update_json(input_json_file, image_name, image_url, latitude, longitude, face_count, has_weapon):
    input_json_file['image_name'] = image_name
    input_json_file['image_url'] = image_url
    input_json_file['lat'] =latitude
    input_json_file['long'] = longitude
    input_json_file['number_faces'] = face_count
    input_json_file['has_weapon'] = has_weapon

def update_fc(gis_connection, layer, latitude, longitude, image_name, image_url, face_count):
    layer_fset = layer.query(return_geometry=True)
    all_features = layer_fset.features
    original_features = all_features[0]
    template_feature = deepcopy(original_features)
    features_for_update = []
    new_feature = deepcopy(template_feature)
    
    input_geometry = {'y':latitude,
                      'x':longitude}
    
    output_geometry = geometry.project(geometries = [input_geometry],
                                                    in_sr=4326,
                                                    out_sr=4326,
                                                    gis=gis)

    new_feature.geometry = output_geometry[0]
    
    new_feature.attributes['image_name'] = image_name
    new_feature.attributes['image_url'] = image_url
    new_feature.attributes['number_faces'] = face_count
    new_feature.attributes['lat'] = latitude
    new_feature.attributes['long'] = longitude
    new_feature.attributes['event_time'] = datetime.datetime.now()
    
    features_for_update.append(new_feature)
    layer.edit_features(adds = features_for_update)

def post_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    response = requests.post((geoevent_url), headers=headers, data=json_data)

def main(img, ):
    # Helper lists
    faceList = []
    allFaces = []
    done_urls = []
    faceID = []
    da_Faces = []
    facePics = {}
    addedRows = []
    addedDaFaces = []

    if img.endswith('.jpg'):
            
            if True:

                image, image_url = process_image(img)

                image_has_weapon = is_weapon(image_url, cv_subscription, cv_region)

                csv_file = os.path.splitext(img)[0] + ".csv"
                csv_path = os.path.join(img_Locs, csv_file)
                if os.path.exists(csv_path):
                    fName, lat, long, fTime, fGroup = get_spatial_info(csv_path)

                # Posts the image to the Microsoft Cognitive Services API, returns result
                mcs_response = requests.post(face_api_url, params=mcs_params, headers=mcs_headers, json={"url": image_url})

                # Return response from the Microsoft Cognitive Services API coded as JSON
                faces = mcs_response.json()

                #print(faces)
                if len(faces) > 0:
                    if 'error' in faces[0].keys():
                        print(faces['error']['code'])
                        print(faces['error']['message'])
                        break

                    else:

                        out_fig = os.path.splitext(img)[0] + 'MarkUp.jpg'
                        image_url = web_markUp + out_fig

                        plt.figure(figsize=(8,8))
                        ax = plt.imshow(image, alpha=0.6)
                        plt.axis('off')

                        face_count = 0
                        for face in faces:
                            face_count +=1
                            fr = face["faceRectangle"]
                            fa = face["faceAttributes"]
                            origin = (fr["left"], fr["top"])
                            pat = patches.Rectangle(origin, fr["width"], fr["height"], fill=False, linewidth=2, color='b')
                            ax.axes.add_patch(pat)

                            plt.text(origin[0], origin[1], "%s, %d"%(fa["gender"].capitalize(), fa["age"]),                                     fontsize=20, weight="bold", va="bottom")

                        outFig = os.path.splitext(img)[0] + 'MarkUp.jpg'
                        figName = os.path.join(markUp, outFig)
                        plt.savefig(figName, orientation='portrait', bbox_inches="tight", )

                        geoevent_json = {}                  

                        update_json(geoevent_json, img, image_url, lat, long, face_count, image_has_weapon)

                        #update_fc(gis, cameras_lyr, lat, long, img, image_url, face_count)

                        plt.gcf().clear()

                        responseFile =  os.path.join(responseFP,img + ".json")

                        with open(responseFile, 'w') as outfile:
                            json.dump(faces, outfile)

                        geoevent_json_file =os.path.join(geoevent_json_path, img + ".json")

                        with open(geoevent_json_file, 'w') as ge_file:
                            json.dump(geoevent_json, ge_file)
                        
                        post_to_geoevent(json.dumps(geoevent_json), geoevent_url)

                        print(geoevent_json)
                        
                else:
                    print("No faces detected...")