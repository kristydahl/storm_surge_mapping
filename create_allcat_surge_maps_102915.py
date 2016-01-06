import arcpy
import os
import glob

arcpy.env.overwriteOutput = True

# all_cats_surge creates a map showing extent of all categories of storm for a given year and SLR projection
def all_cats_surge(location, year, projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)

    map_path = os.path.join(location_path,'map_docs')
    sym_layers_path = os.path.join(location_path, 'symbology_layers')
    testmap = os.path.join(location_path, 'testmap.mxd') # switch to portrait/landscape if necessary
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
    legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

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


        legend.autoAdd = True
        legend.title='Storm Surge Extent'

        while legend.isOverflowing:
          legend.elementHeight = legend.elementHeight + 0.1

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
    testmap = os.path.join(location_path, 'testmap.mxd') # toggle portrait/landscape here
    print(testmap)

    outmap = os.path.join(map_path, 'all_cats_depth_map_' + year + '_' + projection + '.mxd')
    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)
    print(workspace)

    arcpy.env.workspace = workspace
    mxd = arcpy.mapping.MapDocument(str(testmap))
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

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

            legend.autoAdd = True
            legend.title='Storm Surge Depth'

            while legend.isOverflowing:
              legend.elementHeight = legend.elementHeight + 0.1

            arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
            print('Added layer to map')

    mxd.saveACopy(outmap)
    del mxd, lyr

# depth_map2 was written for the electricity resilience maps and includes the analysis of flooded/non-flooded facilities
# def depth_map2(location,cats,year):
#
#     location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
#     general_map_elements_path = os.path.join(location_path,'general_map_elements')
#     plants_path = os.path.join(general_map_elements_path,'plants')
#     substations_path = os.path.join(general_map_elements_path,'substations')
#     map_path = os.path.join(location_path,'map_docs')
#     testmap = os.path.join(location_path, 'testmap_landscape.mxd') # toggle portrait/landscape here
#     #print(testmap)
#
#     outmap = os.path.join(map_path, 'all_cats_depth_map_' + year + '.mxd')
#     gdb = str(location + '.gdb')
#     workspace = os.path.join(location_path,gdb)
#     print(workspace)
#
#     arcpy.env.workspace = workspace
#     mxd = arcpy.mapping.MapDocument(str(testmap))
#     df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
#     legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]
#
#     for cat in cats:
#         fcs = arcpy.ListFeatureClasses('polygon_for_depth*c%s_high_null_extended_%s*' %(cat,year))
#         print(fcs)
#         for fc in fcs:
#             fc_with_full_path = os.path.join(workspace, fc)
#             #print(fc_with_full_path)
#             lyr_name = str('Category ' + cat + ' Depth')
#             raster_lyr = arcpy.MakeFeatureLayer_management(fc_with_full_path,lyr_name)
#             lyr = arcpy.mapping.Layer(lyr_name)
#
#             legend.autoAdd = True
#             legend.title='Storm Surge Depth'
#
#             while legend.isOverflowing:
#               legend.elementHeight = legend.elementHeight + 0.1
#
#             arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
#             print('Added category ' + cat + ' layer to map')
#
#         select_polygon = arcpy.ListFeatureClasses('final_polygon_extract_rg_*c%s_high_null_extended_%s*' %(cat,year))
#         print(select_polygon)
#
#         # Add Substations
#         all_substations = os.path.join(substations_path,'All_Substations.shp')
#         flooded_substations = arcpy.MakeFeatureLayer_management(all_substations,'Flooded Substations')
#         arcpy.SelectLayerByLocation_management('Flooded Substations','within',select_polygon[0])
#         matchcount = int(arcpy.GetCount_management('Flooded Substations').getOutput(0))
#
#         if matchcount == 0:
#             print('No substations in flooded area')
#         else:
#             arcpy.CopyFeatures_management('Flooded Substations',str('flooded_substations'+ '_'+ cat + '_' + year))
#             lyr_list = arcpy.ListFeatureClasses('flooded_substations_%s_%s*' %(cat,year))
#             print(lyr_list)
#             lyr_name = str(lyr_list[0])
#             print(lyr_name)
#             flooded_substations_layer = arcpy.MakeFeatureLayer_management(lyr_name,'Flooded Substations')
#             lyr = arcpy.mapping.Layer('Flooded Substations')
#             layer_style = os.path.join(substations_path,'style_flooded_substations.lyr')
#             arcpy.ApplySymbologyFromLayer_management(lyr, layer_style)
#             arcpy.mapping.AddLayer(df,lyr,"TOP")
#             print('Added flooded substations layer to map')
#
#         # Add Plants
#         all_plants = os.path.join(plants_path,'Operating_Plants.shp')
#         flooded_plants = arcpy.MakeFeatureLayer_management(all_plants,'Flooded Power Plants')
#         arcpy.SelectLayerByLocation_management('Flooded Power Plants','within',select_polygon[0])
#         matchcount = int(arcpy.GetCount_management('Flooded Power Plants').getOutput(0))
#         if matchcount == 0:
#             print('No plants in flooded area')
#         else:
#             arcpy.CopyFeatures_management('Flooded Power Plants',str('flooded_plants'+ '_'+ cat + '_' + year))
#             lyr_list = arcpy.ListFeatureClasses('flooded_plants_%s_%s*' %(cat,year))
#             lyr_name = str(lyr_list[0])
#             print(lyr_name)
#             flooded_plants_layer = arcpy.MakeFeatureLayer_management(lyr_name,'Flooded Power Plants')
#             lyr = arcpy.mapping.Layer('Flooded Power Plants')
#             layer_style = os.path.join(plants_path,'style_flooded_plants.lyr')
#             arcpy.ApplySymbologyFromLayer_management(lyr, layer_style)
#             arcpy.mapping.AddLayer(df,lyr,"TOP")
#             print('Added flooded plants layer to map')
#
#     mxd.saveACopy(outmap)
#     del mxd, lyr

# slr_map produces a map of the extent of inundation from SLR alone in all years for a given SLR projection
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

def slr_surge_maps(location,cats,projection):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    map_path = os.path.join(location_path,'map_docs')
    general_map_elements_path = os.path.join(location_path,'general_map_elements')
    plants_path = os.path.join(general_map_elements_path,'plants')
    substations_path = os.path.join(general_map_elements_path,'substations')

    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)

    arcpy.env.workspace = workspace

    sym_layers_path = os.path.join(location_path, 'symbology_layers', 'storm_projections')
    sym_layers = glob.glob1(sym_layers_path,'*.lyr')


    for cat in cats:
        fcs = arcpy.ListFeatureClasses('final_polygon_extract_rg_c%s_high_null_extended_*_%s*' % (cat,projection))
        print(fcs)
        testmap = os.path.join(location_path, 'testmap.mxd') # switch portrait/landscape if necessary
        mxd = arcpy.mapping.MapDocument(testmap)
        df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
        legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

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

            legend.title='Storm Surge Extent'

            while legend.isOverflowing:
              legend.elementHeight = legend.elementHeight + 0.1

            arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
            print('Added layer to map')
            outmap = os.path.join(map_path, 'c_' + cat + '_present_future_surge_' + projection + '.mxd')

            # select_polygon = arcpy.ListFeatureClasses('final_polygon_extract_rg_*c%s_high_int_%s*' %(cat,year))
            # print(select_polygon)

        mxd.saveACopy(outmap)
        print('Map Saved')
    del mxd, lyr



def add_common_layers(location):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    folders_path = os.path.join(location_path, 'general_map_elements')
    folders = glob.glob1(folders_path,'*')

    map_path = os.path.join(location_path,'map_docs')
    maps = glob.glob1(map_path,'all_cats_depth_map_2050_IH.mxd') # Change wildcard here if only adding layers to certain mxds

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
        legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]
        legend.autoAdd = False
        each_map_no_ext = os.path.splitext(map_with_full_path)

        order_i_want = ['kings_bay_area_water.shp','roads_clipped.shp','places.shp','tl_2014_us_mil.shp'] #need to change water file name to something standard

        for layer in order_i_want:
            for folder in folders:
                full_folder_path = os.path.join(folders_path,folder)
                shp = glob.glob1(full_folder_path,'*.shp')

                for i in shp:

                    shp_with_full_path = os.path.join(full_folder_path,i)
                    sym_layer = glob.glob1(full_folder_path,'*_style*')[0]
                    sym_layer_with_full_path = os.path.join(full_folder_path,sym_layer)

                    if i == 'roads_clipped.shp':
                        print('Found clipped roads file')
                        lyr_to_add = arcpy.mapping.Layer(output_clipped_roads)

                    elif i == 'places.shp':
                        statement_file = glob.glob1(full_folder_path,'places_def_query*')
                        full_statement_file_path = os.path.join(full_folder_path, statement_file[0])

                        statement = open(full_statement_file_path,"r").readlines()

                        full_layer_path = os.path.join(full_folder_path,i)
                        lyr = arcpy.mapping.Layer(full_layer_path)
                        lyr.definitionQuery = statement[0]

                        lyr.showLabels = True

                        outname = os.path.join(full_folder_path,'selected_places.lyr')

                        lyr_to_add = arcpy.mapping.Layer(outname)
                        for lblClass in lyr_to_add.labelClasses:
                            lblClass.expression = '"%s" & "<BOL>" + [name] + "</BOL>" & "%s"' %("<FNT name = 'Georgia' size = '16'>","</FNT>") # Edit font name and size appropriately

                    else:
                        lyr_to_add = arcpy.mapping.Layer(shp_with_full_path)

                if i == layer:

                    arcpy.ApplySymbologyFromLayer_management(lyr_to_add, sym_layer_with_full_path)

                    arcpy.mapping.AddLayer(df,lyr_to_add,"TOP")
                    print('Added ' + i + ' with ' + sym_layer + ' to ' + each_map)

    outmap = each_map_no_ext[0] + '_gen_lyrs_added.mxd'
    mxd.saveACopy(outmap)

# def add_common_layers2(location,filename): #I think this is just for the electricity resilience maps with flooded/nonflooded plants
#
#     location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/electricity_resilience_maps',location)
#     folders_path = os.path.join(location_path, 'general_map_elements')
#     folders = glob.glob1(folders_path,'*')
#
#     map_path = os.path.join(location_path,'map_docs')
#
#     maps = glob.glob1(map_path,filename) #Change wildcard here if adding layers to a subset of mxds
#
#
#     for each_map in maps:
#         map_with_full_path = os.path.join(map_path,each_map)
#         mxd = arcpy.mapping.MapDocument(map_with_full_path)
#         df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
#         legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]
#         legend.autoAdd = True
#         each_map_no_ext = os.path.splitext(map_with_full_path)
#         print(each_map_no_ext)
#
#
#         for folder in folders:
#             full_folder_path = os.path.join(folders_path,folder)
#             shp = glob.glob1(full_folder_path,'*.shp')
#
#             for i in shp:
#                 shp_with_full_path = os.path.join(full_folder_path,i)
#                 sym_layer = glob.glob1(full_folder_path,'*_style*')
#                 sym_layer_with_full_path = os.path.join(full_folder_path,sym_layer[0])
#
#                 if i == 'roads.shp':
#                     print('Clipping roads file')
#
#                     clipping_polygon = location_path + "/" + "elevation/clipping_polygon.shp"
#                     output_clipped_roads = full_folder_path + '/roads_clipped.shp'
#
#                     clipped_roads = arcpy.Clip_analysis(shp_with_full_path, clipping_polygon, output_clipped_roads)
#                     lyr_to_add = arcpy.mapping.Layer(output_clipped_roads)
#
#                 else:
#                     lyr_to_add = arcpy.mapping.Layer(shp_with_full_path)
#
#                 arcpy.ApplySymbologyFromLayer_management(lyr_to_add, sym_layer_with_full_path)
#
#                 if lyr_to_add == '*state*':
#                     legend.autoAdd = False
#                     arcpy.mapping.AddLayer(df,lyr_to_add,'BOTTOM')
#                 elif lyr_to_add == '*places*':
#                     legend.autoAdd = False
#                     arcpy.mapping.AddLayer(df,lyr_to_add,'TOP')
#
#                 elif lyr_to_add =='Operating_Plants.shp':
#                     #legend.autoAdd = True
#                     arcpy.mapping.AddLayer(df,lyr_to_add,'TOP')
#
#                 elif lyr_to_add =='All_Substations.shp':
#                     #legend.autoAdd = True
#                     arcpy.mapping.AddLayer(df,lyr_to_add,'TOP')
#                 else:
#                     legend.autoAdd = False
#                     arcpy.mapping.AddLayer(df,lyr_to_add,"TOP")
#
#                 print('Added ' + i + ' to ' + each_map)
#                 outmap = each_map_no_ext[0] + '_gen_lyrs_added.mxd'
#
#         layers = arcpy.mapping.ListLayers(mxd)
#         #print(layers)
#         for layer in layers:
#             if layer.name == 'Operating_Plants':
#                 layer.name = 'Power Plants'
#             elif layer.name == 'All_Substations':
#                 layer.name = 'Substations'
#         arcpy.RefreshTOC()
#
# ##        for lyr in legend.listLegendItemLayers():
# ##            legend.updateItem(lyr)
#         mxd.saveACopy(outmap)
#         #Will export to PNG, EPS, and AI manually so that each map has a visual check before exporting
