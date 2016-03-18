import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os
import os.path
import glob
import numpy
from numpy import genfromtxt

arcpy.env.overwriteOutput = True

def extend_surge(slosh_file,outname):

    gdb = str('C:/Users/kristydahl/Desktop/GIS_data/water_surface_testing.gdb')
    arcpy.env.workspace = gdb

    slosh_file = Con(IsNull(slosh_file),arcpy.sa.FocalStatistics(slosh_file, NbrCircle(100,"CELL"),"MEAN","DATA"),slosh_file)
    print(slosh_file) # This creates a tmp file within the AppData forlder. This is the file that gets fed into extend_surge below.

    any_nulls = arcpy.GetRasterProperties_management(slosh_file,"ANYNODATA")
    any_nulls_output = any_nulls.getOutput(0)
    print(any_nulls_output)

    if any_nulls_output=='1':
        print('extending surge')
        extend_surge(slosh_file,outname)
    else:
        print('done extending surge')
        #outname = 'c1_high_null_extended'
        slosh_file.save(outname)
        print('saved' + str(outname))
