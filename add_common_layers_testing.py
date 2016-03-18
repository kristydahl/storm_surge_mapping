__author__ = 'kristydahl'
import arcpy
import os
import glob
arcpy.env.overwriteOutput = True

def reorder_layers():

    map_file = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/map_docs/all_cats_depth_map_2050_IH_gen_lyrs_added.mxd'
    mxd = arcpy.mapping.MapDocument(map_file)
    df = arcpy.mapping.ListDataFrames(mxd,'Layers')[0]

    order_i_want = ['tl_2014_us_mil','places','roads_clipped','kings_bay_area_water']

    for idx, val in enumerate(order_i_want):
        index = idx
        print index
        if index+1 < len(order_i_want):
            for lyr in arcpy.mapping.ListLayers(mxd,"",df):
                print lyr
                if lyr.name.lower() == val:
                    refLayer = lyr
                    print('reference layer is:')
                    print(refLayer)
                    print('now the move layer would be:')
                    print order_i_want[index+1]
                if lyr.name.lower() == order_i_want[index+1]:
                    moveLayer = lyr
                    print ('move layer is: ')
                    print(moveLayer)

                # if moveLayer is None:
                #     print('No move layer')
                # if moveLayer in locals():
                #     print (moveLayer)

            arcpy.mapping.MoveLayer(df,refLayer,moveLayer,'AFTER')
            print('moved a layer')

    for lyr in arcpy.mapping.ListLayers(mxd,"",df):
        if lyr.name.lower() == arcpy.mapping.ListLayers(mxd,"",df)[-1]:#'category 5 depth':
            refLayer = lyr
            print refLayer
        if lyr.name.lower() == 'statep010':
            moveLayer = lyr
    arcpy.mapping.MoveLayer(df,refLayer,moveLayer,'AFTER')
    print('moved a layer')

    mxd.save()
    del mxd


def add_common_layers(location):

    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    folders_path = os.path.join(location_path, 'general_map_elements')
    folders = glob.glob1(folders_path,'*')

    map_path = os.path.join(location_path,'map_docs')
    maps = glob.glob1(map_path,'all_cats_depth_map_2100_IH.mxd') # Change wildcard here if only adding layers to certain mxds

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

        order_i_want = ['area_water.shp','World_Seas.shp','roads_clipped.shp','places.shp','tl_2014_us_mil.shp'] #need to change water file name to something standard

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
                            lblClass.expression = '"%s" & "<BOL>" + [name] + "</BOL>" & "%s"' %("<FNT name = 'Georgia' size = '18'>","</FNT>")
                    else:
                        lyr_to_add = arcpy.mapping.Layer(shp_with_full_path)

                if i == layer:

                    arcpy.ApplySymbologyFromLayer_management(lyr_to_add, sym_layer_with_full_path)

                    arcpy.mapping.AddLayer(df,lyr_to_add,"TOP")
                    print('Added ' + i + ' with ' + sym_layer + ' to ' + each_map)

    outmap = each_map_no_ext[0] + '_gen_lyrs_added.mxd'
    mxd.saveACopy(outmap)