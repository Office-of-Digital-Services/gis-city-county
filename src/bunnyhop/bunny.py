"""
    This file will do the bulk of the interesting work of conflating boundaries, normaling terms, and joining data
    Let's plan to break it up into a similar set of branches to how Liana initially designed it. Roughly
    that translates to branches for processing the BOE data itself,
    TIGER transformations
    GNIS transformations
    and CalTrans data transformation
"""

import logging
import pathlib
import os

from . import config
from . import retrieve

import arcpy
import arcgis
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


class BOERetrieve():
    """
        Retrieve and process the BOE data layer. This works differently than the others. It's
        already an ArcGIS Feature Service, and we need to do more work on it.
    
        Why is this a class when the others are just functions? Because it has more branches and more variables.
        It could get cumbersome to pass all the data around, so we'll just use instance attributes instead.
    """

    def __init__(self, source_layer=config.BOE_LAYER_URL):
        self.layer_url = source_layer

        self.boe_input_path = None

        self.cities_output_path = None
        self.counties_output_path = None
        self.merged_output_path = None

        self.census_table = None
        self.gnis_table=None
        self.dla_cities_table=None
        self.dla_counties_table=None

    def retrieve_and_process(self, census_table, gnis_table, dla_cities_table, dla_counties_table):
        self.census_table = census_table
        self.gnis_table = gnis_table
        self.dla_cities_table = dla_cities_table
        self.dla_counties_table = dla_counties_table

        self.retrieve_boe_layer()
        self.process_boe_layer()
        self.run_joins()
        self.merge()

    def retrieve_boe_layer(self):
        portal = arcgis.GIS("https://arcgis.com")  # not really sure we need this
        feature_layer = arcgis.features.FeatureLayer(config.BOE_LAYER_URL)
        features = feature_layer.query()
        features.save(arcpy.env.workspace, "boe_source_data")

        self.boe_input_path = pathlib.PurePath(arcpy.env.workspace) / "boe_source_data"

    def process_boe_layer(self, repair_geometry_first=True):
        
        # in many situations, we want to start by repairing the geometry - some of the rings may be broken
        if repair_geometry_first:
            # operates in place, so we can keep the same path
            arcpy.management.RepairGeometry(str(self.boe_input_path), delete_null=False)

        self.cities_pathway()
        self.counties_pathway()

    def cities_pathway(self):
        """
            We want multipart features - one record with possibly many polygons - for each city.
            So, we select out the cities, dissolve them, then add the county information back in.
        """
        cities_working = "cities_working"
        arcpy.analysis.Select(in_features=str(self.boe_input_path),
                                out_feature_class=cities_working,
                                where_clause="CITY <> 'Unincorporated'"
        )

        cities_dissolved = "cities_dissolved"
        arcpy.management.Dissolve(cities_working,
                                    out_feature_class=cities_dissolved,
                                    dissolve_field="CITY;COPRI",
                                    multi_part=True
        )

        # Join the county name back on
        arcpy.management.JoinField(cities_dissolved,
                                    in_field="CITY",
                                    join_table=str(self.boe_input_path),
                                    join_field="CITY",
                                    fields="COUNTY",
                                    index_join_fields="NEW_INDEXES"
        )

        arcpy.management.AddField(in_table=cities_dissolved,
                                  field_name="Place_Name",
                                  field_type="Text",
                                  field_is_nullable=True
        )

        arcpy.management.CalculateField(cities_dissolved,
                                        "Place_Name",
                                        "!CITY!")
        
        self.cities_output_path = cities_dissolved

    def counties_pathway(self):
        """
            For the counties data, we do two dissolves. The first one dissolves everything in
            the county to get the full boundary. The second one dissolves by county and COPRI
            value only on the unincorporated area's COPRI value to attach the COPRI to the full
            county itself.
        """
        counties_copri_working = "counties_copri_working"
        arcpy.analysis.Select(in_features=str(self.boe_input_path),
                                out_feature_class=counties_copri_working,
                                where_clause="CITY = 'Unincorporated'"
                            )

        counties_copri_ids = "counties_copri_ids"
        arcpy.management.Dissolve(counties_copri_working,
                                    out_feature_class=counties_copri_ids,
                                    dissolve_field="COUNTY;COPRI"
                                )
        
        counties_working = "counties_working"
        arcpy.management.Dissolve(in_features=str(self.boe_input_path),
                                    out_feature_class=counties_working,
                                    dissolve_field="COUNTY"
                                )
        
        arcpy.management.JoinField(
            in_data=counties_working,
            in_field="COUNTY",
            join_table=counties_copri_ids,
            join_field="COUNTY",
            fields="COPRI",
            index_join_fields="NEW_INDEXES"
        )
        
        arcpy.management.AddField(in_table=counties_working,
                                  field_name="Place_Name",
                                  field_type="Text",
                                  field_is_nullable=True
        )

        arcpy.management.CalculateField(counties_working,
                                        "Place_Name",
                                        "!COUNTY!")
        
        self.counties_output_path = counties_working
        
    def run_joins(self):
        """
            Joins the data to both the cities and counties layers
        """
        self._join_individual(self.cities_output_path, dla_table=self.dla_cities_table)
        self._join_individual(self.counties_output_path, dla_table=self.dla_counties_table)

    def _join_individual(self, layer, dla_table):
        """
        We do three joins of external data - this will join all three to the appropriate layer
        based on the matching fields. We could merge the data once beforehand then join these once
        but then we need to split it back out. I chose this path.
        Args:
            layer (_type_): Path to a feature class for cities or counties - it'll be either self.cities_output_path
                or self.counties_output_path
        """

        arcpy.management.JoinField(
            layer,
            in_field="Place_Name",
            join_table=self.census_table,
            join_field="Place_Name",
            fields="GEOID;Place_Type",
            index_join_fields="NEW_INDEXES"
        )

        arcpy.management.JoinField(
            layer,
            in_field="Place_Name",
            join_table=self.gnis_table,
            join_field="GNIS_Name",
            fields="feature_name",
            index_join_fields="NEW_INDEXES"
        )

        # import the DLA table to an ArcGIS table so we can use it in a join
        dla_table_name = os.path.splitext(os.path.split(dla_table)[1])[0]
        arcpy.TableToTable_conversion(dla_table, arcpy.env.workspace, dla_table_name)

        arcpy.management.JoinField(
            layer,
            in_field="Place_Name",
            join_table=dla_table_name,
            join_field="PLACE_NAME",
            fields="PLACE_ABBR;CNTY_ABBR",
            index_join_fields="NEW_INDEXES"
        )


    def merge(self):
        merged_layer = "cities_counties_merged"
        arcpy.management.Merge([self.cities_output_path, self.counties_output_path], merged_layer)

        self.merged_output_path = merged_layer



def flow(output_folder):
    log = logging.getLogger("bunnyhop")
    
    # config flags for development
    if config.GET_GNIS or config.GET_BOE:
        gnis_file_data: pandas.DataFrame = retrieve.retrieve_gnis(output_folder=output_folder)
        gnis_processed = process_gnis(str(gnis_file_data['csv']))
    
    if config.GET_CENSUS or config.GET_BOE:
        census_data = retrieve.retrieve_census(output_folder=output_folder)
        census_processed = process_census(census_data)

    if config.GET_BOE:
        boe_runner = BOERetrieve()
        boe_runner.retrieve_and_process(census_table=census_processed,
                                        gnis_table=gnis_processed,
                                        dla_cities_table=config.DLA_CITIES_TABLE,
                                        dla_counties_table=config.DLA_COUNTIES_TABLE
                                        )

        log.info(f"Finished. See merged output at {boe_runner.merged_output_path}")