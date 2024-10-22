import pytest
import logging

import arcpy

from bunnyhop import coastline, config

logging.basicConfig()
log = logging.getLogger(__name__)

# this is just a currently valid local file - needs to be abstracted out
COUNTIES_SOURCE_DATA = r"counties_working"
CITIES_SOURCE_DATA = r"cities_dissolved"
WORKSPACE = r"C:\Users\nick.santos\AppData\Local\Temp\bunnyhop_workspace1om6mijr\bunnyhop_workspace.gdb"

def test_coastline_fixes(counties_source_data=COUNTIES_SOURCE_DATA, cities_source_data=CITIES_SOURCE_DATA, workspace=WORKSPACE):
    with arcpy.EnvManager(workspace=workspace, overwriteOutput=True):
        #coastline.coastal_cut(input_data=counties_source_data,
        #                      output_name="testing_coastal_cut_counties",
        #                      cities_counties="counties",
        #                      log=log,
        #                      run_sliver_fix=True
        #                      )
    
        coastline.coastal_cut(input_data=cities_source_data,
                              output_name="testing_coastal_cut_cities",
                              cities_counties="cities",
                              log=log,
                              run_sliver_fix=True
                              )