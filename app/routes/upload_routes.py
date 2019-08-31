import os
import urllib3
import json
import shutil
import subprocess

from datetime import datetime
from flask import jsonify, request, send_from_directory, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db
from app.scripts import process_netowl, unzip, move_files
from app.forms.forms import UploadForm, UploadShapes, UploadImagery, UploadCMB, GetBrokenLinks
from app.models.models import User, Post

from config import Config

# Allows for the upload and subsequent updating of data from the Common Map Background.
# Data is assumed to be ZIP'd and be organized much in the same way that data will be delivered
# from the Army Geospatial Center (AGC).


@app.route('/uploads/cmb', methods=['POST', 'GET'])
@login_required
def form_upload_cmb():
    form = UploadCMB()
    if request.method == 'POST':
        # Stores the file passed via the form as a variable.
        f = request.files['file']
        filename = f.filename

        # Saves the ZIP file to the upload folder specified in the Config.py file
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))

        # Makes an entry in the profile indicating that a CMB upload has been made
        post_body = "CMB File: " + filename
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()

        # Unzips the files into a folder with the same name as the
        dirnames = unzip.unzip_file(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))

        # Specifies the file types used by the CADRG format and creates a list for
        # comparing files to ensure that they are
        cadrg_files = ['toc', 'gn2', 'jn3', 'ja2', 'mi3', 'on3', 'tp3']

        # Variable triggers used for calling the batch files later in the process.
        # If a specific file type is encountered, these triggers will be changed to True
        IMAGERY = False
        CADRG = False
        CIB = False
        DTD = False

        # Sorts the data by looking for specific file types

        print("Beginning sorting of data")
        for root, dirname, filename in os.walk(dirnames):
            for file in filename:

                # Looks for CADRG files by seeing if CADRG is in file path
                if 'CADRG' in root:
                    CADRG = True
                    src_file = os.path.join(root, file)
                    cadrg_dirs = root.split("CADRG")[1]
                    final_cadrg_dir = app.config['CADRG_FINAL_FOLDER'] + cadrg_dirs
                    if os.path.exists(final_cadrg_dir) == False:
                        try:
                            os.makedirs(final_cadrg_dir)
                        except:
                            pass

                    shutil.copy(src_file, final_cadrg_dir)

                # Looks for ECRG files based upon if ECRG is in the file path
                if 'ECRG' in root:
                    CADRG = True
                    src_file = os.path.join(root, file)

                    cadrg_dirs = root.split("ECRG")[1]
                    final_cadrg_dir = app.config['CADRG_FINAL_FOLDER'] + cadrg_dirs
                    if os.path.exists(final_cadrg_dir) == False:
                        try:
                            os.makedirs(final_cadrg_dir)
                        except:
                            pass

                    shutil.copy(src_file, final_cadrg_dir)

                # Looks for CIB based on if CIB is in the file path.
                # Moves the file to the specified directory.
                if 'CIB' in root:
                    CIB = True
                    src_file = os.path.join(root, file)
                    cib_dirs = root.split("Products\CIB")[1]
                    final_cib_dir = app.config['CIB_FINAL_FOLDER'] + cib_dirs
                    if os.path.exists(final_cib_dir) == False:
                        try:
                            os.makedirs(final_cib_dir)
                        except:
                            pass

                    shutil.copy(src_file, final_cib_dir)

                # Looks for DTED/SRTM based on if DTED/SRTM is in the file path.
                # Moves the file to the specified directory.
                if 'DTED_SRTM' in root:
                    DTD = True
                    src_file = os.path.join(root, file)
                    dtd_dirs = root.split("DTED_SRTM")[1]
                    final_dtd_dir = app.config['ELEV_FINAL_FOLDER'] + dtd_dirs
                    if os.path.exists(final_dtd_dir) == False:
                        try:
                            os.makedirs(final_dtd_dir)
                        except:
                            pass

                    shutil.copy(src_file, final_dtd_dir)

                # Looks for Buckeye Imagery based on if Buckeye is in the file path.
                # Moves the file to the specified directory.
                if 'Buckeye_MT' in root:
                    IMAGERY = True
                    src_file = os.path.join(root, file)
                    be_dirs = root.split("Buckeye_MT")[1]
                    final_be_dir = app.config['IMAGERY_FINAL_FOLDER'] + be_dirs
                    if os.path.exists(final_be_dir) == False:
                        try:
                            os.makedirs(final_be_dir)
                        except:
                            pass
                    # Passes over lidar data (too large)
                    if 'Lidar' not in root:
                        shutil.copy(src_file, final_be_dir)

                # Looks for NAIP based on if NAIP is in the file path.
                # Moves the file to the specified directory.
                if 'USDA_NAIP' in root:
                    IMAGERY = True
                    src_file = os.path.join(root, file)
                    naip_dirs = root.split("USDA_NAIP")[1]
                    final_naip_dir = app.config['IMAGERY_FINAL_FOLDER'] + naip_dirs
                    if os.path.exists(final_naip_dir) == False:
                        try:
                            os.makedirs(final_naip_dir)
                        except:
                            pass

                    shutil.copy(src_file, final_naip_dir)

        # If the specified trigger has been flagged, runs the specified batch file.
        # Batch files open a specific version of ArcPy and run a script that has ArcPy dependencies.
        # Batch file process was used because errors kept being raised when calling ArcPy functions
        # from Flask enabled web application.

        # Batch files are located in ../Scripts/batch
        if IMAGERY:
            if os.path.exists(app.config['IMAGERY_FINAL_FOLDER']):
                subprocess.call(
                    [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_imagery_mosaic.bat'])
        if CADRG:
            if os.path.exists(app.config['CADRG_FINAL_FOLDER']):
                subprocess.call(
                    [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_cadrg_mosaic.bat'])
        if DTD:
            if os.path.exists(os.path.join(app.config['ELEV_FINAL_FOLDER'], 'dted1')):
                subprocess.call(
                    [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_dted1_mosaic.bat'])
            if os.path.exists(os.path.join(app.config['ELEV_FINAL_FOLDER'], 'dted2')):
                subprocess.call(
                    [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_dted2_mosaic.bat'])
        if CIB:
            if os.path.exists(app.config['CIB_FINAL_FOLDER']):
                subprocess.call(
                    [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_cib_mosaic.bat'])

        return render_template('upload_cmb_results.html')
    if request.method == 'GET':
        return render_template('upload.html', form=form)


# Renders the map based on the services housed from the CMB upload
@app.route('/uploads/test-cmb')
def form_test_cmb():
    return render_template('upload_cmb_results.html')


# Process that checks if each of the necessary intermediate folders,
# file geodatabases, and mosaic datasets are accessible and created.
# If folders, file geodatase, and mosaics are not created, process will
# automatically create them.
@app.route('/uploads/check-files-folders', methods=['POST', 'GET'])
@login_required
def check_files_folders():
    title = "Validate Folders, File Geodatabase, and Mosaic Datasets"
    form = GetBrokenLinks()
    if form.validate_on_submit():
        subprocess.call(
            [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\check_files_folders.bat'])
        post_body = "Validated Upload CMB Files and Folder"
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return "Success!"
    return render_template('simple_form.html', form=form, title=title)


# Creates a OGC Geopackage from the CADRG Folder
@app.route('/uploads/create-cadrg-gpkg', methods=['POST', 'GET'])
@login_required
def create_cadrg_gpkg():
    form = GetBrokenLinks()
    title = "Create OGC Geopackage from CADRG Folder"
    if form.validate_on_submit():
        subprocess.call(
            [r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\create_cadrg_gpkg.bat'])
        post_body = "Created CADRG Geopackage"
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return "Success!"
    return render_template('simple_form.html', form=form, title=title)
