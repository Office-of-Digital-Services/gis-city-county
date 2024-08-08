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

    log.debug("Adding LEGAL_PLACE_NAME field")
    arcpy.management.AddField(in_table=gnis_filtered_table, field_name="LEGAL_PLACE_NAME", field_type="Text", field_is_nullable=True)
    arcpy.management.AddField(in_table=gnis_filtered_table, field_name="GNIS_JOIN_NAME", field_type="Text", field_is_nullable=True)

    calc_field_code_block = """
def split_name(classcode, name):
    if classcode=="C1":
        return name.split(" ",2)[2]
    elif classcode == "H1":
        return name
    else:
        return name
    """

    log.debug("Filling in GNIS_JOIN_NAME field")
    arcpy.management.CalculateField(in_table=gnis_filtered_table,
                                      field="GNIS_JOIN_NAME",
                                      expression="split_name(!census_class_code!,!feature_name!)",
                                      expression_type="PYTHON3",
                                      code_block=calc_field_code_block
                                    )
    
    log.debug("Filling in LEGAL_PLACE_NAME field")
    arcpy.management.CalculateField(in_table=gnis_filtered_table,
                                      field="LEGAL_PLACE_NAME",
                                      expression="!feature_name!",
                                      expression_type="PYTHON3",
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
    arcpy.management.AddField(in_table=census_input_table, field_name="PLACE_TYPE", field_type="Text", field_is_nullable=True)
    arcpy.management.AddField(in_table=census_input_table, field_name="PLACE_NAME", field_type="Text", field_is_nullable=True)
    arcpy.management.AddField(in_table=census_input_table, field_name="GEOID", field_type="Text", field_is_nullable=True)

    log.debug("Calculating Census Place_Type")
    arcpy.management.CalculateField(in_table=census_input_table,
                                    field="PLACE_TYPE",
                                    expression="!Area_Name!.split()[-1].capitalize()",
                                    expression_type="PYTHON3")
    
    place_name_code_block = """def place_name(area, type):
    if type == "County":
        return area
    else:
        return area.rsplit(" ", 1)[0]   
    """
    
    log.debug("Calculating Census Place_Name")
    arcpy.management.CalculateField(in_table=census_input_table,
                                    field="PLACE_NAME",
                                    expression="place_name(!Area_Name!, !PLACE_TYPE!)",
                                    expression_type="PYTHON3",
                                    code_block=place_name_code_block
                                )
    
    type_id_code_block = """def type_id(type, state, county, place):
    if type=="County":
        return f"{state:02}{county:03}"
    elif type == "Town" or type == "City":
        return f"{state:02}{place:05}"
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
        self.log = logging.getLogger("bunnyhop")

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

        self.log.info("Beginning BOE Layer processing")
        self.retrieve_boe_layer()
        self.process_boe_layer()
        self.run_joins()
        self.merge()

    def retrieve_boe_layer(self):
        self.log.debug("Retrieving BOE Layer")
        portal = arcgis.GIS("https://arcgis.com")  # not really sure we need this
        feature_layer = arcgis.features.FeatureLayer(config.BOE_LAYER_URL)
        features = feature_layer.query()
        features.save(arcpy.env.workspace, "boe_source_data")

        self.log.debug("BOE Layer Retrieved")
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
        self.log.info("Beginning processing cities")
        self.log.debug("Selecting out cities")
        cities_working = "cities_working"
        arcpy.analysis.Select(in_features=str(self.boe_input_path),
                                out_feature_class=cities_working,
                                where_clause="CITY <> 'Unincorporated'"
        )

        self.log.debug("Dissolving cities")
        cities_dissolved = "cities_dissolved"
        arcpy.management.Dissolve(cities_working,
                                    out_feature_class=cities_dissolved,
                                    dissolve_field="CITY;COPRI",
                                    multi_part=True
        )

        # Join the county name back on
        self.log.debug("Attaching county name to cities")
        arcpy.management.JoinField(cities_dissolved,
                                    in_field="CITY",
                                    join_table=str(self.boe_input_path),
                                    join_field="CITY",
                                    fields="COUNTY",
                                    index_join_fields="NEW_INDEXES"
        )

        self.log.debug("Adding PLACE_NAME field")
        arcpy.management.AddField(in_table=cities_dissolved,
                                  field_name="PLACE_NAME",
                                  field_type="Text",
                                  field_is_nullable=True
        )

        self.log.debug("Calculating PLACE_NAME field")
        arcpy.management.CalculateField(cities_dissolved,
                                        "PLACE_NAME",
                                        "!CITY!")
        
        self.cities_output_path = cities_dissolved

    def counties_pathway(self):
        """
            For the counties data, we do two dissolves. The first one dissolves everything in
            the county to get the full boundary. The second one dissolves by county and COPRI
            value only on the unincorporated area's COPRI value to attach the COPRI to the full
            county itself.
        """
        self.log.debug("Starting Counties processing")

        self.log.debug("Selecting out counties")
        counties_copri_working = "counties_copri_working"
        arcpy.analysis.Select(in_features=str(self.boe_input_path),
                                out_feature_class=counties_copri_working,
                                where_clause="CITY = 'Unincorporated'"
                            )
        
        self.log.debug("Dissolving counties to get COPRI IDs")
        counties_copri_ids = "counties_copri_ids"
        arcpy.management.Dissolve(counties_copri_working,
                                    out_feature_class=counties_copri_ids,
                                    dissolve_field="COUNTY;COPRI"
                                )
        
        self.log.debug("Dissolving counties to get full boundary")
        counties_working = "counties_working"
        arcpy.management.Dissolve(in_features=str(self.boe_input_path),
                                    out_feature_class=counties_working,
                                    dissolve_field="COUNTY"
                                )
        
        self.log.debug("Attaching county COPRI IDs")
        arcpy.management.JoinField(
            in_data=counties_working,
            in_field="COUNTY",
            join_table=counties_copri_ids,
            join_field="COUNTY",
            fields="COPRI",
            index_join_fields="NEW_INDEXES"
        )
        
        self.log.debug("Adding PLACE_NAME field to county")
        arcpy.management.AddField(in_table=counties_working,
                                  field_name="PLACE_NAME",
                                  field_type="Text",
                                  field_is_nullable=True
        )

        self.log.debug("Calculating County PLACE_NAME field")
        arcpy.management.CalculateField(counties_working,
                                        "PLACE_NAME",
                                        "!COUNTY!")
        
        self.counties_output_path = counties_working
        
    def run_joins(self):
        """
            Joins the data to both the cities and counties layers
        """
        self.log.debug("Merging DLA Tables")
        arcpy.Merge_management([self.dla_cities_table, self.dla_counties_table], "dla_merged")

        self._join_individual(self.cities_output_path, dla_table="dla_merged")
        self._join_individual(self.counties_output_path, dla_table="dla_merged")

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
            in_field="PLACE_NAME",
            join_table=self.census_table,
            join_field="PLACE_NAME",
            fields="GEOID;PLACE_TYPE",
            index_join_fields="NEW_INDEXES"
        )

        arcpy.management.JoinField(
            layer,
            in_field="PLACE_NAME",
            join_table=self.gnis_table,
            join_field="GNIS_JOIN_NAME",
            fields="LEGAL_PLACE_NAME",
            index_join_fields="NEW_INDEXES"
        )

        # import the DLA table to an ArcGIS table so we can use it in a join
        #dla_table_name = os.path.splitext(os.path.split(dla_table)[1])[0]
        #arcpy.CopyRows_management(dla_table, dla_table_name)

        arcpy.management.JoinField(
            layer,
            in_field="Place_Name",
            join_table=dla_table,
            join_field="PLACE_NAME",
            fields="PLACE_ABBR;CNTY_ABBR",
            index_join_fields="NEW_INDEXES"
        )


    def merge(self):
        merged_layer = "cities_counties_merged"
        arcpy.management.Merge([self.counties_output_path, self.cities_output_path], merged_layer)

        self.merged_output_path = merged_layer



def flow(output_folder):
    log = logging.getLogger("bunnyhop")
    
    # config flags for development
    if config.GET_GNIS or config.GET_BOE:
        if not config.DEBUG:
            gnis_file_data: pandas.DataFrame = retrieve.retrieve_gnis(output_folder=output_folder)
        else:
            log.warning("Using DEBUG GNIS file.")
            gnis_file_data = {'csv': config.DEBUG_GNIS_FILE}

        gnis_processed = process_gnis(str(gnis_file_data['csv']))
    
    if config.GET_CENSUS or config.GET_BOE:
        if not config.DEBUG:
            census_data = retrieve.retrieve_census(output_folder=output_folder)
        else:
            log.warning("Using DEBUG Census file.")
            census_data = config.DEBUG_CENSUS_FILE
        census_processed = process_census(census_data)

    if config.GET_BOE:
        boe_runner = BOERetrieve()
        boe_runner.retrieve_and_process(census_table=census_processed,
                                        gnis_table=gnis_processed,
                                        dla_cities_table=config.DLA_CITIES_TABLE,
                                        dla_counties_table=config.DLA_COUNTIES_TABLE
                                        )

        log.info(f"Finished. See merged output at {os.path.join(arcpy.env.workspace, boe_runner.merged_output_path)}")