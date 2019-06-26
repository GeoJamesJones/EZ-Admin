import logging
import os
import requests
import datetime

#from app import app, db
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from datetime import timedelta

log = logging.getLogger()

try:
    gis_username = os.environ.get('gis_username')
    target_password = os.environ.get('gis_password')
    gis_url = os.environ.get('gis_url')
except:
    pass

target_portal = GIS(gis_url, gis_username, target_password)

CHECK_ALL_ITEMS = True

def is_url_reachable(url):
    """Returns a bool representing if the URL is reachable"""
    try:
        response = requests.get(url)
        return response.ok
    except Exception as e:
        return False

def test_urls_in_webmap(webmap_item):
    """Takes in an `Item` class instance of a Web Map Item.
    Tests if all operational layers and basemap layers are
    reachable. Returns a tuple of (reachable, unreachable), 
    with each tuple entry being a list of layers/basemaps JSON.
    """
    reachable = []
    unreachable = []
    wm = WebMap(webmap_item)

    # Concatanate all operational layers and basemap layers to 1 list
    all_layers = list(wm.layers)
    if hasattr(wm.basemap, 'baseMapLayers'):
        all_layers += wm.basemap.baseMapLayers

    # Test all of the layers, return the results
    for layer in [layer for layer in all_layers \
                  if hasattr(layer, 'url')]:
        if is_url_reachable(layer.url):
            log.debug(f"    [✓] url {layer.url} reachable")
            reachable.append(layer)
        else:
            log.debug(f"    [X] url {layer.url} NOT reachable")
            unreachable.append(layer)
    return (reachable, unreachable)

def handle_unreachable(webmap_item, reachable, unreachable, gis):
    """Called whenever we encounter a WebMap with broken URLs. Will 
    assemble an appropriate message, and send it out to the previously
    configured emails.
    """
    # Get the owner of the item

    owner = gis.users.get(webmap_item.owner)
    
    try:
        broken_items = {
            "owner":owner,
            "owner_email":owner.email,
            "WebMap":webmap_item.id,
            "reachable_items":reachable,
            "unreachable-items":unreachable
        }
        return broken_items
    except Exception as e:
        return False

def get_items_to_check(gis):
    """Generator function that will yield Items depending on how you
    configured your notebook. Will either yield every item in an 
    organization, or will yield items in specific groups.
    """
    if CHECK_ALL_ITEMS:
        for user in gis.users.search('!esri_ & !admin'):
            for item in user.items(max_items=999999999):
                # For the user's root folder
                yield item
            for folder in user.folders:
                # For all the user's other folders
                for item in user.items(folder, max_items=999999999):
                    yield item
    else:
        for group_name in CHECK_THESE_GROUPS:
            group = gis.groups.search(f"title: {group_name}")[0]
            for item in group.content():
                yield item

def main():
    broken_items = []
    checked_items = []
    print("Process is now running, please wait...\n-----")
    for item in get_items_to_check(target_portal):
        i = {"title":item.title, "type":item.type, "owner":item.owner}
        checked_items.append(i)
        print(f"\rChecking item {item.id}", end="")
        if item.type == "Web Map":
            reachable, unreachable = test_urls_in_webmap(item)
            if unreachable:
                print(f"\nWebmap {item.id} unreachable. Notifying...")
                items = handle_unreachable(item, reachable, unreachable, target_portal)
                broken_items.append(items)
    print("-----\nNotebook completed running.")
    print("-----\nChecked the following items: {}".format(checked_items))

if __name__ == "__main__":
    main()