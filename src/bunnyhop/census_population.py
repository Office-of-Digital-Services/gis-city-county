"""
Retrieves census population estimates and joins them in

For now, an empty placeholder that adds the field, and that's it.
"""
import logging

from .config import FIELD_NAMES

import arcpy

log = logging.getLogger("bunnyhop")

def add_population(features):
    log.info("Adding Census Population Estimates")
    arcpy.AddField_management(features, FIELD_NAMES['population'], "LONG")