"""
    This file will do the bulk of the interesting work of conflating boundaries, normaling terms, and joining data
    Let's plan to break it up into a similar set of branches to how Liana initially designed it. Roughly
    that translates to branches for processing the BOE data itself,
    TIGER transformations
    GNIS transformations
    and CalTrans data transformation
"""

import logging

from . import config
from . import retrieve

import arcpy
import pandas



def process_gnis(local_gnis_table):
    # copy the GNIS table out of Excel in one shot - we'll get more predictable outputs
    # this way rather than trying to query/select an Excel table
    log = logging.getLogger("bunnyhop")

    log.info("Beginning GNIS processing")
    log.debug("Loading GNIS data into ArcGIS table")
    gnis_raw_input_table = "gnis_raw_input"
    arcpy.management.CopyRows(in_rows=local_gnis_table, out_table=gnis_raw_input_table)

    log.debug("Filtering GNIS data to California")
    gnis_filtered_table = "gnis_filtered"
    arcpy.analysis.TableSelect(in_table=gnis_raw_input_table, out_table=gnis_filtered_table, where_clause="state_name = 'California' And feature_class = 'Civil' And (census_class_code = 'H1' Or census_class_code = 'C1')")

    log.debug("Adding GNIS_Name field")
    arcpy.management.AddField(in_table=gnis_filtered_table, field_name="GNIS_Name", field_type="Text", field_is_nullable=True)

    calc_field_code_block = """
def split_name(classcode, name):
    if classcode=="C1":
        return name.split(" ",2)[2]
    elif classcode == "H1":
        return name.rsplit(" ",1)[0]
    else:
        return name
    """

    log.debug("Filling in GNIS_Name field")
    arcpy.management.CalculateField(in_table=gnis_filtered_table,
                                      field="GNIS_Name",
                                      expression="split_name(!census_class_code!,!feature_name!)",
                                      expression_type="PYTHON3",
                                      code_block=calc_field_code_block
                                    )
    
    log.info("GNIS processing complete")
    return gnis_filtered_table

def process_census(local_census_table):
    # copy the GNIS table out of Excel in one shot - we'll get more predictable outputs
    # this way rather than trying to query/select an Excel table

    log = logging.getLogger("bunnyhop")
    log.info("Beginning Census processing")
    log.debug("Loading Census data into ArcGIS table")
    census_input_table = "census_input"
    arcpy.management.CopyRows(in_rows=str(local_census_table), out_table=census_input_table)

    log.debug("Adding Census fields")
    arcpy.management.AddField(in_table=census_input_table, field_name="Place_Type", field_type="Text", field_is_nullable=True)
    arcpy.management.AddField(in_table=census_input_table, field_name="Place_Name", field_type="Text", field_is_nullable=True)
    arcpy.management.AddField(in_table=census_input_table, field_name="GEOID", field_type="Text", field_is_nullable=True)

    log.debug("Calculating Census Place_Type")
    arcpy.management.CalculateField(in_table=census_input_table,
                                    field="Place_Type",
                                    expression="!Area_Name!.split()[-1]",
                                    expression_type="PYTHON3")
    
    place_name_code_block = """def place_name(area, type):
    if type == "County":
        return area
    else:
        return area.rsplit(" ", 1),[0]   
    """
    
    log.debug("Calculating Census Place_Name")
    arcpy.management.CalculateField(in_table=census_input_table,
                                    field="Place_Name",
                                    expression="place_name(!Area_Name!, !Place_Type!)",
                                    expression_type="PYTHON3",
                                    code_block=place_name_code_block
                                )
    
    type_id_code_block = """def type_id(type, state, county, place):
    if type=="County":
        return state + county
    elif type == "town" or type == "city":
        return state + place
    """

    log.debug("Calculating Census GEOID")
    arcpy.management.CalculateField(in_table=census_input_table,
                                    field="GEOID",
                                    expression="type_id(!Place_Type!, !State_FIPS_Code!,!County_FIPS_Code!,!Place_FIPS_Code!)",
                                    expression_type="PYTHON3",
                                    code_block=type_id_code_block
                                )
    
    log.info("Census processing complete")

    return census_input_table


def flow(output_folder):
    
    # config flags for development
    if config.GET_GNIS:
        gnis_file_data: pandas.DataFrame = retrieve.retrieve_gnis(output_folder=output_folder)
        gnis_processed = process_gnis(str(gnis_file_data['csv']))
    
    if config.GET_CENSUS:
        census_data = retrieve.retrieve_census(output_folder=output_folder)
        census_processed = process_census(census_data)



    