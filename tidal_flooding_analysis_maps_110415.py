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


def set_file_paths(location, dem_file, slr_file):

    location_path = os.path.join("C:/Users/kristydahl/Desktop/GIS_data/military_bases", location)
    elevation_path = os.path.join(location_path, "elevation")
    dem = os.path.join(location_path, "elevation", dem_file)
    slr_path = os.path.join(location_path,'slr')
    slr_data = os.path.join(slr_path,slr_file)
    gdb = str(location + '.gdb')
    results_path = os.path.join(location_path, gdb)
    arcpy.env.workspace = results_path

    return { 'location': location_path, 'dem': dem, 'slr_data': slr_data, 'elevation': elevation_path, 'dem': dem, 'results': results_path}


def water_surfaces(location, dem_file, slr_file):

    paths = set_file_paths(location,dem_file,slr_file)
    slr_csv_data = os.path.join(paths['location'], "slr", slr_file)
    slr_data = genfromtxt(slr_csv_data,dtype=None, skip_header=1,delimiter=',')
    dem = paths['dem']

    surfaces = []

    for row in slr_data:
        print('Creating surfaces')
        year = row[0]
        value = row[1]
        projection=row[2]
        print(row)
        surface = Con(Raster(dem)/0.3048 <=row[1], 1) #Use DEM in meters and flood level in feet!!
        outname = (paths['results'] + str("/" + 'tf_extent' + "_" + str(int(row[0]))+ '_' + str(row[2])))
        surface.save(outname)
        surfaces.append(surface)

    print("Surfaces created")
    return(surfaces)

def create_clipping_polygon(location,dem_file):
    location_path = os.path.join("C:/Users/kristydahl/Desktop/GIS_data/military_bases", location)
    elevation_path = os.path.join(location_path, "elevation")
    dem = os.path.join(location_path, "elevation", dem_file)

    extents = ["LEFT", "RIGHT", "TOP", "BOTTOM"]
    corners = []


    for extent in extents:
        corner_tmp = arcpy.GetRasterProperties_management(dem, extent)
        corner = corner_tmp.getOutput(0)
        corners.append(corner)
        corners = [float(item) for item in corners]

    x1 = corners[0]
    x2 = corners[1]
    y1 = corners[3]
    y2 = corners[2]

    # Create new polygon with extent and coordinate system of raster

    features=[]
    coord_info = [[x1,y2], [x2, y2], [x2, y1], [x1, y1]]

    for coord in coord_info:
        features.append(arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in coord_info])))

    output_clipping_polygon = os.path.join(elevation_path, "clipping_polygon.shp")
    print(output_clipping_polygon)

    arcpy.CopyFeatures_management(features, output_clipping_polygon)
    print('Created clipping polygon')
    return(output_clipping_polygon)


def region_group_extract(location, dem_file,slr_file):
    paths = set_file_paths(location, dem_file,slr_file)
    surfaces = water_surfaces(location, dem_file,slr_file)

    region_grouped_files = []
    extracted_files = []
    final_polygons = []

    for surface in surfaces:
        fullname = str(surface)
        print('surface name is ' + fullname)
        filename = os.path.basename(fullname)

        # Perform region group
        print('Region grouping' + filename)
        outRegionGrp = RegionGroup(fullname, "EIGHT", "WITHIN",'NO_LINK')
        outname_rg = (paths['results'] + str("/rg_" + filename))
        outRegionGrp.save(outname_rg)

        print("Region grouped" + filename)

        # Extract connected areas

        fullname = str(outname_rg)
        print('File to extract is ' + fullname)
        filename = os.path.basename(fullname)
        outname_extract = (paths['results'] +  str('/extract_' + filename))

        print('Extracting' + filename)
        arr = arcpy.da.FeatureClassToNumPyArray(outname_rg, ('Value', 'Count'))
        count = arr['Count']
        value = arr['Value']
        index_to_extract = numpy.argmax(count)
        value_to_extract = str(value[index_to_extract])

        inSQLClause = 'Value =' + value_to_extract
        print('Extracting ' + value_to_extract + 'from ' + filename)

        attExtract = ExtractByAttributes(fullname, inSQLClause)
        attExtract.save(outname_extract)
        extracted_files.append(attExtract)
        print('Extracted connected areas from' + outname_rg)

        # create polygon    START HERE!
        fullname = str(outname_extract)
        filename = os.path.basename(fullname)
        outname_polygon = str(paths['results'] + '/final_polygon_' + filename )


        arcpy.RasterToPolygon_conversion(fullname, outname_polygon,"SIMPLIFY", "VALUE")
        final_polygons.append(outname_polygon)

        print('Converted ' + outname_extract + ' to polygon')
    return {'final_polygons': final_polygons}

def create_maps(location,projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/UCS_tidal_flooding_maps',location)
    map_path = os.path.join(location_path,'map_docs')
    sym_layers_path = os.path.join(location_path, 'symbology_layers')
    gdb = str(location + '.gdb')
    results_path = os.path.join(location_path, gdb)
    arcpy.env.workspace = results_path

    testmap = os.path.join(location_path, 'testmap_2col_tidal_flooding.mxd')
    sym_layer = os.path.join(sym_layers_path,'water_style.lyr')
    print(sym_layer)

    #shps = region_group_extract(location, dem_file, slr_file)
    shps = arcpy.ListFeatureClasses('final_polygon*tf_extent_*_%s' %(projection))

    mxd = arcpy.mapping.MapDocument(testmap)
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]


    outmap = os.path.join(map_path, 'tidal_flooding_surfaces_' + projection + '.mxd')

    for shp in shps:
        shp_with_full_path = os.path.join(results_path, shp)
        print(shp_with_full_path)
        lyr = arcpy.mapping.Layer(shp_with_full_path)
        arcpy.ApplySymbologyFromLayer_management(lyr,sym_layer)
        arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
        print('Added ' + shp + ' to map')
    mxd.saveACopy(outmap)

    del mxd, lyr

def add_common_layers(location,dem_file):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/UCS_tidal_flooding_maps',location)
    folders_path = os.path.join(location_path, 'general_map_elements')
    folders = glob.glob1(folders_path,'*')

    map_path = os.path.join(location_path,'map_docs')
    maps = glob.glob1(map_path,'*.mxd')


    for each_map in maps:
        map_with_full_path = os.path.join(map_path,each_map)
        mxd = arcpy.mapping.MapDocument(map_with_full_path)
        df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

        each_map_no_ext = os.path.splitext(map_with_full_path)

        clipping_polygon = create_clipping_polygon(location,dem_file)

        for folder in folders:
            full_folder_path = os.path.join(folders_path,folder)
            shp = glob.glob1(full_folder_path,'*.shp')

            if len(shp) >=1:

                for i in shp:
                    shp_with_full_path = os.path.join(full_folder_path,i)
                    print(shp)
                    sym_layer = glob.glob1(full_folder_path,'*_style*')
                    sym_layer_with_full_path = os.path.join(full_folder_path,sym_layer[0])
                    print('Repairing Geometry')
                    arcpy.RepairGeometry_management(shp_with_full_path)
                    print('Repaired Geometry')

                    outname_clipped_lyr = os.path.join(full_folder_path, 'clipped_' + i)
                    clipped_lyr = arcpy.Clip_analysis(shp_with_full_path, clipping_polygon, outname_clipped_lyr)

                    print(clipped_lyr)

                    lyr = arcpy.mapping.Layer(outname_clipped_lyr)
                    print(lyr)

                    arcpy.ApplySymbologyFromLayer_management(lyr, sym_layer_with_full_path)

                    arcpy.mapping.AddLayer(df,lyr,"TOP")
                    print('Added ' + i + ' to ' + each_map)
                    outmap = each_map_no_ext[0] + '_gen_lyrs_added.mxd'
        mxd.saveACopy(outmap)
        #Will export to PNG, EPS, and AI manually so that each map has a visual check before exporting










__author__ = 'kristydahl'
