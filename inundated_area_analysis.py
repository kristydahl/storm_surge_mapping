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

# function with parameters of year(s), projection, location, base name

# get bases layer

# add a field to the bases layer's attribute table

# calculate geometry--> area in acres

# select base name from bases layer

# get base area in acres

# set depth breaks [0,5,10,15,20,40]

# get array of "polygon for depth" layers. there will be one for each category of storm

# start for loop

# create csv file
# csv_filename = str(location + '_' + cat + '_' + year + '_flooded_substations_by_depth.csv')
#             csv_filename = os.path.join(location_path,csv_filename)
#
#             with open(csv_filename, 'wb') as csvfile:
#
#                 print(csvfile)

# clip "polygon for depth" to selected base name (save as a new layer? i think so)

# add field to attribute table

# calculate geometry --> area in acres

# get total inundated area (statistics of area column, SUM)

# get area of each depth category and write it to the csv along with % base affected within that depth category



for idx,val in enumerate(breaks):
                    #print idx,val
                    if idx+1 < 5:

                        flood_depth = arcpy.ListFeatureClasses('polygon_for_depth*c%s*%s*' %(cat,year))
                        flood_depth_layer = arcpy.MakeFeatureLayer_management(flood_depth[0],'Flood Depth')

                        select_statement = str('"gridcode" >' + breaks[idx] + 'And' + '"gridcode" <' + breaks[idx+1])
                        arcpy.SelectLayerByAttribute_management('Flood Depth','NEW_SELECTION', select_statement)

                        depth_selection_name = str('c' + cat + '_' + year + '_' + breaks[idx]+'_'+breaks[idx+1]+'_ft')
                        arcpy.CopyFeatures_management('Flood Depth',depth_selection_name)

                       # print('Category ' + cat + ' ' + year + ': ' + THIS MANY ACRES FLOODED in the ' + breaks[idx] + ' - ' + breaks[idx+1] + ' ft range')

                        writer = csv.writer(csvfile)
                        writer.writerow([location, cat, year, breaks[idx], breaks[idx+1], matchcount])


                    elif idx+1 == 5: #Change to elif and uncomment above when doing all depth categories...this is just for the last category

                        flood_depth = arcpy.ListFeatureClasses('polygon_for_depth*c%s*%s*' %(cat,year))
                        flood_depth_layer = arcpy.MakeFeatureLayer_management(flood_depth[0],'Flood Depth')

                        select_statement = str('"gridcode" >' + breaks[idx])
                        arcpy.SelectLayerByAttribute_management('Flood Depth','NEW_SELECTION', select_statement)

                        depth_selection_name = str('c' + cat + '_' + year + '_' + breaks[idx]+'plus_ft')
                        arcpy.CopyFeatures_management('Flood Depth',depth_selection_name)


                        print('Category ' + cat + ' ' + year + ': ' + str(matchcount) + ' flooded substations in the ' + breaks[idx] + ' plus ft range')

                        writer = csv.writer(csvfile)
                        writer.writerow([location, cat, year, breaks[idx], '+' , matchcount])









