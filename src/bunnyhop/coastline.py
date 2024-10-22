# Download the coastline data

# Filter a version for cities and a version for countiesUnion it to the input data

from collections import defaultdict

import arcpy
import arcgis

from . import config

def coastal_cut(input_data,
                output_name,
                cities_counties,
                log,
                coastline_data=config.COASTLINE_LAYER_URL,
                exclusion_field=config.COASTLINE_EXCLUSION_FIELD,
                counties_exclude=config.COASTLINE_COUNTIES_EXCLUDE,
                cities_exclude=config.COASTLINE_CITIES_EXCLUDE,
                run_sliver_fix=config.COASTLINE_SLIVER_FIX):
    
    if cities_counties == "cities":
        exclude = cities_exclude
        coastal_layer_name = "coastal_select_cities"
    elif cities_counties == "counties":
        exclude = counties_exclude
        coastal_layer_name = "coastal_select_counties"
    else:
        raise ValueError("parameter cities_counties must be either 'cities' or 'counties'")
    
    if len(exclude) > 1:
        exclude_str = "'" + "','".join(exclude) + "'"
    else:
        exclude_str = f"'{exclude[0]}'"

    # download the coastline data
    coastal_layer = "coastal_full"
    if not arcpy.Exists(coastal_layer):
        portal = arcgis.GIS("https://arcgis.com")  # not really sure we need this
        feature_layer = arcgis.features.FeatureLayer(coastline_data)
        features = feature_layer.query()
        features.save(arcpy.env.workspace, coastal_layer)

    # now, filter the coastline data to only have the appropriate exclusion polygons
    # it's an exclude, but we need to use "in" instead of "not in" because the items to exclude are encapsulated in the polygons.
    log.debug("Selecting out coastline exclusion polygons")
    arcpy.analysis.Select(coastal_layer, coastal_layer_name, f"\"{exclusion_field}\" in ({exclude_str})")

    # run a union to the output path
    log.debug("Running coastline union")
    arcpy.analysis.Union([input_data, coastal_layer_name], output_name)

    if run_sliver_fix:
        log.debug("Fixing coastal slivers")
        fix_slivers(output_name)

def fix_slivers(input, keep_fragment_geoms=config.COASTLINE_KEEP_FRAGMENTS_IN_GEOMS, threshold=config.COASTLINE_CHECK_SIZE_THRESHOLD_METERS):
    
    polys_by_name = defaultdict(lambda: [])  # we'll index polygons by name here

    with arcpy.da.UpdateCursor(input, field_names=["SHAPE@", "LEGAL_PLACE_NAME", "OID@"]) as cursor:
        for row in cursor:  # pull them out so we we can address them by place name
            polys_by_name[row[1]].append(row)

        for place in polys_by_name:
            if len(polys_by_name[place]) < 2:
                continue  # skip any polygon that doesn't have a coastal buffer
            
            place1 = polys_by_name[place][0]
            place2 = polys_by_name[place][1]

            place1, place2 = check_parts(place1, place2, keep_fragment_geoms, threshold)
            place1, place2 = check_parts(place2, place1, keep_fragment_geoms, threshold)

            polys_by_name[place][0] = place1
            polys_by_name[place][1] = place2

    with arcpy.da.UpdateCursor(input, field_names=["SHAPE@", "LEGAL_PLACE_NAME", "OID@"]) as cursor:
        rows_by_oid = {}
        for name in polys_by_name:  # index the rows by their OID so we can easily look them up to run the update
            for row in polys_by_name[name]:
                oid = row[2]
                rows_by_oid[oid] = row

        for row in cursor:
            update_value = rows_by_oid[row[2]]
            cursor.updateRow(update_value)

def check_parts(place1, place2, keep_fragment_geoms, threshold, sr=config.COASTLINE_CHECK_SR):
    
    place1_parts = place1[0].partCount
    place2_parts = place2[0].partCount
    
    swaps = []
    for part_id in range(place1_parts):
        part_array = place1[0].getPart(part_id)  # index 0 is the geometry
        part = arcpy.Polygon(part_array, spatial_reference=sr)

        if part.area < threshold:
            skip = False  # check if it's a fragment we need to keep
            for geom in keep_fragment_geoms:
                if not part.disjoint(geom):
                    skip = True
            if skip:
                continue
        
            # OK, it's not a fragment to keep and it's small. Check if it touches any of place2's parts
            for place2_id in range(place2_parts):
                place2_part_array = place2[0].getPart(place2_id)
                place2_part = arcpy.Polygon(place2_part_array, spatial_reference=sr)
                if place2_part.area > threshold and part.touches(place2_part):
                    swaps.append(part)
                    break

    for swap in swaps:  # perform these at the end to not change the geometry while we're iterating over it
        place2[0] = place2[0].union(swap)  # add the part to the other part
        place1[0] = place1[0].difference(swap)  # remove it from this part

    return place1, place2

    # Find every polygon whose LEGAL PLACE NAME is duplicated - one will be the coastal buffer, one will be the land based items
    # For each of those polygons:
    #   for part in polygon:
    #       if part area below threshold
    #          check if it's in the keep_fragment_geoms (that it's disjoint) - if it is, then continue
    #       check if the part touches the land polygon. If so, union it there. Otherwise, if it touches the ocean polygon, union it there
