import csv
import os
import json
import time
import logging

import datetime as dt

from arcgis.gis import GIS

log = logging.getLogger()

gis_username = os.environ.get('gis_username')
target_password = os.environ.get('gis_password')
gis_url = os.environ.get('gis_url')

target_portal = GIS(gis_url, gis_username, target_password)

# The number of days a user is inactive for before...
NUM_INACTIVE_DAYS_TO_NOTIFY = 60 # we notify about their inactivity
NUM_INACTIVE_DAYS_TO_DISABLE = 90 # we delete their account

# Email these people a report about who this notebook notified/disabled
EMAIL_NOTEBOOK_REPORT = False
NOTEBOOK_REPORT_RECIPIENTS = []

USER_DISABLE_NOTIFY_PROTECTION = True

workspace = "/Users/jame9353/Documents/temp_data/bucketize/csv"

def datetime_of_last_login(user) -> dt.datetime:
    """Returns a datetime instance of when the user last logged in.
    
    The `user.lastLogin` property returns the milliseconds since the 
    epoch, whereas a standard timestamp is the seconds since the epoch. 
    Therefore, we must divide by 1000.
    """
    timestamp_of_last_login = int(user.lastLogin / 1000)
    last_login = dt.datetime.fromtimestamp(timestamp_of_last_login)
    return last_login

def num_days_since_last_login(user) -> int:
    """Returns the number of days since a user last logged in. 

    Subtracting the `last_login` and `now` datetime instances will
    yield a timedelta instance. This timedelta instance has a 
    `.days` property, which is what we want to return
    """
    last_login = datetime_of_last_login(user)
    now = dt.datetime.now()
    return (now - last_login).days

def datetime_of_account_deletion(user) -> dt.datetime:
    """Returns the datetime of when the account is planned to be deleted
    
    This is calculated based off of NUM_INACTIVE_DAYS_TO_DELETE variable,
    by adding a timedelta to a datetime (returns a datetime)
    """
    last_login = datetime_of_last_login(user)
    return last_login + timedelta(days=NUM_INACTIVE_DAYS_TO_DISABLE)

def write_csv(users_notify_range, users_disable_range):
    """Given two lists of users to notify/disable, write a CSV
    with 1 row per user, stating if in the notify/disable range """
    file_path = f'{workspace}/INACTIVE_USERS--{time.ctime()}.csv'
    with open(file_path, 'w') as file:
        writer = csv.DictWriter(file, ['user', 'in_notify_range',
                                       'in_disable_range'])
        writer.writeheader()
        for user in target_portal.users.search():
            writer.writerow({
                'user' : user.username,
                'in_notify_range' : bool(user in users_notify_range),
                'in_disable_range' : bool(user in users_disable_range)})
    return "CSV saved in {}".format(workspace)

def write_json(users_notify_range, users_disable_range):
    """Given two lists of users to notify/disable, write a JSON, 
       stating if in the notify/disable range """

    eval_users = []

    for user in target_portal.users.search():
        usr = {
            'user' : user.username,
            'in_notify_range' : bool(user in users_notify_range),
            'in_disable_range' : bool(user in users_disable_range)}
        eval_users.append(usr)

    return eval_users

def stringify_users(users):
    """Takes a list of users, and returns a string representation"""
    if users:
        return ", ".join(user.username for user in users)
    else:
        return "No Users"

def precondition_check():
    """Checks if running as admin by checking 'lastLogin' prop of User"""
    if 'lastLogin' not in target_portal.users.me:
        raise Exception("You don't have the proper permissions to "\
                        "run this notebook; you must be an admin.")

users_to_notify = []
users_to_disable = []
csv_item = None

def main():
    # Tell user we're running, initialize
    print("Notebook is now running, please wait...\n-----")
    global users_to_notify, users_to_disable, csv_item
    precondition_check()
    users_to_notify = []
    users_to_disable = []

    # Stage an in-memory list of all users to notify/delete
    for user in target_portal.users.search():
        num_days = num_days_since_last_login(user)
        if (num_days > NUM_INACTIVE_DAYS_TO_NOTIFY) and \
           (num_days < NUM_INACTIVE_DAYS_TO_DISABLE):
            # If in the 'notify' timeframe, but not long enough to delete
            users_to_notify.append(user)
        elif (num_days >= NUM_INACTIVE_DAYS_TO_DISABLE):
            # If in the 'delete' timeframe
            users_to_disable.append(user)

    # Write the in-memory lists to a CSV
    csv_item = write_csv(users_to_notify, users_to_disable)
    json_item = write_json(users_to_notify, users_to_disable)
    print(json_item)

    # Check if we should notify/delete the users in the in-memory lists
    if USER_DISABLE_NOTIFY_PROTECTION:
        log.warning(f"Not disabling/notifying any users, since "\
                    f"USER_DISABLE_NOTIFY_PROTECTION config variable "\
                    f"is set to `True`: Set to `False` to have "\
                    f"this notebook actually notify/disable users.")


    # Tell user we're finished
    print("-----\nNotebook completed running.")

if __name__ == "__main__":
    main()