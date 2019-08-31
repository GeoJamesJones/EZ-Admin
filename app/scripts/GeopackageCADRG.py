import arcpy
import os

# Creates an OGC Geopackage from the CADRG Folder

cwd = arcpy.env.workspace = r"C:\services\data\cadrg"

workspaces = arcpy.ListWorkspaces("*")

gpkgs = []

try:

    for workspace in workspaces:
        gpkg_name = os.path.split(workspace)[1] + ".gpkg"
        if arcpy.Exists(gpkg_name) == False:
            arcpy.CreateSQLiteDatabase_management(gpkg_name, 'GEOPACKAGE_1.2')
            print("Successfully created " + gpkg_name)
        else:
            print(gpkg_name + " already exists...")

        gpkgs.append(gpkg_name)

        toc_files = []
        for root, dirname, filename in arcpy.da.Walk(workspace):
            for file in filename:
                if file == "A.TOC":
                    toc_files.append(os.path.join(root, file))

        count = 0
        for toc in toc_files:
            arcpy.AddRasterToGeoPackage_conversion(toc, gpkg_name, os.path.split(workspace)[
                                                   1] + "_" + str(count), "TILED")
            count += 1
            print("Successfully added files to " + gpkg_name)

except Exception as e:
    print("Error: " + str(e))
    exit()

finally:
    print("Completed Geopackaging CADRG")
