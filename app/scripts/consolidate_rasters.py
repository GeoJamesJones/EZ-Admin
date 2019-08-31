import arcpy
import argparse
import os
import logging
import time

# Updates a specified mosaic dataset.


def update_mosaic(workspace, mosaic_dataset, raster_type):

    print('Completed copy of data, beginning update of Mosaic Dataset.')
    try:

        # ArcPy function to add data to mosaic dataset
        arcpy.AddRastersToMosaicDataset_management(
            mosaic_dataset, raster_type=raster_type, input_path=workspace)
        mosaic_updated = True
    except Exception as e:
        print(str(e))
        mosaic_updated = False

    print("Completed update of Mosaic Dataset")

# Main function that allows for script to be reused multiple times.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workspace", help="Workspace", required=True)
    parser.add_argument("-md", "--mosaic_dataset",
                        help="Mosaic Dataset", required=True)
    parser.add_argument("-r", "--raster_type",
                        help="Raster Type", required=True)
    args = parser.parse_args()

    try:
        update_mosaic(args.workspace, args.mosaic_dataset, args.raster_type)

    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()
