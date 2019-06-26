from app import app

import os
import zipfile
import logging


def unzip_file(file):
    app.logger.info("Beginning unzip of file.")
    zip_ref = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], file), 'r')
    folder = os.path.splitext(file)[0]
    outdir = os.makedirs(os.path.dirname(os.path.join(app.config['UPLOAD_FOLDER'],folder)), exist_ok=True)
    out_directory = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    zip_ref.extractall(out_directory)
    zip_ref.close()
    app.logger.info("Successfully unzipped file.")
    return out_directory