from app import app, db
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template, session
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from arcgis.gis import GIS
from arcgis.mapping import WebMap

from app.scripts.get_broken_links import is_url_reachable, test_urls_in_webmap, handle_unreachable, get_items_to_check
from app.forms.forms import GetBrokenLinks, AddPortalUser, ChangeUserPortal
from app.models.models import Post, User

import requests
import os
import json
import string
import urllib3
import sys
import shutil

# Creates connection to ArcGIS Portal or ArcGIS Online to allow for basic administrative tasks

#target_portal = GIS(current_user.portal_url, current_user.portal_username, current_user.portal_password)

# Iterates through Portal or AGOL and checks each Web Map for broken links
# Does require that the account specified in the users profile have
# administrative access to the Portal/AGOL Org, not a custom role
# Majority of code for this task is stored in the get_broken_links.py
# script located in the ../Scripts folder

@app.route('/admin/check-broken-items', methods=['GET', 'POST'])
@login_required
def check_broken_items():
    form = GetBrokenLinks()
    title = "Check for Broken Service Links in Portal for ArcGIS or ArcGIS Online"
    if form.validate_on_submit():
        try:
            broken_items = []
            checked_items = []
            
            for item in get_items_to_check(target_portal):
                i = {"title":item.title, "type":item.type, "owner":item.owner}
                checked_items.append(i)

                if item.type == "Web Map":
                    reachable, unreachable = test_urls_in_webmap(item)
                    if unreachable:
                        print(f"\nWebmap {item.id} unreachable. Notifying...")
                        items = handle_unreachable(item, reachable, unreachable, target_portal)
                        broken_items.append(items)

            post_body = "Query for portal broken items."
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()
            return render_template("get_broken_links_results.html", broken_items=broken_items, checked_items=checked_items)
        except:
            return render_template('500.html'), 500
    return render_template('simple_form.html', form=form, title=title)

# Checks the federation status of the ArcGIS Enterprise setup
# Will validate that each of the associated ArcGIS Servers associated with the 
# ArcGIS Enterprise installation are accessible.
# ArcGIS Data Stores will also be validated and checked. 
# Requires that the user account specified in the profile
# have administrative priviledges and not a custom role.
# This Route will only work with ArcGIS Enterprise. 

@app.route('/admin/check-federation-status', methods=['GET', 'POST'])
@login_required
def check_federation_status():
    form = GetBrokenLinks()
    title = "Check Federation Status of ArcGIS Enterprise"
    if form.validate_on_submit():
        try:
            federated_servers = []
            server_val = []

            # Makes connection to Target Portal administrative module
            portal_mgr = target_portal.admin

            # Gets list of all of the Federated Servers associated with the ArcGIS Enterprise instance
            fed_servers = portal_mgr.federation.servers['servers']

            # Iterates through list of Federated servers
            for fed_server in fed_servers:
                server = {
                    "admin_url":fed_server['adminUrl'], 
                    "server_role":fed_server['serverRole'],
                    "server_function":fed_server['serverFunction']
                    }
                federated_servers.append(server)

                # Validates all of the servers associated with ArcGIS Enterprise instance
                val_all = portal_mgr.federation.validate_all()
                val_status = {"val_status":val_all['status']}
                for val in val_all['serversStatus']:
                    s_val = {
                        "status":val['status'],
                        "server_id":val['serverId'],
                        "messages":val['messages']
                    }
                    server_val.append(s_val)

            
            # Logs that the Check Federation Status task has ran and stores it in the Users Profile so that it can be returned to the user in the "Profile" section
            post_body = "Query for server federation status."
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()

            return render_template('check_federation_status_results.html', val_status=val_status, federated_servers=federated_servers, server_val=server_val)
        except Exception as e:
            print(str(e))
    return render_template('simple_form.html', form=form, title=title)

# Returns a list of all users in the ArcGIS Portal or ArcGIS Online organization
# Requires administrative permissions associated with the user profile stored in the application

@app.route('/admin/get-users', methods=['GET', 'POST'])
@login_required
def form_get_users():
    form = GetBrokenLinks()
    title = "Get Portal for ArcGIS or ArcGIS Online Organization Users"
    if form.validate_on_submit():
        users = []
        
        # Searches for all users that are not the associated Portal or Site administrator account
        source_users = target_portal.users.search('!esri_ & !admin')

        # Returns specific  attributes assocaited with the User's profile
        for user in source_users:
            user = {
                "username":user.username,
                "firstname":user.firstName,
                "lastname":user.lastName,
                "email":user.email,
                "licensetype":user.userLicenseTypeId,
                "role":user.role,
                "storageUsage":user.storageUsage,
                "storageQuota":user.storageQuota
            }
            users.append(user)
            portal_url = {"name":str(target_portal)}

        # Logs that the Check Federation Status task has ran and stores it in the Users Profile so that it can be returned to the user in the "Profile" section
        post_body = "Query for portal users."
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return render_template('get_portal_users_results.html', portal_url=portal_url, users=users)

    return render_template('simple_form.html', form=form, title=title)

# Creates User inside of the Portal for ArcGIS or ArcGIS Online organization
# Allows whoever creates the account to specify User Role, Groups associated with the user,
# and if the user will be licensed for ArcGIS Pro.
# Current application is tailored towards creating a user on the Commercial Civil Affairs System
# Production and Training ArcGIS Online Organizations.

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
def form_create_user():
    form = AddPortalUser()
    title = 'Create CCAS User'
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data
        organization = form.organization.data
        licensepro = form.licensepro.data
        # Creates connections to Production (main_portal) and Training (training_portal)
        main_portal = GIS("https://swcs.maps.arcgis.com", "james_jones_swcs", "QWerty654321@!")
        training_portal = GIS("https://swcs-training.maps.arcgis.com", "jjones_training", "QWerty654321@!")

        # Creates the users
        target_user = main_portal.users.create(username, password, firstname, 
                                                lastname, email, role)

        training_user = training_portal.users.create(username, password, firstname, 
                                                lastname, email, role)

        # Allows the user to be added to a specific Group
        # Note that this will be updated to match the groups associated with CCAS
        if organization == 'EUCOM':
            group = target_portal.groups.search("Featured Maps and Apps")[0]
            group.add_users(target_user.username)
        
        # Allows an admin to automatically assign a user an ArcGIS Pro license
        if licensepro == 'Yes':
            pro_license = target_portal.admin.license.get('ArcGIS Pro')
            pro_license.assign(username=username, entitlements='desktopBasicN')

        users = []

        source_users = target_portal.users.search(username)

        for user in source_users:
            user = {
                "username":user.username,
                "firstname":user.firstName,
                "lastname":user.lastName,
                "email":user.email,
                "licensetype":user.userLicenseTypeId,
                "role":user.role,
                "storageUsage":user.storageUsage,
                "storageQuota":user.storageQuota
            }
            users.append(user)
        
        portal_url = {"name":str(target_portal)}

        # Logs that the Check Federation Status task has ran and stores it in the Users Profile so that it can be returned to the user in the "Profile" section
        post_body = "Created Portal User."
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return render_template('get_portal_users_results.html', portal_url=portal_url, users=users)
    return render_template('simple_form.html', form=form, title=title)

# Allows a user to query an ArcGIS Enterprise or ArcGIS Online Organization for all groups that
# are active.  
# Ignores any default groups that are native to the application and any groups assocaited with Basemaps. 

@app.route('/admin/get-groups', methods=['GET', 'POST'])
@login_required
def form_get_groups():
    form = GetBrokenLinks()
    title = "Get Groups in Portal for ArcGIS or ArcGIS Online Orgization"
    if form.validate_on_submit():
        try:
            groups = []
            # Searches portal for any groups not created by the Application or associated with Basemaps
            source_groups = target_portal.groups.search("!owner:esri_* & !Basemaps")
            for group in source_groups:
                group_members = group.get_members()
                group_content = group.content()
                content = []
                for cont in group_content:
                    c = {
                        "title":cont['title'],
                        "type":cont['type'],
                        "numViews":cont['numViews']
                    }
                    content.append(c)
                group_info = {
                    "name":group.title,
                    "owner":group_members['owner'],
                    "admins":group_members['admins'],
                    "users":group_members['users'],
                    "content":content
                }

                groups.append(group_info)

            portal_url = {"name":str(target_portal)}

            # Logs that the Get Groups task has ran and stores it in the Users Profile so that it can be returned to the user in the "Profile" section
            post_body = "Query for Portal Groups."
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()    

            return render_template('get_portal_groups_results.html', portal_url=portal_url, groups=groups)
            
        except Exception as e:
            return str(e)
    return render_template('simple_form.html', form=form, title=title)

# Searches through the various temporary or uploads directories and removes temporary files
# This is a hard delete and items will not be recoverable after delete

@app.route('/admin/clean-temp', methods=['GET', 'POST'])
@login_required
def clean_temp_directories():
    form = GetBrokenLinks()
    title = "Clean Application Temporary Directories"
    if form.validate_on_submit():

        deleted_items = []

        for root, dirname, filename in os.walk(app.config['UPLOAD_FOLDER']):
            for f in filename:
                filepath = os.path.join(root, f)
                deleted_items.append({'file': f}) 
                os.remove(filepath)
            for d in dirname:
                dirpath = os.path.join(root, d)
                deleted_items.append({'directory': d})
                shutil.rmtree(dirpath)

        for root, dirname, filename in os.walk(app.config['NETOWL_FINAL_FOLDER']):
            for f in filename:
                filepath = os.path.join(root, f)
                deleted_items.append({'file': f}) 
                os.remove(filepath)
            for d in dirname:
                dirpath = os.path.join(root, d)
                deleted_items.append({'directory': d})
                shutil.rmtree(dirpath)

        # Logs that the Clean Temporary Directories task has ran and stores it in the Users Profile so that it can be returned to the user in the "Profile" section
        post_body = "Clean temp directory."
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return render_template('clean_temp_dirs_results.html', deleted_items=deleted_items)
    return render_template('simple_form.html', form=form, title=title)

# Gets inaactive users.  Currently incomplete.

@app.route('/admin/get-inactive', methods=['GET', 'POST'])
@login_required
def form_get_inactive():
    form = GetBrokenLinks()
    if form.validate_on_submit():
        # The number of days a user is inactive for before...
        NUM_INACTIVE_DAYS_TO_NOTIFY = 60 # we notify about their inactivity
        NUM_INACTIVE_DAYS_TO_DISABLE = 90 # we delete their account
    return render_template('get_inactive_users.html', form=form)

# Allows a user to change their default portal that they are connected.
# Updates the portal information stored in the users profile.  
# Updates the session's "current_user" with portal_name, portal_url, portal_username, portal_password.
# This would be allowed to be completed by any user.

@app.route('/admin/add-portal', methods=['GET', 'POST'])
@login_required
def add_portal_info():
    form = ChangeUserPortal()
    title = "Add or Change Portal for ArcGIS or ArcGIS Online Login and Connection Information"
    if form.validate_on_submit():
        portal_url = form.portal_url.data
        portal_name = form.portal_name.data
        portal_username = form.username.data
        password = form.password.data
        login_to_portal = form.login_to_portal.data

        current_user.portal_name = portal_name
        current_user.portal_url = portal_url
        current_user.portal_username = portal_username
        current_user.portal_password = password
        db.session.commit()

        flash("Successfully updated Portal for ArcGIS connection information")

        if login_to_portal:
            global target_portal
            target_portal = GIS(portal_url, portal_username, password)
            flash("Successfully logged in to {}".format(portal_name))
        
        # Logs that the Change Portal task has ran and stores it in the Users Profile so 
        # that it can be returned to the user in the "Profile" section
        post_body = "Changed Portal for ArcGIS URL."
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
            
        next_page = url_for('index')
        return redirect(next_page), 200
    return render_template('simple_form.html', form=form, title=title)






    
