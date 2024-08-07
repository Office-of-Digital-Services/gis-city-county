import logging.config
import tempfile
from typing import Optional
import pathlib
import os
import logging
from logging.config import dictConfig
from string import Template

from .config_github import *
from .logging_and_alerts import *

import arcpy

### BOE CONFIGS ###
GET_BOE = True

# BOE layer via https://gis.data.ca.gov/maps/93f73ae0070240fca9a4d3826ddb83cd/about
BOE_LAYER_URL = "https://services6.arcgis.com/snwvZ3EmaoXJiugR/arcgis/rest/services/City_and_County_Boundary_Line_Changes/FeatureServer/1"


### DLA CONFIGS ###
_current_folder = os.path.dirname(os.path.abspath(__file__))
DLA_CITIES_TABLE = os.path.join(_current_folder, "data", "DLA_CityNames.xlsx")
DLA_COUNTIES_TABLE = os.path.join(_current_folder, "data", "DLA_CountyNames.xlsx")


### GNIS CONFIGS ###

GET_GNIS = False
GNIS_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/FederalCodes/FedCodes_CA_Text.zip"
GNIS_ZIP_FILE_PATH = "Text/FederalCodes_CA.txt"  # where is the file we want to extract from the zip file?

### CENSUS CONFIGS ###

GET_CENSUS = False

# we do an iterative check for the census data (described in the code itself), starting with the current year, then going back
# to earlier years until we find a good one. What's the earliest year we should use? Set this to a year you know has good
# data with all the variables filled in.
CENSUS_EARLIEST_YEAR = 2023  # don't check any years earlier (e.g. 2022) than this. If 2023 fails for some reason, just STOP.
CENSUS_FOLDER_URL = Template("https://www2.census.gov/programs-surveys/popest/geographies/$year/")
CENSUS_FILE_URL = Template("https://www2.census.gov/programs-surveys/popest/geographies/$year/all-geocodes-v$year.xlsx")

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