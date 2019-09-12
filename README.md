# EZ-Admin

## Background on Application

Application helps simplify Administration of ArcGIS Enterprise and provides an API that aids in transforming unstructured data into a usable format by the ArcGIS Platform. <br>

## Dependencies

<ol>
<li>Python 3.6 or greater</li>
<li>Elasticsearch 7.3</li>
<li>Microsoft Cognitive Services Keys:</li>
<ul>
<li>Faces API</li>
<li>Computer Vision API</li>
<li>Translation Service API</li>
<li>Text API</li>
<li>Content Moderation Service</li>
</ul>
<li>NetOwl API Key</li>
</ol>

## Setup

Step 1:  Download EZ-Admin to local file system<br>
Step 2:  Create either conda environment or virtual environment<br>
Step 3:  Activate the conda environment or virtual environment<br>
Step 4:  Run pip install -r requirements.txt. This will install all of the necessary python packages. <br>
Step 5:  Run test_ez_admin.sh.  This will run the unit tests for the application. <br>
Step 6:  Run start_ez_admin_production.sh.  This will set the necessary environment variables and run the application on a production web server (Waitress). If you need to run the application in a development environment, run start_ez_admin_development.sh.  <br>

## Application Structure

<ul>
<li>root:</li>
<li>ez_admin.py</li>
<li>config.py</li>
<li>app</li>
<ul>
<ul>
<li>\forms</li>
<ul>
<li>\forms.py</li>
</ul>
</ul>
<ul>
<li>\models</li>
<ul>
<li>\models.py</li>
</ul>
</ul>
<ul>
<li>\routes</li>
<ul>
<li>admin_routes.py</li>
<li>analyze_routes.py</li>
<li>api_routes.py</li>
<li>errors.py</li>
<li>query_routes.py</li>
<li>routes.py</li>
<li>upload_routes.py</li>
</ul>
</ul>
<ul>
<li>\scripts</li>
<ul>
<li>\batch</li>
<ul>
<li>check_files_folders.bat</li>
<li>create_cadrg_gpkg.bat</li>
<li>update_cadrg_mosaic.bat</li>
<li>update_cib_mosaic.bat<br></li>
<li>update_dted1_mosaic.bat<br></li>
<li>update_dted2_mosaic.bat<br></li>
<li>update_imagery_mosaic.bat<br></li>
</ul>
<li>\data<br></li>
<ul>
<li>CCAS_Affiliations.csv<br></li>
</ul>
<li>azure_cognitive.py<br></li>
<li>bucketizebing.py<br></li>
<li>bucketizenews.py<br></li>
<li>check_for_inactive_users.py<br></li>
<li>consolidate_rasters.py<br></li>
<li>create_ca_list.py<br></li>
<li>CreateFoldersFiles.py<br></li>
<li>detect_faces.py<br></li>
<li>geoevent.py<br></li>
<li>GeopackageCADRG.py<br></li>
<li>get_broken_links.py<br></li>
<li>load_CA_affiliations.py<br></li>
<li>move_files.py<br></li>
<li>process_netowl.py<br></li>
</ul>
<li>templates<br></li>
<li>__init__.py<br></li>
<li>search.py<br></li>
</ul>
<li>logs<br></li>
<li>migrations<br></li>
<li>static<br></li>
<li>\images<br></li>
</ul>