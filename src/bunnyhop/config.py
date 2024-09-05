import logging.config
import tempfile
from typing import Optional
import pathlib
import os
import logging
from logging.config import dictConfig
from string import Template

from .logging_and_alerts import *

import arcpy

_current_folder = os.path.dirname(os.path.abspath(__file__))

### DEBUG CONFIG ###
DEBUG = False  # uses local Census and FIPS data that's cached rather than retrieving it
DEBUG_CENSUS_FILE = os.path.join(_current_folder, "data", "census_FIPS.csv")
DEBUG_GNIS_FILE = os.path.join(_current_folder, "data", "gnis_raw_input_data.csv")

FILE_GITHUB_ISSUES = False

# Set REPROJECT_TO to None to disable reprojection
REPROJECT_TO = arcpy.SpatialReference(3310)
CALCULATE_AREA_IN_CRS = arcpy.SpatialReference(3310)
CALCULATE_AREA_UNITS_USER = "SqMi"  # for the field name
CALCULATE_AREA_UNITS = "SQUARE_MILES_INT"  # provided to ArcGIS - we can calculate in Miles even in a CRS that is in meters. The important point is that the CRS is equal area.

### BOE CONFIGS ###
GET_BOE = True

# BOE layer via https://gis.data.ca.gov/maps/93f73ae0070240fca9a4d3826ddb83cd/about
BOE_LAYER_URL = "https://services6.arcgis.com/snwvZ3EmaoXJiugR/arcgis/rest/services/City_and_County_Boundary_Line_Changes/FeatureServer/1"

# These adjustments are more crude replacements, but they're because of challenges created in the
# rest of the workflow that don't work well with coincident cities/counties (where they're one in the same boundary).
# It's worth just patching these values in at the end.
BOE_ADJUST = [
    {
        "where": {"PLACE_NAME": "San Francisco County"},
        "field": {"COPRI": "38000"}
    },
    {
        "where": {"PLACE_NAME": "San Francisco County"},
        "field": {"LEGAL_PLACE_NAME": "San Francisco County"}
    }
]

### DLA CONFIGS ###
DLA_CITIES_TABLE = os.path.join(_current_folder, "data", "DLA_CityNames.xlsx", "CityNames$")
DLA_COUNTIES_TABLE = os.path.join(_current_folder, "data", "DLA_CountyNames.xlsx", "CountyNames$")


### GNIS CONFIGS ###

GET_GNIS = True
GNIS_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/FederalCodes/FedCodes_CA_Text.zip"
GNIS_ZIP_FILE_PATH = "Text/FederalCodes_CA.txt"  # where is the file we want to extract from the zip file?

# These are processed at the *end* of the GNIS processing code since they make 
# changes to the GNIS_JOIN_NAME field so that it can properly get merged
# with the BOE data. They make one-off fixes to the join names for jurisdictions
# whose names don't follow certain patterns or where BOE has abbreviations, etc.
GNIS_ADJUSTMENTS = {
    # census field name
    "GNIS_JOIN_NAME": {
        "El Paso de Robles": "Paso Robles",
        "San Buenaventura": "Ventura",
        "Saint Helena": "St. Helena",
        "California City": "California"
    }
}

### CENSUS CONFIGS ###

GET_CENSUS = False

# we do an iterative check for the census data (described in the code itself), starting with the current year, then going back
# to earlier years until we find a good one. What's the earliest year we should use? Set this to a year you know has good
# data with all the variables filled in.
CENSUS_EARLIEST_YEAR = 2023  # don't check any years earlier (e.g. 2022) than this. If 2023 fails for some reason, just STOP.
CENSUS_FOLDER_URL = Template("https://www2.census.gov/programs-surveys/popest/geographies/$year/")
CENSUS_FILE_URL = Template("https://www2.census.gov/programs-surveys/popest/geographies/$year/all-geocodes-v$year.xlsx")

# these are processed at the end of retrieval of census data before the
# data really begins being processed - they're effectively treated as errors
# even though only one of them is. But they don't make it to customer-facing data
# they just help it get joined in
CENSUS_ADJUSTMENTS = {
    # census field name
    "Area_Name": {
        "La Ca±ada Flintridge city": "La Cañada Flintridge city",
        "El Paso de Robles (Paso Robles) city": "Paso Robles city",
        "San Buenaventura (Ventura) city": "Ventura city",
        "California City city": "California city"
    }
}

IN_ARCGIS_ONLINE_NOTEBOOKS = True if os.getcwd() == "/arcgis" else False  
FOLDER_WORKSPACE: Optional[pathlib.PurePath] = None
GDB_WORKSPACE: Optional[pathlib.PurePath] = None




def create_workspace():
    """
        Ensures that we have a workspace to write outputs to - sets it to both the default and scratch workspaces for everything els
        By default, creates a file geodatabase. When it detects it's in ArcGIS Online Notebooks, it places this
        geodatabase in the /arcgis/home folder. Otherwise, it generates a folder path with the tempfile package

    Returns:
        pathlib.PurePath: The full path to the file geodatabase workspace
    """
    workspace_directory: Optional[pathlib.PurePath] = None

    if IN_ARCGIS_ONLINE_NOTEBOOKS:
        workspace_directory = pathlib.PurePath(os.getcwd()) / "home" / "workspace"
    else:
        workspace_directory = pathlib.PurePath(tempfile.mkdtemp(prefix="bunnyhop_workspace"))

    gdb_name = "bunnyhop_workspace.gdb"
    gdb_path = workspace_directory / gdb_name
    arcpy.management.CreateFileGDB(str(workspace_directory), gdb_name)

    arcpy.env.workspace = str(gdb_path)
    arcpy.env.scratchWorkspace = str(gdb_path)

    return workspace_directory, gdb_path


def config_logging(config):
    # make sure the folder to the log file exists
    os.makedirs(os.path.dirname(config["handlers"]["file_logger"]["filename"]), exist_ok=True)

    dictConfig(config)
    log = logging.getLogger("bunnyhop")

    log.info("Logging configured")


def startup():
    global FOLDER_WORKSPACE, GDB_WORKSPACE, LOG_FILE_PATH, LOGGING_CONFIG

    workspace_dir, gdb_path = create_workspace()
    log_dir = workspace_dir / "logs"
    log_path = log_dir / "run_log.txt"

    FOLDER_WORKSPACE = workspace_dir
    GDB_WORKSPACE = gdb_path
    LOG_FILE_PATH = log_path
    LOGGING_CONFIG["handlers"]["file_logger"]["filename"] = str(log_path)
    
    config_logging(config=LOGGING_CONFIG)

    log = logging.getLogger("bunnyhop")
    log.info("Startup complete")
    log.debug(f"log file at {log_path}")
    log.debug(f"workspace gdb at {gdb_path}")