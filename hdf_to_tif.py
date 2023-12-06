import os
import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True
path = r"E:\LAI"
# arcpy.env.workspace = path

for year_folder in os.listdir(path):
    sub_path = rf'{path}\{year_folder}'
    # print(sub_path)
    for hdf_file_name in os.listdir(sub_path):
        if not hdf_file_name.endswith('.hdf'):
            continue
        else:
            hdf_path = rf"{sub_path}\{hdf_file_name}"
            in_hdf = hdf_path
            out_hdf_to_raster = rf"{sub_path}\{hdf_file_name[:-4]}.tif"
            arcpy.management.ExtractSubDataset(in_hdf, out_hdf_to_raster)
            print(f'Extracting LAI_{hdf_file_name} !')
print('done.')
