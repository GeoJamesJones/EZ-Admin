import os
import pandas as pd
import requests
import logging

log = logging.getLogger()

from arcgis.gis import GIS

gis_username = os.environ.get('gis_username')
target_password = os.environ.get('gis_password')
gis_url = os.environ.get('gis_url')

target_portal = GIS(gis_url, gis_username, target_password)

portal_mgr = target_portal.admin

fed_servers = portal_mgr.federation.servers['servers']

for fed_server in fed_servers:
    print(f"{fed_server['adminUrl']:<50}{fed_server['serverRole']:20}{fed_server['serverFunction']}")

val_all = portal_mgr.federation.validate_all()
print(val_all['status'])
for val in val_all['serversStatus']:
    print(val['status'])
    print(val['serverId'])
    print(val['messages'])