import arcpy
import os

to_check = {
    "SHAPE_FINAL_FOLDER":("File", r'C:\services\data\shapes'),
    "ELEV_FINAL_FOLDER":("File", r'C:\services\data\elevation'),
    "CADRG_FINAL_FOLDER":("File", r'C:\services\data\cadrg'),
    "CIB_FINAL_FOLDER":("File", r'C:\services\data\cib'),
    "IMAGERY_FINAL_FOLDER":("File", r'C:\services\data\imagery'),
    "MOSAICS_GEODATABASE":("FGDB", r"C:\services\mosaics\geodata.gdb"),
    "UPLOADS_FOLDER":("File", r"C:\uploads"),
    "CADRG_MOSAIC":("Mosaic", "CADRG"),
    "DTED1_MOSAIC":("Mosaic", "DTED1"),
    "DTED2_MOSAIC":("Mosaic", "DTED2"),
    "CIB_MOSAIC":("Mosaic", "CIB"),
    "IMAGERY_MOSAIC":("Mosaic", "IMAGERY"),
}

for key, value in to_check.items():
    file_type = value[0]
    path = value[1]
    print(key)
    print(file_type)
    print("Checking " + path)
    if file_type == 'File':
        if os.path.exists(path):
            print(path + " exists")
        else:
            os.mkdir(path, mode=0o777)
            print("Created " + path)
    elif file_type == "FGDB":
        if arcpy.Exists(path):
            print(path + " exists")
        else:
            arcpy.CreateFileGDB_management(os.path.split(path)[0], os.path.split(path)[1])
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