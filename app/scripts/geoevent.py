import requests

# Helper function that will take incoming JSON Data and POST it to the 
# designated GeoEvent URL. 
# Disabled SSL Verification to allow for app to POST to secured (HTTPS) GeoEvent Servers
# that have exposed a REST endpoint on port 6143
def post_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    requests.post((geoevent_url), headers=headers, data=json_data, verify=False)

# Helper function that will take incoming JSON Data and PUT it to the 
# designated GeoEvent URL. 
# Disabled SSL Verification to allow for app to PUT to secured (HTTPS) GeoEvent Servers
# that have exposed a REST endpoint on port 6143. 
# In all honesty, I just use this as a generic PUT function...
def put_to_geoevent(json_data, geoevent_url):
    headers = {
        'Content-Type': 'application/json',
                }

    requests.put((geoevent_url), headers=headers, data=json_data, verify=False)