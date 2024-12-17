COUNTIES = 1
CITIES = 2
OVERLAPPING = 3

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

def make_bluegreen(views=VIEW_IDS, services=BACKING_ITEM_IDS):
    outputs = []
    for view in views:
        item = {"view": view["itemid"]}
        item["backing_services"] = [service["itemid"] for service in services if service["type_key"] == view["type_key"]]
        outputs.append(item)
    return outputs

BLUEGREEN_SERVICES = make_bluegreen()