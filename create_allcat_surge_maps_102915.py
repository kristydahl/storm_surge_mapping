import arcpy
import os
import glob

arcpy.env.overwriteOutput = True

# all_cats_surge creates a map showing extent of all categories of storm for a given year and SLR projection
def all_cats_surge(location, year, projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)

    map_path = os.path.join(location_path,'map_docs')
    sym_layers_path = os.path.join(location_path, 'symbology_layers')
    testmap = os.path.join(location_path, 'testmap_2col_all_cats_extent.mxd') # switch to portrait/landscape if necessary
    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)

    arcpy.env.workspace = workspace

    outmap = os.path.join(map_path, 'all_cats_surge_' + year + '_' + projection + '.mxd')

    fcs = arcpy.ListFeatureClasses('final_polygon_extract_rg_c*_high_null_extended_%s_%s*' % (year,projection))
    symbology_layers = glob.glob1(sym_layers_path,'category*')
    print(fcs)
    print(symbology_layers)

    mxd = arcpy.mapping.MapDocument(testmap)
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    #legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

    for idx, val in enumerate(fcs):
        index = idx
        category = index + 1
        fc_with_full_path = os.path.join(workspace, val)
        lyr_name = 'Category ' + str(category)

        fc_lyr = arcpy.MakeFeatureLayer_management(fc_with_full_path,lyr_name)
        lyr = arcpy.mapping.Layer(lyr_name)

        sym_layer_style = symbology_layers[index]
        sym_layer_style_with_full_path = os.path.join(sym_layers_path,sym_layer_style)
        arcpy.ApplySymbologyFromLayer_management(lyr, sym_layer_style_with_full_path)


        #legend.autoAdd = True
        #legend.title='Storm Surge Extent'

        #while legend.isOverflowing:
          #legend.elementHeight = legend.elementHeight + 0.1

        arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
        print('Added styled layer to map')

    mxd.saveACopy(outmap)
    del mxd, lyr

# depth_map produces a map of the depth for each storm category for a given year and slr projection. layers need to
# be turned on/off to see a specific category of storm, as this map contains all of them.
def depth_map(location,cats,year, projection):
# Will need to check to make sure this is working since I mostly used depth_map2 for the electricity project


    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    map_path = os.path.join(location_path,'map_docs')
    print(map_path)
    testmap = os.path.join(location_path, 'testmap_2col_depth.mxd') # toggle portrait/landscape here
    print(testmap)

    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)
    print(workspace)

    outmap = os.path.join(map_path, 'all_cats_depth_map_' + year + '_' + projection + '.mxd')
    print(outmap)

    arcpy.env.workspace = workspace
    mxd = arcpy.mapping.MapDocument(str(testmap))
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    #legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

    for cat in cats:
        fcs = arcpy.ListFeatureClasses('polygon_for_depth*c%s_high*_%s_%s*' %(cat,year,projection))
        print(fcs)
        for fc in fcs:
            fc_with_full_path = os.path.join(workspace, fc)
            print(fc_with_full_path)
            lyr_name = str('Category ' + cat + ' Depth')
            raster_lyr = arcpy.MakeFeatureLayer_management(fc_with_full_path,lyr_name)
            lyr = arcpy.mapping.Layer(lyr_name)
            arcpy.ApplySymbologyFromLayer_management(lyr, 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/depth_gradations_fullrange2.lyr')

            # legend.autoAdd = True
            # legend.title='Storm Surge Depth'
            #
            # while legend.isOverflowing:
            #   legend.elementHeight = legend.elementHeight + 0.1

            arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
            print('Added layer to map')

    mxd.saveACopy(outmap)
    del mxd, lyr


# slr_map produces a map of the extent of inundation from SLR alone in all years for a given SLR projection
# Note that this does not have a map template with legend, nor has it been updated. Will do if SLR only maps deemed necessary
def slr_map(location, projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)

    map_path = os.path.join(location_path,'map_docs')

    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)
    #results_path = os.path.join(location_path, 'miami_testing.gdb')
    print(workspace)

    testmap = os.path.join(location_path, 'testmap.mxd') #toggle portrait/landscape here
    outmap_name = str('slr_extent_' + projection + '.mxd')
    outmap = os.path.join(map_path, outmap_name)

    arcpy.env.workspace = workspace

    fcs = arcpy.ListFeatureClasses('final_polygon_extract_rg_slr*_%s*' %(projection))
    print(fcs)

    sym_layers_path = os.path.join(location_path, 'symbology_layers', 'slr_only')
    sym_layers = glob.glob1(sym_layers_path,'*.lyr')

    mxd = arcpy.mapping.MapDocument(testmap)
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

    for idx,val in enumerate(fcs):
        index = idx
        fc_with_full_path = os.path.join(workspace, val) #will need to check to make sure this works--used to use results_path
        split_val = val.split('_')
        slryear = split_val[4]
        year = slryear.strip('slr')

        lyr_name = year

        fc_lyr = arcpy.MakeFeatureLayer_management(fc_with_full_path,lyr_name)
        lyr = arcpy.mapping.Layer(lyr_name)

        sym_layer_style = os.path.join(sym_layers_path, sym_layers[index])
        arcpy.ApplySymbologyFromLayer_management(lyr, sym_layer_style)

        arcpy.mapping.AddLayer(df,lyr,"BOTTOM")

        legend.autoAdd = True
        legend.title='Sea Level Rise'

        print('Added ' + year + ' to map')

    mxd.saveACopy(outmap)
    del mxd, lyr

#slr_surge_maps produces maps of present and future surge given a set of storm categories and a SLR projection
def slr_surge_maps(location,cats,projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    map_path = os.path.join(location_path,'map_docs')
    general_map_elements_path = os.path.join(location_path,'general_map_elements')


    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)

    arcpy.env.workspace = workspace

    sym_layers_path = os.path.join(location_path, 'symbology_layers', 'storm_projections')
    sym_layers = glob.glob1(sym_layers_path,'*.lyr')


    for cat in cats:
        fcs = arcpy.ListFeatureClasses('final_polygon_extract_rg_c%s_high_null_extended_*_%s*' % (cat,projection))
        print(fcs)
        testmap = os.path.join(location_path, 'testmap_2col_slr_surge.mxd') # switch portrait/landscape if necessary
        mxd = arcpy.mapping.MapDocument(testmap)
        df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
        #legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

        for idx,val in enumerate(fcs):
            index = idx
            #print(val)
            fc_with_full_path = os.path.join(workspace, val)
            #print(fc_with_full_path)
            split_val = val.split('_')
            #print(split_val)
            year = split_val[8] #Some places need 7, some need 8 depending on whether files were clipped to SLOSH extent
            print(year)
            lyr_name = year

            fc_lyr = arcpy.MakeFeatureLayer_management(fc_with_full_path,lyr_name)
            lyr = arcpy.mapping.Layer(lyr_name)

            sym_layer_style = os.path.join(sym_layers_path, sym_layers[index])
            arcpy.ApplySymbologyFromLayer_management(lyr, sym_layer_style)

            # legend.title='Storm Surge Extent'
            #
            # while legend.isOverflowing:
            #   legend.elementHeight = legend.elementHeight + 0.1

            arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
            print('Added layer to map')
            outmap = os.path.join(map_path, 'c_' + cat + '_present_future_surge_' + projection + '.mxd')

            # select_polygon = arcpy.ListFeatureClasses('final_polygon_extract_rg_*c%s_high_int_%s*' %(cat,year))
            # print(select_polygon)

        mxd.saveACopy(outmap)
        print('Map Saved')
    del mxd, lyr


def tf_map(location,projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location) #CHANGE BACK TO MILITARY BASES PATH!
    map_path = os.path.join(location_path,'map_docs')
    sym_layers_path = os.path.join(location_path, 'symbology_layers')
    gdb = str(location + '.gdb')
    results_path = os.path.join(location_path, gdb)
    arcpy.env.workspace = results_path

    testmap = os.path.join(location_path, 'testmap_2col_tidal_flooding.mxd')
    mxd = arcpy.mapping.MapDocument(testmap)
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

    outmap = os.path.join(map_path, 'tidal_flooding_surfaces_' + projection + '.mxd')

    sym_layers_path = os.path.join(location_path, 'symbology_layers', 'tf_projections')
    sym_layers = glob.glob1(sym_layers_path,'*.lyr')

    #sym_layer = os.path.join(sym_layers_path,'water_style.lyr')
    print(sym_layers)

    #shps = region_group_extract(location, dem_file, slr_file)
    shps = arcpy.ListFeatureClasses('final_polygon*tf_extent_*_%s' %(projection))
    print outmap

    for idx,val in enumerate(shps):
        shp_with_full_path = os.path.join(results_path, val)
        print(shp_with_full_path)
        lyr = arcpy.mapping.Layer(shp_with_full_path)

        sym_layer_style = os.path.join(sym_layers_path, sym_layers[idx])
        arcpy.ApplySymbologyFromLayer_management(lyr, sym_layer_style)

        arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
        print('Added ' + val + ' to map')
    mxd.saveACopy(outmap)

    del mxd, lyr

def create_depth_and_tf_maps_for_array_of_locations(place):
    all_locations_array = [[place, ['1','2','3','4'],'2012','IH'],[place, ['1','2','3','4'],'2050','IH'],[place, ['1','2','3','4'],'2050','H'],[place, ['1','2','3','4'],'2070','IH'],[place, ['1','2','3','4'],'2070','H'],[place, ['1','2','3','4'],'2100','IH'],[place, ['1','2','3','4'],'2100','H']] # UPDATE ARRAY DEPENDING ON WHETHER PLACE HAS CAT 5 STORMS

    print('all_locations_array: ')
    print(all_locations_array)
    print('')

    for location_array in all_locations_array:

        location = location_array[0]
        cats = location_array[1]
        year = location_array[2]
        projection = location_array[3]

        print("location: " + location)
        print("cats: " , cats)
        print("year: " + year)
        print("projection: " + projection)
        print('')

        depth_map(location,cats,year,projection)
        tf_map(location,projection)



def add_common_layers(location):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location) # CHANGE BACK TO MILITARY BASES PATH
    folders_path = os.path.join(location_path, 'general_map_elements')
    folders = glob.glob1(folders_path,'*')

    map_path = os.path.join(location_path,'map_docs')
    maps = glob.glob1(map_path,'*.mxd') # Change wildcard here if only adding layers to certain mxds
    print maps

    roads_path = os.path.join(folders_path,'roads')
    print roads_path
    roads_file = glob.glob1(roads_path,'roads.shp')[0]
    print roads_file
    roads_file_full_path = os.path.join(roads_path, roads_file)
    print roads_file_full_path

    # clip roads file
    print('Clipping roads file')

    clipping_polygon = location_path + "/" + "elevation/clipping_polygon.shp"
    output_clipped_roads = roads_path + '/roads_clipped.shp'
    clipped_roads = arcpy.Clip_analysis(roads_file_full_path, clipping_polygon, output_clipped_roads)


    for each_map in maps:
        map_with_full_path = os.path.join(map_path,each_map)
        mxd = arcpy.mapping.MapDocument(map_with_full_path)
        df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
        print df
        #legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]
        #legend.autoAdd = False
        each_map_no_ext = os.path.splitext(map_with_full_path)

        order_i_want = ['statesp010.shp','area_water.shp','World_Seas.shp','roads_clipped.shp','places.shp','tl_2014_us_mil.shp'] #need to change water file name to something standard
        print order_i_want
        for layer in order_i_want:
            for folder in folders:
                full_folder_path = os.path.join(folders_path,folder)
                print full_folder_path
                shp = glob.glob1(full_folder_path,'*.shp')
                print shp

                for i in shp:

                    shp_with_full_path = os.path.join(full_folder_path,i)
                    sym_layer = glob.glob1(full_folder_path,'*_style*')[0]
                    sym_layer_with_full_path = os.path.join(full_folder_path,sym_layer)

                    if i == 'roads_clipped.shp':
                        print('Found clipped roads file')
                        lyr_to_add = arcpy.mapping.Layer(output_clipped_roads)

                    elif i == 'places.shp':
                        statement_file = glob.glob1(full_folder_path,'places_def_query*')
                        print 'def query found'
                        full_statement_file_path = os.path.join(full_folder_path, statement_file[0])

                        statement = open(full_statement_file_path,"r").readlines()

                        print statement

                        full_layer_path = os.path.join(full_folder_path,i)
                        lyr = arcpy.mapping.Layer(full_layer_path)
                        lyr.definitionQuery = statement[0]

                        lyr.showLabels = True

                        outname = os.path.join(full_folder_path,'selected_places.lyr')
                        print outname

                        lyr.saveACopy(outname)

                        lyr_to_add = arcpy.mapping.Layer(outname)
                        print 'created layer of selected places'
                        for lblClass in lyr_to_add.labelClasses:
                            #lblClass.expression = '"%s" & "<BOL>" + [name] + "</BOL>" & "%s"' %("<FNT name = 'Gotham Medium' size = '8'>","</FNT>") # works
                            lblClass.expression = '"%s" + [name] + "%s"' %("<FNT name = 'Gotham Medium' size = '8'>","</FNT>") #  Edit font name and size appropriately

                    else:
                        lyr_to_add = arcpy.mapping.Layer(shp_with_full_path)

                if i == layer:

                    arcpy.ApplySymbologyFromLayer_management(lyr_to_add, sym_layer_with_full_path)

                    arcpy.mapping.AddLayer(df,lyr_to_add,"TOP")
                    print('Added ' + i + ' with ' + sym_layer + ' to ' + each_map)

        outmap = each_map_no_ext[0] + '_gen_lyrs_added.mxd'
        mxd.saveACopy(outmap)
