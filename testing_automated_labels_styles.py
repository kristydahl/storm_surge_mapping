__author__ = 'kristydahl'

import arcpy
import os
import glob

arcpy.env.overwriteOutput = True

def depth_map(location,cats,year, projection):
    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    map_path = os.path.join(location_path,'map_docs')
    testmap = os.path.join(location_path, 'testmap_custom.mxd') # toggle portrait/landscape here
    print(testmap)

    outmap = os.path.join(map_path, 'testing_automated_styles_labels_c5_2100_h.mxd')# edited for hard file path
    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)
    print(workspace)

    arcpy.env.workspace = workspace
    mxd = arcpy.mapping.MapDocument(str(testmap))
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    #legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]

    for cat in cats:
        print(cat)
        print(year)
        print(projection)
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
            # legend.title='Depth of inundation (ft)'
            #
            # while legend.isOverflowing:
            #   legend.elementHeight = legend.elementHeight + 0.1

            arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
            print('Added layer to map')
    mxd.saveACopy(outmap)
    del mxd, lyr

# This is working. Next steps:
# 1. Read definitionQuery from txt file
# 2. Incorporate into full script
def add_common_layers():
    map_path = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/map_docs/testing_automated_styles_labels2012_ih.mxd'
    outname = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/map_docs/testing_automated_styles_labels2012_ih_added_labels.mxd'
    print(map_path)
    mxd = arcpy.mapping.MapDocument(map_path)
    df = df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
    lyr = arcpy.mapping.Layer('C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/general_map_elements/places/places.shp')
    print(lyr)
    statement_file = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/general_map_elements/places/places_def_query.txt'
    statement = open(statement_file,"r").readlines()
    print(statement[0])
    #lyr = arcpy.mapping.Layer('places_lyr')
    #lyr.name = 'test_places'
    lyr.definitionQuery = statement[0] #'"name" IN' + "('Grover Island','Kingsland','Saint Marys')"

    lyr.showLabels = True

    lyr.saveACopy('C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/general_map_elements/places/selected_places.lyr')

    #arcpy.ApplySymbologyFromLayer_management(lyr, 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/places_labels_style.lyr')
    sourceLayer = arcpy.mapping.Layer('C:/Users/kristydahl/Desktop/GIS_data/military_bases/places_labels_style.lyr')
    sourceLayer.showLabels = True
    lyr = arcpy.mapping.Layer('C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/general_map_elements/places/selected_places.lyr')
    arcpy.mapping.UpdateLayer(df,lyr,sourceLayer, True)
    arcpy.ApplySymbologyFromLayer_management(lyr, 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/places_labels_style.lyr')
    arcpy.mapping.AddLayer(df,lyr,'TOP')
    print('Added layer')


    mxd.saveACopy(outname)
    del mxd, lyr


