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
#from app.scripts import consolidate_rasters
from app.forms.forms import UploadForm, UploadShapes, UploadImagery, UploadCMB
from app.models.models import User, Post, NetOwl_Entity

from config import Config

urllib3.disable_warnings()

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.upload.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], 'documents', filename
        ))
        post_body = "Document: " + filename
        post = Post(body=post_body, author=current_user)
        db.session.add(post)
        
        final_folder = app.config['NETOWL_FINAL_FOLDER']
        uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', filename)
        process_netowl.netowl_curl(uploaded_file, final_folder, ".json", app.config['NETOWL_KEY'])
        with open(os.path.join(final_folder, filename +'.json'), 'rb') as json_file:
            data = json.load(json_file)

        entity_list = process_netowl.process_netowl_json(f.filename, data)

        spatial_entities = []
        nonspatial_entities = []

        for entity in entity_list:
            if entity.geo_entity == True:
                spatial_entities.append(vars(entity))
                """try:
                    no_entity = NetOwl_Entity(
                            geoentity=entity['geo_entity'],
                            geosubtype=entity['geo_subtype'],
                            geotype=entity['geo_type'],
                            entity_id=entity['id'],
                            lat=entity['lat'],
                            lon=entity['long'],
                            norm=entity['norm'],
                            ontology=entity['ontology'],
                            pretext=entity['pre_text'],
                            value=entity['value'],
                            posttext=entity['post_text'],
                            user_id=current_user)
                except Exception as e:
                    return str(e)"""
            else:
                nonspatial_entities.append(vars(entity))

        os.remove(uploaded_file)
        os.remove(os.path.join(final_folder, filename +'.json'))

        db.session.commit()

        return render_template('results.html', query=spatial_entities)

        #return redirect(url_for('index'))

    return render_template('upload.html', form=form)

@app.route('/uploads/shapes', methods=['POST', 'GET'])
@login_required
def form_upload_shapes():
    form = UploadShapes()
    if form.validate_on_submit():
        if form.datatype.data == 'Shapefile':
            f = form.upload.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename
            ))
            post_body = "Shapefiles: " + filename
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()
            final_folder = app.config['SHAPE_FINAL_FOLDER']
            if os.path.exists(final_folder) == False:
                os.makedirs(final_folder)
            dirname = unzip.unzip_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            copied_shapes = move_files.copy_directory(dirname,final_folder, "Upload Shapefiles")

            #return jsonify(copied_shapes)
            return render_template('job_results.html', job=copied_shapes)
        elif form.datatype.data == "Elevation":
            f = form.upload.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'elev', filename
            ))
            post_body = "Elevation Data: " + filename
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()
            final_folder = app.config['ELEV_FINAL_FOLDER']
            dirname = unzip.unzip_file(os.path.join(app.config['UPLOAD_FOLDER'], 'elev', filename))
            copied_elev = move_files.copy_directory(dirname,final_folder, "Upload Elevation")
            #consolidate_rasters.update_mosaic(final_folder, app.config['ELEVATION_MOSAIC'])

            #return jsonify(copied_shapes)
            return render_template('job_results.html', job=copied_elev)
    return render_template('upload.html', form=form)

@app.route('/uploads/imagery', methods=['POST', 'GET'])
@login_required
def form_upload_imagery():
    form = UploadImagery()
    if form.validate_on_submit():
        if form.datatype.data == 'cadrg':
            f = form.upload.data
            filename = secure_filename(f.filename)
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'cadrg')) == False:
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], 'cadrg'))
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'cadrg', filename
            ))
            post_body = "CADRG: " + filename
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()
            os.mkdir(os.path.join(app.config['CADRG_FINAL_FOLDER'], filename.split(".")[0]))
            final_folder = os.path.join(app.config['CADRG_FINAL_FOLDER'], filename.split(".")[0])
            dirname = unzip.unzip_file(os.path.join(app.config['UPLOAD_FOLDER'], 'cadrg', filename))
            copied_imagery = move_files.copy_directory(dirname,final_folder, "Upload CADRG")
            #consolidate_rasters.update_mosaic(final_folder, app.config['CADRG_MOSAIC'])

            #return jsonify(copied_shapes)
            return render_template('job_results.html', job=copied_imagery)
        elif form.datatype.data == 'cib':
            f = form.upload.data
            filename = secure_filename(f.filename)
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'cib')) == False:
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], 'cib'))
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'cib', filename
            ))
            post_body = "CIB: " + filename
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()
            os.mkdir(os.path.join(app.config['CIB_FINAL_FOLDER'], filename.split(".")[0]))
            final_folder = os.path.join(app.config['CIB_FINAL_FOLDER'], filename.split(".")[0])
            dirname = unzip.unzip_file(os.path.join(app.config['UPLOAD_FOLDER'], 'cib', filename))
            copied_imagery = move_files.copy_directory(dirname,final_folder, "Upload CIB")
            #consolidate_rasters.update_mosaic(final_folder, app.config['CIB_MOSAIC'])

            #return jsonify(copied_shapes)
            return render_template('job_results.html', job=copied_imagery)
        elif form.datatype.data == 'imagery':
            f = form.upload.data
            filename = secure_filename(f.filename)
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'imagery')) == False:
                os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], 'imagery'))
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'imagery', filename
            ))
            post_body = "Imagery: " + filename
            post = Post(body=post_body, author=current_user)
            db.session.add(post)
            db.session.commit()
            os.mkdir(os.path.join(app.config['IMAGERY_FINAL_FOLDER'], filename.split(".")[0]))
            final_folder = os.path.join(app.config['IMAGERY_FINAL_FOLDER'], filename.split(".")[0])
            dirname = unzip.unzip_file(os.path.join(app.config['UPLOAD_FOLDER'], 'imagery', filename))
            copied_imagery = move_files.copy_directory(dirname,final_folder, "Upload Imagery")
            #consolidate_rasters.update_mosaic(final_folder, app.config['IMAGERY_MOSAIC'])

            #return jsonify(copied_shapes)
            return render_template('job_results.html', job=copied_imagery)
    return render_template('upload.html', form=form)

@app.route('/uploads/cmb', methods=['POST', 'GET'])
@login_required
def form_upload_cmb():
    form = UploadCMB()
    if form.validate_on_submit():
        f = form.upload.data
        filename = secure_filename(f.filename)
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

        
        #subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\stop_service.bat'])
        if IMAGERY:
            if os.path.exists(app.config['IMAGERY_FINAL_FOLDER']):
                subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\update_imagery_mosaic.bat'])
        if CADRG:
            if os.path.exists(app.config['CADRG_FINAL_FOLDER']):
                subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\update_cadrg_mosaic.bat'])
        if DTD:
            if os.path.exists(os.path.join(app.config['ELEV_FINAL_FOLDER'], 'dted1')):
                subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\update_dted1_mosaic.bat']) 
            if os.path.exists(os.path.join(app.config['ELEV_FINAL_FOLDER'], 'dted2')):
                subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\update_dted2_mosaic.bat'])
        if CIB:
             if os.path.exists(app.config['CIB_FINAL_FOLDER']):
                subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\update_cib_mosaic.bat'])
        
        print("Stopping services...")
        print("Updating footprints layer...")
        print("Restarting services...")
        #subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\update_footprints.bat'])
        #subprocess.call([r'C:\Users\localadmin\Documents\GitHub\bucketize-api\app\scripts\batch\start_service.bat'])

        return render_template('upload_cmb_results.html')
    return render_template('upload.html', form=form)

@app.route('/uploads/test-cmb')
def form_test_cmb():
    return render_template('upload_cmb_results.html')