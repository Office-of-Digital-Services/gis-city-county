"""
    This file will do the bulk of the interesting work of conflating boundaries, normaling terms, and joining data
    Let's plan to break it up into a similar set of branches to how Liana initially designed it. Roughly
    that translates to branches for processing the BOE data itself,
    TIGER transformations
    GNIS transformations
    and CalTrans data transformation
"""

import arcpy


