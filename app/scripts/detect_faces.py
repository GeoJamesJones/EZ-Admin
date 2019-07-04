from app import app, db

import arcgis
import csv
import io
import json
import os
import requests
import datetime
import time

from elasticsearch import Elasticsearch

from app.scripts.azure_cognitive import ComputerVision

def is_weapon(image, subscription_key, region_code):
    weapon_tags = ['weapon', 'gun', 'knife', 'axe']
    vision = ComputerVision(subscription_key, region_code)
    resp = vision.submit(image)
    #return resp
    return not set(weapon_tags).isdisjoint(resp['description']['tags'])

def update_json(input_json_file, image_url, latitude, longitude, face_count, male_count, female_count, children_count, has_weapon, event_time):
    input_json_file['image_url'] = image_url
    input_json_file['lat'] =latitude
    input_json_file['long'] = longitude
    input_json_file['number_faces'] = face_count
    input_json_file['male'] = male_count
    input_json_file['female'] = female_count
    input_json_file['children'] = children_count
    input_json_file['has_weapon'] = has_weapon
    input_json_file['event_time'] = event_time

def main(img, lat, lon):

    if img.endswith('.jpg'):

        # Sets the Base URL that will be passed to the 
        base_url = 'https://eastus.api.cognitive.microsoft.com/face/v1.0/'

        # Sets the subscription key for the Microsoft Cognitive Services Faces API
        faces_subscription_key = '53242be6635c420c807d15a44a7015cf'
        assert faces_subscription_key

        cv_subscription = 'b5c56de0406947f5a5ef90c6f32e0665'
        cv_region = 'eastus'

        # Sets the base URL for the Detect Faces tool from Microsoft Cognitive Services Face Detection API
        face_api_url = base_url + 'detect'

        # Headers and Parameters for the Microsoft Cognitive Services Face Detection API Requests Call
        mcs_headers = { 'Ocp-Apim-Subscription-Key': faces_subscription_key}
            
        mcs_params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
        }

        image_has_weapon = is_weapon(img, cv_subscription, cv_region)

        # Posts the image to the Microsoft Cognitive Services API, returns result
        mcs_response = requests.post(face_api_url, params=mcs_params, headers=mcs_headers, json={"url": img})

        # Return response from the Microsoft Cognitive Services API coded as JSON
        faces = mcs_response.json()

        #print(faces)
        if len(faces) > 0:
            if 'error' in faces[0].keys():
                print(faces['error']['code'])
                print(faces['error']['message'])

                return {faces['error']['code']:faces['error']['message']}

            else:
                face_count = 0
                male = 0
                female = 0
                children = 0

                for face in faces:
                    face_count +=1
                    if face["faceAttributes"]["gender"] == 'male':
                        male +=1
                    else:
                        female +=1

                    if face["faceAttributes"]["age"] <= 18:
                        children +=1

                event_time = time.time()
                geoevent_dict = {}                  

                update_json(geoevent_dict, img, float(lat), float(lon), face_count, int(male), int(female), int(children), image_has_weapon, event_time)
                
                return geoevent_dict, faces
                        
        else:
            print("No faces detected...")
            return {200:'No faces detected in image.'}
