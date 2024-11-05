from _metadata import METADATA

import arcgis
import json

# layer IDs and also type keys
COUNTIES = 1
CITIES = 2
OVERLAPPING = 3

SERVICE_DESCRIPTIONS = {}
SERVICE_DESCRIPTIONS[CITIES] = "PRE-RELEASE: City boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA). The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities were added from Caltrans Division of Local Assistance (DLA) data. Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, the coastline is used to separate coastal buffers from the land-based portions of jurisdictions. This feature layer is for public use."
SERVICE_DESCRIPTIONS[COUNTIES] = "PRE-RELEASE: County boundaries boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA), altered to show the counties as one polygon. The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities were added from Caltrans Division of Local Assistance (DLA) data. Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, the coastline is used to separate coastal buffers from the land-based portions of jurisdictions. This feature layer is for public use."
SERVICE_DESCRIPTIONS[OVERLAPPING] = "PRE-RELEASE: County and incorporated place (city) boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA), altered to show the counties as one polygon. This layer displays the city polygons on top of the County polygons so the area isn't interrupted. The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities were added from Caltrans Division of Local Assistance (DLA) data. Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, the coastline is used to separate coastal buffers from the land-based portions of jurisdictions. This feature layer is for public use."

BACKING_ITEM_IDS = [
    {"itemid": "ccca849ba14a4981b03890fa0eb18fd0", "type_key": CITIES, "name": "cities blue"}, # blue
    {"itemid": "54174ab653044e5cb4e02ec62dd5b20e", "type_key": CITIES, "name": "cities green"},  # green
    {"itemid": "d6e66ae333ec4ca8b1760070d3f60619", "type_key": COUNTIES, "name": "counties blue"}, # blue
    {"itemid": "2c4615f85c7a4b578c9d88736ec8b1de", "type_key": COUNTIES, "name": "counties green"},  # green
    {"itemid": "b55964fa399746aea4c9b259626d0005", "type_key": OVERLAPPING, "name": "overlapping blue"}, # blue
    {"itemid": "90bdf35f9a784312b4cf7d3567e7ac5c", "type_key": OVERLAPPING, "name": "overlapping green"}  # green
]  # for each of these, we can get the item's service endpoint as item.url and get the layer as item.layers[0] then set the metadata with different strategies

VIEW_IDS = [
    {"itemid": "be8a1cd8eff242b0a25feb54e5a2f5a6", "type_key": CITIES}, # with coastal buffers
    {"itemid": "8cd5d2038c5547ba911eea7bec48e28b", "type_key": CITIES}, # without coastal buffers
    {"itemid": "28c9f9dd8c3d4eb5a534cb30ddb3ce39", "type_key": COUNTIES}, # with coastal buffers
    {"itemid": "60b7e0f3d33b4064a4b43bf14589bfe3", "type_key": COUNTIES}, # without coastal buffers
    {"itemid": "14ff938d4a3045aea74fe18cbf954aa5", "type_key": OVERLAPPING}, # with coastal buffers
    {"itemid": "894e9cda46bb45c2a0c7b5534b9a6b4a", "type_key": OVERLAPPING} # without coastal buffers
]

def update_service_metadata(service_url, session, service_description, metadata):
    update = {"serviceDescription":service_description, "description": metadata, "editingInfo":{"lastEditDate": None}}
    update_str = json.dumps(update)

    update_url = service_url.replace("rest/services", "rest/admin/services") + "/updateDefinition"
    print(update_url)
    session.post(update_url, {"updateDefinition": update_str})

def update_backing_services(items=BACKING_ITEM_IDS, service_descriptions=SERVICE_DESCRIPTIONS, metadata=METADATA):
    gis = arcgis.gis.GIS("pro")
    for item in items:
        print(item["name"])
        key = item["type_key"]
        item_id = item["itemid"]

        arcgis_item = gis.content.get(item_id)
        service_url = arcgis_item.url
        layer = arcgis_item.layers[0]

        # we take different strategies to update the layer and the service metadata.
        # start with the service
        print("Service Update")
        update_service_metadata(service_url, gis.session, service_description=service_descriptions[key], metadata=metadata)

        # then the layer
        print("Layer Update")
        layer.properties["description"] = metadata
        layer.properties["editingInfo"]["lastEditDate"] = None
        layer.manager.update_definition(layer.properties)


def update_views(items=VIEW_IDS, service_descriptions=SERVICE_DESCRIPTIONS, metadata=METADATA):
    # we'll need to consider how we do this. We can maybe do it here, but we might need to do it with a swap, then an edit, as we do when we do it manually.
    # the layer doesn't pick up the changes from code on the views - not sure how to do it. But the main item will, so do that.

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
