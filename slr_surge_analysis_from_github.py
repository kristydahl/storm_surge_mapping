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

# Set paths to data
def set_file_paths(location, slosh_file, dem_file):
    #print('Setting file paths')
    location_path = os.path.join("C:/Users/kristydahl/Desktop/GIS_data/military_bases", location)
    slosh_path = os.path.join(location_path, "slosh")
    slosh_file_path = os.path.join(slosh_path, slosh_file)
    elevation_path = os.path.join(location_path, "elevation")
    dem = os.path.join(location_path, "elevation", dem_file)
    gdb = str(location + '.gdb')
    results_path = os.path.join(location_path, gdb)

    return { 'location': location_path, 'slosh': slosh_path, 'slosh_file': slosh_file_path, 'elevation': elevation_path, 'dem': dem, 'results': results_path}
    print('File paths are set')

# Prep slosh data by removing 99.9 values using UpdateCursor. ***This needs to be run first!***
def prep_data(location,slosh_file,dem_file):
    print('Prepping slosh data from ' + slosh_file)
    paths = set_file_paths(location, slosh_file, dem_file)
    field_names = [f.name for f in arcpy.ListFields(paths['slosh_file'], "*_high")]
    print(field_names)

    for field in field_names:
        print(field)
        with arcpy.da.UpdateCursor(paths['slosh_file'],field) as cursor:
            for row in cursor:
                if row[0] == 99.9000015258789:
                    row[0] = 0
                    # TODO: refactor so it creates a new file instead of updating in place
                    cursor.updateRow(row)
        print ("Updated")

    del row
    del cursor

    return(field_names)


def clip_resample_slosh(location, slosh_file, dem_file): # Note that output rasters are written to gdb
    print('Clipping and resampling slosh file')
    paths = set_file_paths(location, slosh_file, dem_file)

    # Create new polygon with extent and coordinate system of raster

    extents = ["LEFT", "RIGHT", "TOP", "BOTTOM"]
    corners = []

    dem = paths['dem']

    for extent in extents:
        corner_tmp = arcpy.GetRasterProperties_management(dem, extent)
        corner = corner_tmp.getOutput(0)
        corners.append(corner)
        corners = [float(item) for item in corners]

    x1 = corners[0]
    x2 = corners[1]
    y1 = corners[3]
    y2 = corners[2]

    features=[]
    coord_info = [[x1,y2], [x2, y2], [x2, y1], [x1, y1]]

    for coord in coord_info:
        features.append(arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in coord_info])))

    output_clipping_polygon = paths['elevation'] + "/" + "clipping_polygon.shp"

    arcpy.CopyFeatures_management(features, output_clipping_polygon)
    print('Created clipping polygon')

    # Clip SLOSH file to polygon with raster dem extent

    output_clipped_slosh = paths['slosh'] + "/clipped_" + slosh_file

    clipped_slosh = arcpy.Clip_analysis(paths['slosh_file'], output_clipping_polygon, output_clipped_slosh)

    #return{'clipped_slosh': clipped_slosh}
    print('Clipped SLOSH file')

    # Get cell size properties for raster resampling
    cellsize_properties = ["CELLSIZEX"]
    cellsizes = []

    for cellsize_property in cellsize_properties:
        size_tmp = arcpy.GetRasterProperties_management(paths['dem'], cellsize_property)
        size = size_tmp.getOutput(0)
        cellsizes.append(size)
        cellsizes = [float(item) for item in cellsizes]
        print(cellsizes)
        #arcpy.CheckOutExtension("3D") I don't think I need this
        cellsize = cellsizes[0]

    # Convert SLOSH file to raster and set the 0 values to NoData

    field_names = [f.name for f in arcpy.ListFields(paths['slosh_file'], "*_high")]
    print(field_names)

    slosh_rasters = []
    for field in field_names:
        print(field)
        slosh_raster_0 = paths['slosh'] + "/" + field + '.tif'
        arcpy.PolygonToRaster_conversion(clipped_slosh, field, slosh_raster_0,"CELL_CENTER","NONE",cellsize)
        arcpy.env.workspace = paths['results']
        outras = field + '_null'
        arcpy.CopyRaster_management(slosh_raster_0,outras,"","","0","NONE","NONE","32_BIT_FLOAT","NONE","NONE")
        slosh_rasters.append(outras)

    return{'slosh_rasters': slosh_rasters}

# Extend surge inland using FocalStatistics. At this point, slosh_file has to be passed explicitly and outname changed appropriately each time method is run :( But it works.



def extend_surge(location,slosh_file,outname):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    gdb = str(location + '.gdb')
    arcpy.env.workspace = os.path.join(location_path, gdb)
    #slosh_path = os.path.join(location_path,'slosh')

    slosh_file = Con(IsNull(slosh_file),arcpy.sa.FocalStatistics(slosh_file, NbrCircle(100,"CELL"),"MEAN","DATA"),slosh_file)
    print(slosh_file) # This creates a tmp file within the AppData forlder. This is the file that gets fed into extend_surge below.

    any_nulls = arcpy.GetRasterProperties_management(slosh_file,"ANYNODATA")
    any_nulls_output = any_nulls.getOutput(0)
    print(any_nulls_output)

    if any_nulls_output=='1':
        print('extending surge')
        extend_surge(location,slosh_file,outname)
    else:
        print('done extending surge')
        #outname = 'c1_high_null_extended'
        slosh_file.save(outname)
        print('saved' + str(outname))

def run_array_of_locations():
    all_locations_array = [['sandy_hook', 'c1_high_null','c1_high_null_extended'],['sandy_hook', 'c2_high_null','c2_high_null_extended'],['sandy_hook', 'c3_high_null','c3_high_null_extended'],['sandy_hook', 'c4_high_null','c4_high_null_extended']] # UPDATE ARRAY!
    print('all_locations_array: ')
    print(all_locations_array)
    print('')

    for location_array in all_locations_array:

        location = location_array[0]
        filename = location_array[1]
        outname = location_array[2]

        print("location: " + location)
        print("filename: " + filename)
        print("outname: " + outname)
        print('')

        extend_surge(location, filename,outname)

# Create storm surge surfaces (edited from original so that you don't redo the interpolation
# Note that this version also doesn't use dem_ft, but just does the conversion to ft with the Raster Calculator
# This now takes the extended surge files generated in extend_surge. But the language still reflects the earlier interpolation methods (9/4/15).
def surge_surfaces(location, slosh_file, dem_file,slr_file):
    print('Creating surge surfaces')
    paths = set_file_paths(location, slosh_file, dem_file)

    slr_csv_data = os.path.join(paths['location'], "slr",slr_file)
    slr_data = genfromtxt(slr_csv_data,dtype=None,skip_header=1,delimiter=',')
    arcpy.env.workspace = paths['results']

    all_cats_interpolated = arcpy.ListRasters('c*extended') # This is where the change in file name will happen 9/2/15

    slosh_extent = os.path.join(paths['slosh'],'slosh_extent.shp')
    surfaces = []

    clipped_cats = []

    if os.path.exists(slosh_extent): # This will have to go
        print('Clipping interpolated file to slosh extent')
        for cat in all_cats_interpolated:
            fullname_cat = os.path.join(paths['slosh'],str(cat))

            output_clipped_cat = paths['slosh'] + "/clip_" + cat + '.tif'
            inRaster = fullname_cat
            inMaskData = slosh_extent

            outExtractByMask = ExtractByMask(inRaster,inMaskData)
            outExtractByMask.save(output_clipped_cat)
            clipped_cats.append(outExtractByMask)
    else:
        print('No worries...not clipping the slosh file')
        clipped_cats = all_cats_interpolated
    print(clipped_cats)


    for cat in clipped_cats: # could clean up and change 'clipped_cats' to 'all_cats_interpolated' if slosh_extent does not exist
        #fullname_cat = os.path.join(paths['slosh'],str(cat))
        #basename_cat = os.path.basename(fullname_cat)
        fullname_dem_file = os.path.join(paths['elevation'],dem_file)
        #print(fullname_cat)
        #print(basename_cat)
        print(fullname_dem_file)
        #fullname_dem_ft = os.path.join(paths['elevation'],str(dem_ft))
        #cat_name = os.path.basename(fullname)

        for row in slr_data:
            print(row)
            print('Creating surge surface for ' + str(cat) +  ' ' + str((row[0])))
            surface = Con(Raster(cat) + row[1] >= Raster(fullname_dem_file)/.3048, Raster(cat) + row[1]- Raster(fullname_dem_file)/.3048)
            #print('surface created')
            outname = (paths['results'] + str("/" + cat + "_" + str(int(row[0])) + "_" + str(row[2])+"_diff")) #Removed .tif
            print(outname)
            surface.save(outname)
            surfaces.append(surface)
            print('Created surge surface for ' + str(cat) + str(int(row[0])))

    # Create SLR surfaces

    for row in slr_data:
        print('Creating SLR surface for ' + str(int(row[0])))
        slr_surface = Con(Raster(fullname_dem_file)/.3048 <= row[1], 1)
        outname = (paths['results'] + "/slr" + str(int(row[0])) + '_' + str(row[2]) + "_diff") #Removed .tif
        slr_surface.save(outname)
        surfaces.append(slr_surface)
    print("SLR and surge surfaces created")
    return(surfaces)


# Run region group for all created surfaces

def region_group(location, slosh_file, dem_file, slr_file):
    print('Performing region grouping')
    paths = set_file_paths(location, slosh_file, dem_file)

    surfaces = surge_surfaces(location, slosh_file, dem_file, slr_file)

    inputs_to_rg = []
    region_grouped_files = []

    for surface in surfaces:
        fullname = str(surface)
        filename = os.path.basename(fullname)
        outname_1 = (paths['results'] + "/" + "all_1_" + filename)

        # Convert raster so area has value of 1

        input_to_rg = Con(Raster(fullname)>0,1)
        input_to_rg.save(outname_1)
        inputs_to_rg.append(input_to_rg)

        # Perform region group

        outRegionGrp = RegionGroup(input_to_rg, "EIGHT", "WITHIN")
        outname_rg = (paths['results'] + str("/rg_" + filename))
        outRegionGrp.save(outname_rg)
        region_grouped_files.append(outRegionGrp)

    print("Region grouping done")
    return {'inputs_to_rg': inputs_to_rg, 'region_grouped_files': region_grouped_files}

# Extract connected regions based on largest connected area from region grouping
def extract(location, slosh_file, dem_file, slr_file):
    print('Extracting region grouped files')
    inputs_and_rg_files = region_group(location,slosh_file, dem_file, slr_file)

    rg_files = inputs_and_rg_files['region_grouped_files']
    print(rg_files)

    paths = set_file_paths(location, slosh_file, dem_file)
    arcpy.env.workspace = paths['results']

    extracted_files = []
    for rg_file in rg_files:
        fullname = str(rg_file)
        #print('fullname is ' + fullname)
        filename = os.path.basename(fullname)
        #print('filename is ' + filename)
        #outname = (paths['results'] + "/" + str("extract_" + filename))
        outname = str('extract_' + filename)
        #print('outname is ' + outname)

        arr = arcpy.da.FeatureClassToNumPyArray(fullname, ('Value', 'Count'))
        count = arr['Count']
        value = arr['Value']
        index_to_extract = numpy.argmax(count)
        value_to_extract = str(value[index_to_extract])

        inSQLClause = 'Value =' + value_to_extract
        print('Extracting ' + value_to_extract + 'from ' + filename)

        attExtract = ExtractByAttributes(fullname, inSQLClause)
        attExtract.save(outname)
        extracted_files.append(attExtract)
    print('Extracted connected areas')

    return{'extracted_files': extracted_files}




# Convert to polygon (for surge area maps)
def finalize(location, slosh_file, dem_file, slr_file):
    print('Finalizing')
    print('Getting Extracts')
    extracts = extract(location, slosh_file, dem_file, slr_file)
    extracted_files = extracts['extracted_files']
    print(extracted_files)
    paths = set_file_paths(location, slosh_file, dem_file)


    final_polygons = []

    for extracted_file in extracted_files:
        fullname = str(extracted_file)
        filename = os.path.basename(fullname)
        outname = (paths['results'] + "/" + str('final_polygon_' + filename))

        extract_all_1 = Con(Raster(fullname)>0,1)

        arcpy.RasterToPolygon_conversion(str(extract_all_1), outname,"SIMPLIFY", "VALUE")
        final_polygons.append(outname)

    return(final_polygons)

# Convert to polygon (for depth maps)

def depth_maps(location, slosh_file, dem_file, slr_file): #Use this one.

    paths = set_file_paths(location, slosh_file, dem_file)
    arcpy.env.workspace = paths['results']
    print(paths['results'])

    surfaces = arcpy.ListRasters(str('c*diff'))
    print(surfaces)
    extracts = arcpy.ListRasters(str('extract*c*diff*'))
    print(extracts)
    surfaces_extracts = numpy.column_stack((surfaces, extracts))
    print(surfaces_extracts)

    depth_polygons = []
    # Mask the surge surface with the final extracted footprint
    for row in surfaces_extracts:
        inRaster = row[0]
        maskRaster = row[1]

        inRaster_fullname = str(inRaster)
        inRaster_filename = os.path.basename(inRaster_fullname)

        maskRaster_fullname = str(maskRaster)
        maskRaster_filename = os.path.basename(maskRaster_fullname)

        outname = (str('raster_for_depth_' + inRaster_filename))

        outExtractByMask = arcpy.sa.ExtractByMask(str(paths['results'] + '/' + inRaster_fullname), str(paths['results'] + '/' + maskRaster_fullname))
        outExtractByMask.save(outname)
        print('Saved' + outname)

        #Aggregate
        inRaster = outname
        print(inRaster)
        cellFactor = 6
        out_raster_name = str('agg_'+ outname)
        print(out_raster_name)

        outAgg = arcpy.sa.Aggregate(inRaster,cellFactor,'MEAN')
        outAgg.save(out_raster_name)
        print('Aggregated ' + out_raster_name)

        #Convert the raster from float to integer format
        outname_int = str('integer_'+out_raster_name)
        integer_raster = arcpy.sa.Int(outAgg*100)
        integer_raster.save(outname_int)
        print('Converted this file to integer: ' + outname_int)

        #Convert the masked file to polygon
        outname_poly = (paths['results'] + '/' + str('polygon_for_depth_' + inRaster_filename)) # Removed .replace('tif','shp')))
        print(outname_poly)
        arcpy.RasterToPolygon_conversion(outname_int,outname_poly,"SIMPLIFY", "VALUE") # Surge value in GRIDCODE field
        depth_polygons.append(outname_poly)
        print('Saved this polygon: ' + outname_poly)

    print(depth_polygons)
    return(depth_polygons)

# This method runs finalize, region group, extract, and depth_maps
def run_finalize_and_depth_maps_for_array_of_locations():
    all_locations_array = [['eglin', 'ep3mom.shp','full_mosaic_agg_setnull.tif','eglin_slr_data_ih.csv'],['eglin', 'ep3mom.shp','full_mosaic_agg_setnull.tif','eglin_slr_data_h.csv']] # UPDATE ARRAY!
    print('all_locations_array: ')
    print(all_locations_array)
    print('')

    for location_array in all_locations_array:

        location = location_array[0]
        slosh_file = location_array[1]
        dem_file = location_array[2]
        slr_file = location_array[3]

        print("location: " + location)
        print("filename: " + slosh_file)
        print("dem_file: " + dem_file)
        print("slr_file: " + slr_file)
        print('')

        finalize(location, slosh_file, dem_file, slr_file)
        depth_maps(location, slosh_file, dem_file, slr_file)
