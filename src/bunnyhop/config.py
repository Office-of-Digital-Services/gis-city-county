import tempfile
from typing import Optional
import pathlib
import os
from config_github import *
import logging

GNIS_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/FederalCodes/FedCodes_CA_Text.zip"
GNIS_ZIP_FILE_PATH = "Text/FederalCodes_CA.txt"  # where is the file we want to extract from the zip file?

### CENSUS CONFIGS ###

# we do an iterative check for the census data (described in the code itself), starting with the current year, then going back
# to earlier years until we find a good one. What's the earliest year we should use? Set this to a year you know has good
# data with all the variables filled in.
CENSUS_EARLIEST_YEAR = 2023  # don't check any years earlier (e.g. 2022) than this. If 2023 fails for some reason, just STOP.

IN_ARCGIS_ONLINE_NOTEBOOKS = True if os.getcwd() == "/arcgis" else False  
FOLDER_WORKSPACE: Optional[pathlib.PurePath] = None
GDB_WORKSPACE: Optional[pathlib.PurePath] = None


LOG_FILE_PATH = "logs/run_log.txt"  # we'll overwrite this at runtime, most likely
LOGGING_CONFIG = {
    "formatters":{
        "default":{
            "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers":{
        "console":{
            "class": logging.StreamHandler,
            "level": logging.DEBUG,
            "stream": "ext://sys.stdout",
            "formatter": "default"
        },
        "file":{
            "class": logging.handlers.RotatingFileHandler,
            "filename": LOG_FILE_PATH,  # we'll overwrite this at runtime, most likely
            "maxBytes": 4096,
            "formatter": "default"
        }
    },
    "loggers":{
        "bunnyhop": {
            "handlers": ["console", "file"]
        }
    }

}



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


def config_logging():
    logging.config.dictConfig(LOGGING_CONFIG)


def startup():
    global FOLDER_WORKSPACE, GDB_WORKSPACE, LOG_FILE_PATH, LOGGING_CONFIG

    workspace_dir, gdb_path = create_workspace()
    log_dir = workspace_dir / "logs"
    log_path = log_dir / "run_log.txt"

    FOLDER_WORKSPACE = workspace_dir
    GDB_WORKSPACE = gdb_path
    LOG_FILE_PATH = log_path
    LOGGING_CONFIG["handlers"]["file"]["filename"] = log_path

    config_logging()