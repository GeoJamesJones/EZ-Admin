#from app import app

import arcpy
import argparse
import os
import logging
import time

def update_mosaic(workspace, mosaic_dataset, raster_type):

    print('Completed copy of data, beginning update of Mosaic Dataset.')
    try:
        url_dict = {"cmb_ScannedMaps":"https://localhost:6443/arcgis/rest/services/ScannedMaps/cmb_ScannedMaps/MapServer/3",
                    "cmb_Imagery":"https://localhost:6443/arcgis/rest/services/Imagery/cmb_Imagery/MapServer/3",
                    "CIB_5":"https://localhost:6443/arcgis/rest/services/Imagery/CIB_5/MapServer/3",
                    "DTED_1":"https://localhost:6443/arcgis/rest/services/Imagery/DTED_1/MapServer/3",
                    "DTED_2":"https://localhost:6443/arcgis/rest/services/Imagery/DTED_2/MapServer/3"}

        arcpy.AddRastersToMosaicDataset_management(mosaic_dataset, raster_type=raster_type, input_path=workspace)
        arcpy.AddField_management(mosaic_dataset + "\Boundary", "Name", "TEXT", field_length=255)
        arcpy.AddField_management(mosaic_dataset + "\Boundary", "URLs", "TEXT", field_length=255)
        arcpy.CalculateField_management(mosaic_dataset + "\Boundary", "Name", mosaic_dataset, "PYTHON_9.3")
        arcpy.CalculateField_management(mosaic_dataset + "\Boundary", "URLs", url_dict[mosaic_dataset], "PYTHON_9.3")


        mosaic_updated = True
    except Exception as e:
        print(str(e))
        mosaic_updated = False 

    print("Completed update of Mosaic Dataset")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workspace", help="Workspace", required=True)
    parser.add_argument("-md", "--mosaic_dataset", help="Mosaic Dataset", required=True)
    parser.add_argument("-r", "--raster_type", help="Raster Type", required=True)
    args = parser.parse_args()

    try:
        update_mosaic(args.workspace, args.mosaic_dataset, args.raster_type)

    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()