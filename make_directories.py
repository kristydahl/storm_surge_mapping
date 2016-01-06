__author__ = 'kristydahl'
import os
import arcpy
from arcpy import env

def make_directories(location):
    all_maps_dir = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases'
    os.chdir(all_maps_dir)
    os.mkdir(location)
    location_dir = os.path.join(all_maps_dir, location)
    os.chdir(location_dir)
    os.mkdir('elevation')
    os.mkdir('general_map_elements')
    os.mkdir('map_docs')
    os.mkdir('graphics')
    os.mkdir('slosh')
    os.mkdir('slr')
    os.mkdir('symbology_layers')
    general_map_elements_dir = os.path.join(location_dir, 'general_map_elements')
    os.chdir(general_map_elements_dir)
    os.mkdir('places')
    os.mkdir('roads')
    os.mkdir('bases')
    os.mkdir('water')
    os.mkdir('states')
    gdb_name = str(location + '.gdb')
    arcpy.CreateFileGDB_management(location_dir, gdb_name)
