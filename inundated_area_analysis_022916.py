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

def area_flooded_by_depth(location,base_name,cats,years,breaks,projection):
    location_path = os.path.join('C:/Users/kristydahl/Desktop/GIS_data/military_bases',location)
    analysis_folder = os.path.join(location_path,'area_analysis')

    gdb = str(location + '.gdb')
    workspace = os.path.join(location_path,gdb)

    arcpy.env.workspace = workspace
    print "Workspace is: " + gdb
    # get bases layer UPDATE TO FLEXIBLE PATH
    print "base name is: " + base_name
    bases = 'C:/Users/kristydahl/Desktop/GIS_data/military_bases/kings_bay/general_map_elements/bases/tl_2014_us_mil.shp'
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


    for cat in cats:

        csv_filename = str(location + '_' + base_name.replace(" ","_") + '_c' + cat + '_' + projection + '_flooded_area_by_depth.csv')
        csv_filename = os.path.join(analysis_folder,csv_filename)
        print(csv_filename)

        #print 'Cat is: ' + cat

        with open(csv_filename, 'wb') as csvfile:

            #for cat in cats:
            for year in years:
                print 'Year is: ' + year + ' and Category is: ' + cat
                for idx,val in enumerate(breaks):
                    #print idx,val
                    if idx+1 < 6:
                        print 'start depth is:' + breaks[idx]
                        print 'end depth is: ' + breaks[idx+1]
                        flood_depth = arcpy.ListFeatureClasses('polygon_for_depth*c%s*%s*_%s*' %(cat,year,projection)) # this gets the FC for flood depth
                        flood_depth_layer = arcpy.MakeFeatureLayer_management(flood_depth[0],'Flood Depth') # this makes it a layer
                        print 'Created flood depth layer'
                        # Clip flood depth layer to base

                        base_name_no_spaces = base_name.replace(" ","_")
                        base_name_no_parentheses_1 = base_name_no_spaces.replace("(","_")
                        base_name_no_parentheses_2 = base_name_no_parentheses_1.replace(")","")
                        print base_name_no_parentheses_2

                        #outname =  'clip_' + 'c' + cat + '_' + year + '_' + projection + '_' + 'to' + '_' + base_name.replace(" ","_")
                        outname =  'clip_' + 'c' + cat + '_' + year + '_' + projection + '_' + 'to' + '_' + base_name_no_parentheses_2
                        #outname = 'testing_filename'
                        print "outname is: " + outname

                        arcpy.Clip_analysis('Flood Depth',bases_layer,outname)
                        print 'Clipped layer'
                        clipped_depth_layer = arcpy.MakeFeatureLayer_management(outname,'clipped_depth_layer')

                        # THIS IS WHERE IT'S FAILING. I CAN MAKE THE FEATURE IF I SPECIFY A FILENAME OUTSIDE OF THE GDB,
                        # BUT THEN IT FAILS AT THE SelectLayerByAttribute BELOW.

                        # ERRORS: ExecuteError: ERROR 000622: Failed to execute (Make Feature Layer). Parameters are not valid.
                        #ERROR 000628: Cannot set input into parameter out_layer.

                        # Select specific depth range

                        depth_selection_statement = str('"gridcode" >' + breaks[idx] + 'And' + '"gridcode" <' + breaks[idx+1])
                        depth_selection_outname = str('c' + cat + '_' + year + '_' + breaks[idx]+'_'+breaks[idx+1]+'_ft') # this creates a name for the depth selection
                        arcpy.SelectLayerByAttribute_management(clipped_depth_layer,'NEW_SELECTION',depth_selection_statement)

                        # create new Area_acres field and calculate it
                        fc = arcpy.MakeFeatureLayer_management(clipped_depth_layer)
                        arcpy.AddField_management(fc,"Area_acres","FLOAT")
                        arcpy.CalculateField_management(fc,"Area_acres","!shape.area@acres!","PYTHON_9.3")
                        result = arcpy.GetCount_management(fc)


                        result = int(arcpy.GetCount_management(fc).getOutput(0))

                        print result

                        if result == 0:
                            print 'Table is empty'
                            writer = csv.writer(csvfile)
                            writer.writerow([location, base_name, base_area, cat, year, projection, int(breaks[idx])/100, int(breaks[idx+1])/100,0,0])
                            print 'Wrote to csv'

                        else:

                        # get sum of all rows in Area_acres
                            output_table_name = 'output_sum_area_' + breaks[idx] + '_' + breaks[idx+1]
                            print 'Output table name is: ' + output_table_name
                            arcpy.Statistics_analysis(fc,output_table_name,[["Area_acres",'SUM']]) # this outputs a table with the summary statistics.
                            print 'Calculated stats'


                            arr = arcpy.da.TableToNumPyArray(output_table_name,'Sum_Area_acres')[0]
                            print arr
                            sum_area = arr[0]
                            print sum_area

                            writer = csv.writer(csvfile)

                            writer.writerow([location, base_name, base_area, cat, year, projection, int(breaks[idx])/100, int(breaks[idx+1])/100,"%.2f" % sum_area, "%.2f" %((sum_area/base_area)*100)])
                            print 'Wrote to csv'
                            arcpy.SelectLayerByAttribute_management(fc, "CLEAR_SELECTION")


def run_array_of_locations():
    all_locations_array = [['norfolk','Naval Air Station Oceana (Dam Neck Annex)',['1','2','3','4'],['2012','2050','2070','2100'],['0','500','1000','1500','2000','4000'],'H']]
# UPDATE ARRAY!
    print('all_locations_array: ')
    print(all_locations_array)
    print('')

    for location_array in all_locations_array:

        location = location_array[0]
        base_name = location_array[1]
        cats = location_array[2]
        years = location_array[3]
        breaks = location_array[4]
        projection = location_array[5]

        print("location: " + location)
        print("base name: " + base_name)
        print("projection " + projection)
        print('')

        area_flooded_by_depth(location, base_name, cats, years, breaks, projection)











