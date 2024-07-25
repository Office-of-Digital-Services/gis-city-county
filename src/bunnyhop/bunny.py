"""
    This file will do the bulk of the interesting work of conflating boundaries, normaling terms, and joining data
    Let's plan to break it up into a similar set of branches to how Liana initially designed it. Roughly
    that translates to branches for processing the BOE data itself,
    TIGER transformations
    GNIS transformations
    and CalTrans data transformation
"""

import tempfile
from typing import Optional
import pathlib
import os

import arcpy

IN_ARCGIS_ONLINE_NOTEBOOKS = True if os.getcwd() == "/arcgis" else False  

FOLDER_WORKSPACE: Optional[pathlib.PurePath] = None

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


def process_gnis(local_gnis_table):
    # copy the GNIS table out of Excel in one shot - we'll get more predictable outputs
    # this way rather than trying to query/select an Excel table

    gnis_raw_input_table = "gnis_raw_input"
    arcpy.management.CopyRows(in_rows=local_gnis_table, out_table=gnis_raw_input_table)

    gnis_filtered_table = "gnis_filtered"
    arcpy.analysis.TableSelect(in_table=gnis_raw_input_table, out_table=gnis_filtered_table, where_clause="state_name = 'California' And feature_class = 'Civil' And (census_class_code = 'H1' Or census_class_code = 'C1')")

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

    arcpy.management.CalculateField(in_table=gnis_filtered_table,
                                      field="GNIS_Name",
                                      expression="split_name(!census_class_code!,!feature_name!)",
                                      expression_type="PYTHON3",
                                      code_block=calc_field_code_block
                                    )
    


def run():
    folder, gdb = create_workspace()
    FOLDER_WORKSPACE = folder

    