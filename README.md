# EZ-Admin

## Background on Application

Application helps simplify Administration of ArcGIS Enterprise and provides an API that aids in transforming unstructured data into a usable format by the ArcGIS Platform. <br>

## Application Structure

root:<br>
ez_admin.py<br>
config.py<br>
app<br>
    \forms<br>
        \forms.py<br>
    \models<br>
        \models.py<br>
    \routes<br>
        admin_routes.py<br>
        analyze_routes.py<br>
        api_routes.py<br>
        errors.py<br>
        query_routes.py<br>
        routes.py<br>
        upload_routes.py<br>
    \scripts<br>
        \batch<br>
            check_files_folders.bat<br>
            create_cadrg_gpkg.bat<br>
            update_cadrg_mosaic.bat<br>
            update_cib_mosaic.bat<br>
            update_dted1_mosaic.bat<br>
            update_dted2_mosaic.bat<br>
            update_imagery_mosaic.bat<br>
        \data<br>
            CCAS_Affiliations.csv<br>
        azure_cognitive.py<br>
        bucketizebing.py<br>
        bucketizenews.py<br>
        check_for_inactive_users.py<br>
        consolidate_rasters.py<br>
        create_ca_list.py<br>
        CreateFoldersFiles.py<br>
        detect_faces.py<br>
        geoevent.py<br>
        GeopackageCADRG.py<br>
        get_broken_links.py<br>
        load_CA_affiliations.py<br>
        move_files.py<br>
        process_netowl.py<br>
    templates<br>
    __init__.py<br>
    search.py<br>
    logs<br>
    migrations<br>
    static<br>
        \images<br>


## Setup

Step 1:  Download EZ-Admin to local file system<br>
Step 2:  Create either conda environment or virtual environment<br>
Step 3:  Activate the conda environment or virtual environment<br>
Step 4:  Run pip install -r requirements.txt. This will install all of the necessary python packages. <br>
Step 5:  Run test_ez_admin.sh.  This will run the unit tests for the application. <br>
Step 6:  Run start_ez_admin_production.sh.  This will set the necessary environment variables and run the application on a production web server (Waitress). If you need to run the application in a development environment, run start_ez_admin_development.sh.  <br>

