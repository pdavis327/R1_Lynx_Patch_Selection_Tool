import arcpy
import os
from arcpy import env
from arcpy.sa import *


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "Lynx Patch Selection"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [Lynx_Patch_Selection]


class Lynx_Patch_Selection(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Lynx Patch Selection"
		self.description = "This tool selects continuous raster areas greater than or equal to a user defined agreage based on a habitat suitability raster class. The selection is exported to a new polygon file, and each feature is attributed with the proportion and area of a high suitability raster. Optionally, if there are donut holes in the polygons, acreage of another raster can be computed within those areas for each polygon."
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		param0 = arcpy.Parameter(
		    displayName="Patch Acreage",
		    name="acreage",
		    datatype= "GPLong",
		    parameterType="Required",
		    direction="Input")

		param1 = arcpy.Parameter(
		    displayName="Patch Raster",
		    name="Mod_Ras_1",
		    datatype= "GPRasterLayer",
		    parameterType="Required",
		    direction="Input")

		param2 = arcpy.Parameter(
		    displayName="Patch Raster Class Value",
		    name="Mod_Ras_1_Val",
		    datatype= "GPLong",
		    parameterType="Required",
		    direction="Input")
		
		param3 = arcpy.Parameter(
		    displayName="Buffer Patch",
		    name="opt_buffer",
		    datatype= "GPBoolean",
		    parameterType="Optional",
		    direction="Input")
		
		param4 = arcpy.Parameter(
		    displayName="Buffer Distance",
		    name="buff_dis",
		    datatype= "GPLong",
		    parameterType="Optional",
		    direction="Input")		

		param5 = arcpy.Parameter(
		    displayName="High Suitability Raster",
		    name="Mod_Ras_2",
		    datatype="GPRasterLayer",
		    parameterType="Required",
		    direction="Input")

		param6 = arcpy.Parameter(
		    displayName="High Raster Class Value",
		    name="Mod_Ras_2_Val",
		    datatype= "GPLong",
		    parameterType="Required",
		    direction="Input")

		param7 = arcpy.Parameter(
		    displayName="Low Suitability Raster",
		    name="Low_Ras_3",
		    datatype="GPRasterLayer",
		    parameterType="Optional",
		    direction="Input")

		param8 = arcpy.Parameter(
		    displayName="Low Raster Class Value",
		    name="Low_Ras_3_Val",
		    datatype= "GPLong",
		    parameterType="Optional",
		    direction="Input")		

		param9 = arcpy.Parameter(
		    displayName="Donut Raster",
		    name="Donut_1",
		    datatype="GPRasterLayer",
		    parameterType="Optional",
		    direction="Input")

		param10 = arcpy.Parameter(
		    displayName="Donut Raster Class Value",
		    name="Donut_1_Val",
		    datatype= "GPLong",
		    parameterType="Optional",
		    direction="Input")

		param11 = arcpy.Parameter(
		    displayName="Output Feature",
		    name="output_feature",
		    datatype="GPLayer",
		    parameterType="Required",
		    direction="Output")
		
		params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		if parameters[3].value:  # check that parameter has a value
			parameters[4].enabled = True
			
		else:
			parameters[4].enabled = False		

		if parameters[3].value:  # check that parameter has a value
			parameters[7].enabled = True

		else:
			parameters[7].enabled = False
		
		if parameters[7].value:  # check that parameter has a value
			parameters[8].enabled = True
			
		else:
			parameters[8].enabled = False		
	
		if not parameters[3].value:  # check that parameter has a value
			parameters[8].enabled = False		
	
		if parameters[9].value:  # check that parameter has a value
			parameters[10].enabled = True
			
		else:
			parameters[10].enabled = False		
			
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""

	def execute(self, parameters, messages):
		
		acreage = parameters[0].value
		
		Mod_Ras_1 = parameters[1].valueAsText
		
		Mod_Ras_1_Val = parameters[2].value
		
		opt_buffer = parameters[3].valueAsText
		
		buff_dis = parameters[4].value	
		
		High_Ras_2 = parameters[5].valueAsText
		
		High_Ras_2_Val = parameters[6].value
		
		Low_Ras_3 = parameters[7].valueAsText
		
		Low_Ras_3_Val = parameters[8].value		
		
		Donut_1 = parameters[9].valueAsText
		
		Donut_1_Val = parameters[10].value
		
		output_feature = parameters[11].valueAsText
		
		#add field function
		def addField(feature, fieldName, fType):
			field_names = [i.name for i in arcpy.ListFields(feature)]
	
			if not fieldName in field_names: 
				arcpy.AddField_management(feature, fieldName, fType)		
	
		#Populate area new feature class
		def addAreaField(feature, fieldName):
			if arcpy.Describe(feature).shapeType == "Polygon":
				field_names = [i.name for i in arcpy.ListFields(feature)]
	
				if not fieldName in field_names: 
					arcpy.AddField_management(feature, fieldName, "Float")
					arcpy.CalculateField_management(feature, fieldName, "!SHAPE.area@ACRES!", "PYTHON_9.3")	
				else:
					arcpy.CalculateField_management(feature, fieldName, "!SHAPE.area@ACRES!", "PYTHON_9.3")	
		
		if opt_buffer:
			if not buff_dis:
				arcpy.AddError('\n**Buffer distance not entered!**\n')	
				return

		if Low_Ras_3:
			if not Low_Ras_3_Val:
				arcpy.AddError('\n**Low Raster Class Value not entered!**\n')	
				return		

		if Donut_1:
			if not Donut_1_Val:
				arcpy.AddError('\n**Donut 1 Class Value not entered!**\n')	
				return
		
		#Select raster value from mod input at or above the input Mod Ras Value
		Mod_Ras_1 = Raster(Mod_Ras_1)
		Mod_Ras_1_sel = Con(Mod_Ras_1 >= Mod_Ras_1_Val, Mod_Ras_1_Val)
		
		#Convert to Poly
		Mod_Ras_1_sel_poly = arcpy.RasterToPolygon_conversion(Mod_Ras_1_sel, r"in_memory\rasToPoly", "NO_SIMPLIFY", "Value")
		
		#make temp feat		
		Mod_temp = arcpy.MakeFeatureLayer_management(Mod_Ras_1_sel_poly, "Mod_temp")		
		
		#Isolate donut holes
		if (str(opt_buffer) == "true") or Donut_1:
			# Eliminate and Erase to get donuts
			perc = 99.999999
			Mod_elim = arcpy.EliminatePolygonPart_management(Mod_temp, r"in_memory\Mod_elim", 'PERCENT' , "", perc)
			Donuts = arcpy.Erase_analysis(Mod_elim, Mod_temp, r"in_memory\Donuts")			
				
		#optional Buffer
		if str(opt_buffer) == "true":
			arcpy.AddMessage("\nBuffering patch.")
			Mod_temp_buff = arcpy.Buffer_analysis(Mod_temp, r"in_memory\Mod_temp_buff", buff_dis, "", "", "ALL")
			Mod_temp_buff = arcpy.MultipartToSinglepart_management(Mod_temp_buff, r"in_memory\rasToPoly_buff_sing")
			Mod_temp = arcpy.Erase_analysis(Mod_temp_buff, Donuts, r"in_memory\Mod_buff_elim_erase")
			addField(Mod_temp, "ID", "SHORT")
			
			rec = 0
			with arcpy.da.UpdateCursor(Mod_temp, "ID") as cursor:
				for row in cursor:
					if row[0] == 0:
						rec = 1
					else:
						rec +=1
					row[0] = rec
					cursor.updateRow(row)
			del cursor	
		
		addAreaField(Mod_temp, "Mod_Acres")
		
		Mod_temp = arcpy.MakeFeatureLayer_management(Mod_temp, "Mod_temp2")
		
		#Select polygons greater than 20k-acres
		arcpy.AddMessage("\nSelecting patches >= {}-acres in {} class {}.\n".format(acreage, Mod_Ras_1, Mod_Ras_1_Val))
		arcpy.SelectLayerByAttribute_management(Mod_temp, "", ' "Mod_Acres" >= {} '.format(acreage))
		arcpy.CopyFeatures_management(Mod_temp, output_feature + "orig_poly_buffed")

		#Select raster value from high input at input High Ras Value
		High_Ras_2 = Raster(High_Ras_2)
		High_Ras_2_sel = Con(High_Ras_2 == High_Ras_2_Val, High_Ras_2_Val)	
		
		#Convert high ras to Poly
		High_Ras_2_sel_poly = arcpy.RasterToPolygon_conversion(High_Ras_2_sel, r"in_memory\highRasToPoly", "NO_SIMPLIFY", "Value")
		
		#Clip to patch raster to only get area within patch raster
		High_Ras_2_sel_poly = arcpy.Clip_analysis(High_Ras_2_sel_poly, Mod_temp, r"in_memory\High_Ras_2_sel_poly_clip")
		High_Ras_2_sel_poly = arcpy.MultipartToSinglepart_management(High_Ras_2_sel_poly, r"in_memory\High_Ras_2_sel_poly_clip_sing")
		
		addAreaField(High_Ras_2_sel_poly, "High_Acres")
		arcpy.CopyFeatures_management(High_Ras_2_sel_poly, output_feature + "High_clipped")
		
		#Run identity between layers
		arcpy.AddMessage("Identifying suitability areas and computing percent and area within selected patches.\n")
		identFeat = arcpy.Identity_analysis (Mod_temp, High_Ras_2_sel_poly, r"in_memory\identFeat")

		#Compute high stats from identity output
		identFeat_stats = arcpy.Statistics_analysis(identFeat, r"in_memory\identFeat_stats", 'Mod_Acres MEAN;High_Acres SUM', 'ID')		
		
		addField(identFeat_stats, "High_Acres", "Float")
		addField(identFeat_stats, "High_Perc", "Float")	
		
		arcpy.CalculateField_management(identFeat_stats, 'High_Acres', '[SUM_HIGH_ACRES]', 'VB')
		arcpy.CalculateField_management(identFeat_stats, 'HIGH_PERC', '[HIGH_ACRES]/ [MEAN_MOD_ACRES]', 'VB')		
		
		arcpy.CopyFeatures_management(identFeat, output_feature + "High_identfeat")
		
		if Low_Ras_3:
			#Select raster value from low input at input low Ras Value
			Low_Ras_3 = Raster(Low_Ras_3)
			Low_Ras_3_sel = Con(Low_Ras_3 == Low_Ras_3_Val, Low_Ras_3_Val)	
			
			#Convert low ras to Poly
			Low_Ras_3_sel_poly = arcpy.RasterToPolygon_conversion(Low_Ras_3_sel, r"in_memory\LowRasToPoly", "NO_SIMPLIFY", "Value")
			
			#Clip to patch raster to only get area within patch raster
			Low_Ras_3_sel_poly = arcpy.Clip_analysis(Low_Ras_3_sel_poly, Mod_temp, r"in_memory\Low_Ras_3_sel_poly_clip")			
			Low_Ras_3_sel_poly = arcpy.MultipartToSinglepart_management(Low_Ras_3_sel_poly, r"Low_Ras_3_sel_poly_clip_sing")
			addAreaField(Low_Ras_3_sel_poly, "Low_Acres")
			arcpy.CopyFeatures_management(Low_Ras_3_sel_poly, output_feature + "Low_clipped")
			
			#Run identity between layers				
			identFeat2 = arcpy.Identity_analysis (Mod_temp, Low_Ras_3_sel_poly, r"in_memory\identFeat2")				
			arcpy.CopyFeatures_management(identFeat2, output_feature + "Low_identfeat")
			
			#Compute high and low stats from identity output 
			identFeat2_stats = arcpy.Statistics_analysis(identFeat2, r"in_memory\identFeat_stats2", 'Mod_Acres MEAN;Low_Acres SUM', 'ID')	
			
			#add area fields and percent fields & compute
			addField(identFeat2_stats, "Low_Acres", "Float")
			addField(identFeat2_stats, "Low_Perc", "Float")
			arcpy.CalculateField_management(identFeat2_stats, 'Low_Acres', '[SUM_Low_ACRES]', 'VB')
			arcpy.CalculateField_management(identFeat2_stats, 'LOW_PERC', '[LOW_ACRES]/ [MEAN_MOD_ACRES]', 'VB')
		
			#perform join
			arcpy.JoinField_management(Mod_temp, "ID", identFeat_stats, "ID", ["High_Acres", "High_Perc"])
			arcpy.JoinField_management(Mod_temp, "ID", identFeat2_stats, "ID", ["Low_Acres", "Low_Perc"])
			arcpy.DeleteField_management(Mod_temp, "ORIG_FID")			
		
		else:	
			arcpy.JoinField_management(Mod_temp, "ID", identFeat_stats, "ID", ["High_Acres", "High_Perc"])

		#Compute low probability area within donut holes for each polygon >= acreage
		#Check if optional param used
		if Donut_1:
			arcpy.AddMessage("Computing area of {} within donut holes for each patch >= {}-acres.\n".format(Donut_1, acreage))

			#Convert low ras to Poly
			Donut_1 = Raster(Donut_1)
			Donut_1_sel = Con(Donut_1 == Donut_1_Val, Donut_1_Val)		
			Donut_1_sel_poly = arcpy.RasterToPolygon_conversion(Donut_1_sel, r"in_memory\Donut_1_sel_poly", "NO_SIMPLIFY", "Value")
			arcpy.CopyFeatures_management(Donut_1_sel_poly, output_feature + "_DonutsRaster")
			clipped = arcpy.Clip_analysis(Donut_1_sel_poly, Donuts, r"in_memory\clipped")
			arcpy.CopyFeatures_management(clipped, output_feature + "_Donuts")
			#Compute area
			addAreaField(clipped, "Donut_Acres_sum")			
			
			#Elim for intersect
			perc = 99.999999
			Don_elim = arcpy.EliminatePolygonPart_management(Mod_temp, r"in_memory\Modtemp_elim", 'PERCENT' , "", perc)			
			
			#run identity
			identFeat = arcpy.Identity_analysis (Don_elim, clipped, r"in_memory\donutIdent")
			arcpy.CopyFeatures_management(identFeat, output_feature + "_donutsIdentity")
			#compute sum of low acres for each ID
			Donut1_stats = arcpy.Statistics_analysis(identFeat, r"in_memory\Donut1_stats", 'Donut_Acres_sum SUM', 'Id')	
			
			#add field for low acres in stats
			addField(Donut1_stats, "Donut_Acres", "Float")			
			
			arcpy.CalculateField_management(Donut1_stats, 'Donut_Acres', '[SUM_Donut_Acres_sum]', 'VB')	
			lc = r"T:\FS\NFS\R01\Program\7140Geometronics\GIS\Project\zz_Lynx_Hanvey_Dec2019\Workspace\Davis\intermediate_files"
			arcpy.TableToTable_conversion(Donut1_stats, lc, "Donut1_Stats")
			
			#join table to feature
			arcpy.JoinField_management(Mod_temp, "Id", Donut1_stats, "Id", ["Donut_Acres"])
			
			#Copy to new feature
			arcpy.CopyFeatures_management(Mod_temp, output_feature)

		else:
			#Copy to new feature
			arcpy.CopyFeatures_management(Mod_temp, output_feature)
		return
	
	

