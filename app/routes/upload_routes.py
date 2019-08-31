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
from app.models.models import User, Post, NetOwl_Entity

from config import Config

@app.route('/uploads/cmb', methods=['POST', 'GET'])
@login_required
def form_upload_cmb():
    form = UploadCMB() 
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))
        post_body = "CMB File: " + filename
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()

        dirnames = unzip.unzip_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cadrg_files = ['toc', 'gn2', 'jn3', 'ja2', 'mi3', 'on3', 'tp3']

        IMAGERY = False
        CADRG = False
        CIB = False
        DTD = False

        print("Beginning sorting of data")
        for root, dirname, filename in os.walk(dirnames):
            for file in filename:
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
                    
                    if 'Lidar' not in root:
                        shutil.copy(src_file, final_be_dir)

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

    
        if IMAGERY:
            if os.path.exists(app.config['IMAGERY_FINAL_FOLDER']):
                subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_imagery_mosaic.bat'])
        if CADRG:
            if os.path.exists(app.config['CADRG_FINAL_FOLDER']):
                subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_cadrg_mosaic.bat'])
        if DTD:
            if os.path.exists(os.path.join(app.config['ELEV_FINAL_FOLDER'], 'dted1')):
                subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_dted1_mosaic.bat']) 
            if os.path.exists(os.path.join(app.config['ELEV_FINAL_FOLDER'], 'dted2')):
                subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_dted2_mosaic.bat'])
        if CIB:
             if os.path.exists(app.config['CIB_FINAL_FOLDER']):
                subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\update_cib_mosaic.bat'])


        return render_template('upload_cmb_results.html')
    if request.method == 'GET':
            return render_template('upload.html', form=form)

@app.route('/uploads/test-cmb')
def form_test_cmb():
    return render_template('upload_cmb_results.html')

@app.route('/uploads/check-files-folders', methods=['POST', 'GET'])
@login_required
def check_files_folders():
    form = GetBrokenLinks()
    if form.validate_on_submit():
        subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\check_files_folders.bat'])
        post_body = "Validated Upload CMB Files and Folder"
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return "Success!"
    return render_template('validate_upload_files.html', form=form)

@app.route('/uploads/create-cadrg-gpkg', methods=['POST', 'GET'])
@login_required
def create_cadrg_gpkg():
    form = GetBrokenLinks()
    if form.validate_on_submit():
        subprocess.call([r'C:\Users\arcgis\Documents\GitHub\wdc-integration\app\scripts\batch\create_cadrg_gpkg.bat'])
        post_body = "Created CADRG Geopackage"
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        db.session.commit()
        return "Success!"
    return render_template('create_cadrg_gpkg.html', form=form)