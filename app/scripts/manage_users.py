import time
import datetime as dt
from datetime import timedelta

from arcgis.gis import GIS

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
    return last_login + timedelta(days=NUM_INACTIVE_DAYS_TO_DISABLE)ß
