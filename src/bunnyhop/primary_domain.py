"""
Retrieves city/county domain names and joins them in

For now, an empty placeholder that adds the field, and that's it.
"""
import logging

from .config import FIELD_NAMES

import arcpy

log = logging.getLogger("bunnyhop")

def add_primary_domain(features):
    log.info("Adding primary domain")
    arcpy.AddField_management(features, FIELD_NAMES['primary_domain'], "TEXT", field_length=255)