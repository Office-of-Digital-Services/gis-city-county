"""
    @author: Nick Santos
    @date: 11/5/2024
    Usage:
        For updating the human-readable (*not* the machine readable) metadata on the service endpoints for city county. These don't synchronize with
        the metadata in ArcGIS online, so we need a way to update the information so it all stays roughly in sync. There are 6 places that human-readable metadata
        needs to be updated:

            1. Backing Service Main (handled here)
            2. Backing Service Individual Layers (handled here)
            3. View Main (handled here)
            4. View Layers (happens after a Swap Source in AGOL - takes info from item 2)
            5. Backing Service ArcGIS Online standard metadata - syncs to service structured metadata. (Human entry)
            6. View ArcGIS Online standard metadata (Human entry)

        This script handles the first three items, which are otherwise very cumbersome. At some point, we'll want to have a unified interface that keeps these all in sync. But we don't right now.

        To update the human readable service endpoint metadata, update two items:
        
            1. Below, there are three items for the short service description on the main service page. These vary by type of City/County service, so they can say slightly different things. Make any changes you need there.
            2. In this same folder is a file _metadata.py that has the full HTML-laden human-readable metadata to put on the main service and layers. Make updates within that file, taking care to escape quotes,
                to update those portions of the metadata.
"""


from _metadata import METADATA

import arcgis
import json

# layer IDs and also type keys

from _services import CITIES, COUNTIES, OVERLAPPING, BACKING_ITEM_IDS, VIEW_IDS

SERVICE_DESCRIPTIONS = {}
SERVICE_DESCRIPTIONS[CITIES] = "PRE-RELEASE: City boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA). The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities are derived from Caltrans Division of Local Assistance (DLA) and are now managed by CDT. Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, the coastline is used to separate coastal buffers from the land-based portions of jurisdictions. This feature layer is for public use."
SERVICE_DESCRIPTIONS[COUNTIES] = "PRE-RELEASE: County boundaries boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA), altered to show the counties as one polygon. The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities are derived from Caltrans Division of Local Assistance (DLA) and are now managed by CDT. Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, the coastline is used to separate coastal buffers from the land-based portions of jurisdictions. This feature layer is for public use."
SERVICE_DESCRIPTIONS[OVERLAPPING] = "PRE-RELEASE: County and incorporated place (city) boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA), altered to show the counties as one polygon. This layer displays the city polygons on top of the County polygons so the area isn't interrupted. The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities are derived from Caltrans Division of Local Assistance (DLA) and are now managed by CDT. Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, the coastline is used to separate coastal buffers from the land-based portions of jurisdictions. This feature layer is for public use."

def update_service_metadata(service_url, session, service_description, metadata):
    # we want to update only a few values. We have to null out lastEditDate or the server will reject the change
    update = {"serviceDescription":service_description, "description": metadata, "editingInfo":{"lastEditDate": None}}
    update_str = json.dumps(update)  # dump it as a json string - arcgis.session.post won't do that for us

    # transform the URL to the admin URL that we can use to update the service definition
    update_url = service_url.replace("rest/services", "rest/admin/services") + "/updateDefinition"
    print(update_url)
    session.post(update_url, {"updateDefinition": update_str})

def update_backing_services(items=BACKING_ITEM_IDS, service_descriptions=SERVICE_DESCRIPTIONS, metadata=METADATA):
    """For backing services, we can update both the main service and the layer within it.

    Args:
        items (_type_, optional): _description_. Defaults to BACKING_ITEM_IDS.
        service_descriptions (_type_, optional): _description_. Defaults to SERVICE_DESCRIPTIONS.
        metadata (_type_, optional): _description_. Defaults to METADATA.
    """
    gis = arcgis.gis.GIS("pro")
    for item in items:
        print(item["name"])
        key = item["type_key"]  # is it a city, county, or overlapping?
        item_id = item["itemid"]

        # make the variables clearer to reference
        arcgis_item = gis.content.get(item_id)
        service_url = arcgis_item.url
        layer = arcgis_item.layers[0]

        # we take different strategies to update the layer and the service metadata.
        # start with the service
        print("Service Update")
        update_service_metadata(service_url, gis.session, service_description=service_descriptions[key], metadata=metadata)

        # then the layer - a little simpler here. Set the values, then call update_definition on it.
        print("Layer Update")
        layer.properties["description"] = metadata 
        layer.properties["editingInfo"]["lastEditDate"] = None
        layer.manager.update_definition(layer.properties)


def update_views(items=VIEW_IDS, service_descriptions=SERVICE_DESCRIPTIONS, metadata=METADATA):
    # we'll need to consider how we do this. We can maybe do it here, but we might need to do it with a swap, then an edit, as we do when we do it manually.
    # the layer doesn't pick up the changes from code on the views - not sure how to do it. But the main item will, so do that.

    # currently basically the same code as above because that's the only part here that really works
    gis = arcgis.gis.GIS("pro")
    for item in items:
        print("Updating View")
        key = item["type_key"]
        item_id = item["itemid"]

        arcgis_item = gis.content.get(item_id)
        service_url = arcgis_item.url
        layer = arcgis_item.layers[0]

        print("Service Update")  # the main service can be updated the same way as above, which is great. But the layer is different
        update_service_metadata(service_url, gis.session, service_description=service_descriptions[key], metadata=metadata)

if __name__ == "__main__":
    update_views()
    update_backing_services()
