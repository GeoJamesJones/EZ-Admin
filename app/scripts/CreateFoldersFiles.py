import arcpy
import os

# Script that ensures that all of the necessary files and folders are created
# for the Upload CMB process.

to_check = {
    "SHAPE_FINAL_FOLDER": ("File", r'C:\services\data\shapes'),
    "ELEV_FINAL_FOLDER": ("File", r'C:\services\data\elevation'),
    "CADRG_FINAL_FOLDER": ("File", r'C:\services\data\cadrg'),
    "CIB_FINAL_FOLDER": ("File", r'C:\services\data\cib'),
    "IMAGERY_FINAL_FOLDER": ("File", r'C:\services\data\imagery'),
    "UPLOADS_FOLDER": ("File", r"C:\uploads"),
    "CADRG_MOSAIC": ("Mosaic", "CADRG"),
    "DTED1_MOSAIC": ("Mosaic", "DTED1"),
    "DTED2_MOSAIC": ("Mosaic", "DTED2"),
    "CIB_MOSAIC": ("Mosaic", "CIB"),
    "IMAGERY_MOSAIC": ("Mosaic", "IMAGERY")
}

fgdb_path = r"C:\services\mosaics\geodata.gdb"
if arcpy.Exists(fgdb_path):
    print(fgdb_path + " exists")
else:
    if os.path.exists(os.path.split(fgdb_path)[0]) == False:
        os.makedirs(os.path.split(fgdb_path)[0], mode=0o777)
        arcpy.CreateFileGDB_management(
            os.path.split(fgdb_path)[0], os.path.split(path)[1])
    else:
        arcpy.CreateFileGDB_management(
            os.path.split(fgdb_path)[0], os.path.split(path)[1])
    print("Created " + fgdb_path)

for key, value in to_check.items():
    file_type = value[0]
    path = value[1]
    print("Checking " + path)
    if file_type == 'File':
        if os.path.exists(path):
            print(path + " exists")
        else:
            os.makedirs(path, mode=0o777)
            print("Created " + path)

    elif file_type == "Mosaic":
        mosaic_fgdb = to_check["MOSAICS_GEODATABASE"][1]
        if arcpy.Exists(os.path.join(mosaic_fgdb, path)):
            print(path + " exists")
        else:
            sr = arcpy.SpatialReference(4326)
            arcpy.CreateMosaicDataset_management(mosaic_fgdb, path, sr)
            print("Created " + path)
    print("=======================")
