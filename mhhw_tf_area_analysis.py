import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os
import os.path
import glob
import numpy
from numpy import genfromtxt
import csv

arcpy.env.overwriteOutput = True

# Editing so don't need cats or breaks; surface_type is either 'mhhw' or 'tf_extent'
def area_flooded_by_depth(location,base_name,surface_type,years,projection):
    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    analysis_folder = os.path.join(location_path,'area_analysis')

    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)

    arcpy.env.workspace = workspace
    print "Workspace is: " + gdb
    # get bases layer UPDATE TO FLEXIBLE PATH
    print "base name is: " + base_name
    bases = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/general_map_elements/bases/tl_2014_us_mil.shp'
    #bases = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/pascagoula/ingalls_area.lyr'
    #bases = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/annapolis/us_naval_academy2.shp'
    bases_layer = arcpy.MakeFeatureLayer_management(bases,'bases_layer')
    print 'Created layer for bases'
    # select base name from bases layer
    select_statement = """ "FULLNAME" = '%s' """ %base_name
    #select_statement = """ "FID" = 0 """
    arcpy.SelectLayerByAttribute_management(bases_layer,'NEW_SELECTION',select_statement)
    print 'Selected ' + base_name + ' from bases layer'

# get base area in acres
    arcpy.Statistics_analysis(bases_layer,'base_area3',[["area_acres",'SUM']]) # this outputs a table with the summary statistics.
    arr = arcpy.da.TableToNumPyArray('base_area3','Sum_area_acres')[0]
    base_area = arr[0]
    print "base area is: " + str(base_area)


    for year in years:

        csv_filename = str(location + '_' + base_name.replace(" ","_") + '_' + surface_type + '_' + projection + '_flooded_area.csv')
        csv_filename = os.path.join(analysis_folder,csv_filename)
        print(csv_filename)
        with open(csv_filename, 'wb') as csvfile:

            print 'Year is: ' + year + ' and surface type is: ' + surface_type

            flood_surface = arcpy.ListFeatureClasses('final_polygon_extract_rg_%s*%s*_%s*' %(surface_type,year,projection))# this gets the FC for the flooding surface

            print flood_surface
            flood_surface_layer = arcpy.MakeFeatureLayer_management(flood_surface[0],'Flood Surface') # this makes it a layer
            print 'Created flood surface layer'
            # Clip flood depth layer to base

            base_name_no_spaces = base_name.replace(" ","_")
            base_name_no_parentheses_1 = base_name_no_spaces.replace("(","_")
            base_name_no_parentheses_2 = base_name_no_parentheses_1.replace(")","")
            print base_name_no_parentheses_2


            outname =  'clip_' + surface_type + '_' + year + '_' + projection + '_' + 'to' + '_' + base_name_no_parentheses_2


            #outname = 'testing_filename'
            print "outname is: " + outname

            arcpy.Clip_analysis('Flood Surface',bases_layer,outname)
            print 'Clipped flood surface layer to base'

            # print outname
            #
            # what_is_outname = arcpy.ListFeatureClasses(outname)
            # print what_is_outname

            fc = arcpy.MakeFeatureLayer_management(outname,'clipped_surface_layer')
            print 'Created clipped_surface_layer'

            desc = arcpy.Describe(fc)

            print desc.dataType

            # create new Area_acres field and calculate it

            arcpy.AddField_management(fc,"Area_acres","FLOAT")
            arcpy.CalculateField_management(fc,"Area_acres","!shape.area@acres!","PYTHON_9.3")
            result = arcpy.GetCount_management(fc)


            result = int(arcpy.GetCount_management(fc).getOutput(0))

            print result

            if result == 0:
                print 'Table is empty'
                writer = csv.writer(csvfile)
                writer.writerow([location, base_name, base_area, surface_type, year, projection,0,0])
                print 'Wrote to csv'

            else:

            # get sum of all rows in Area_acres
                output_table_name = 'output_sum_area'
                print 'Output table name is: ' + output_table_name
                arcpy.Statistics_analysis(fc,output_table_name,[["Area_acres",'SUM']]) # this outputs a table with the summary statistics.
                print 'Calculated stats'


                arr = arcpy.da.TableToNumPyArray(output_table_name,'Sum_Area_acres')[0]
                print arr
                sum_area = arr[0]
                print sum_area

                writer = csv.writer(csvfile)

                writer.writerow([location, base_name, "%.2f" % base_area, surface_type, year, projection,"%.2f" % sum_area, "%.2f" %((sum_area/base_area)*100)])
                print 'Wrote to csv'

                del fc




def run_array_of_locations():
    all_locations_array = [['pascagoula','Ingalls','mhhw',['2012','2050','2070','2100'],'IH'],['pascagoula','Ingalls','mhhw',['2012','2050','2070','2100'],'H']]
# UPDATE ARRAY!
    print('all_locations_array: ')
    print(all_locations_array)
    print('')

    for location_array in all_locations_array:

        location = location_array[0]
        base_name = location_array[1]
        surface_type = location_array[2]
        years = location_array[3]
        projection = location_array[4]

        print("location: " + location)
        print("base name: " + base_name)
        print("projection " + projection)
        print('')

        area_flooded_by_depth(location, base_name, surface_type, years, projection)











__author__ = 'kristydahl'
