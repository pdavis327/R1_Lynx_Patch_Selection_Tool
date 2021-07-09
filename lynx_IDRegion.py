
import arcpy
import os

patch_dir = (r"T:\FS\NFS\R01\Program\7140Geometronics\GIS\Project\zz_Lynx_Hanvey_Dec2019\Data\Outputs_AllArea.gdb")

Administrative_Region_Boundary = (r"T:\FS\Reference\EDW\BoundaryAdmin_AdministrativeRegion_EDW.lyr")

output_dir = (r"T:\FS\NFS\R01\Program\7140Geometronics\GIS\Project\zz_Lynx_Hanvey_Dec2019\Data\Outputs_AllArea.gdb")

table_dir = (r"T:\FS\NFS\R01\Program\7140Geometronics\GIS\Project\zz_Lynx_Hanvey_Dec2019\Data\PatchOutputSpreadsheets\AllAreaSummariesforMaps")

def addAreaField(feature, fieldName):
	if arcpy.Describe(feature).shapeType == "Polygon":
		field_names = [i.name for i in arcpy.ListFields(feature)]
		if not fieldName in field_names: 
			arcpy.AddField_management(feature, fieldName, "Float")
			arcpy.CalculateField_management(feature, fieldName, "!SHAPE.area@ACRES!", "PYTHON_9.3")	
		else:
			arcpy.CalculateField_management(feature, fieldName, "!SHAPE.area@ACRES!", "PYTHON_9.3")	

walk = arcpy.da.Walk(patch_dir)
for dirpath,dirnames,filenames in walk:
	for filename in filenames:
		path = os.path.join(dirpath, filename)
		ftr_out = (output_dir + "\\" + filename + "_ID_Region")
		tbl_out = (table_dir + "\\" + filename + "_ID_Region.xls")
		arcpy.Identity_analysis(path, Administrative_Region_Boundary, ftr_out, "ALL", "", "NO_RELATIONSHIPS")
		addAreaField(ftr_out, "Acres_Calc")
		arcpy.TableToExcel_conversion(ftr_out, tbl_out)

