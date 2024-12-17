from agol_bluegreen import AGOLBlueGreen
from _services import BLUEGREEN_SERVICES

def swap_all(services=BLUEGREEN_SERVICES):
    for service in services:
        # these aren't officially the blue or green, but it doesn't really matter if the Python code calls them by the names we have for them. It's just a concept.
        bg = AGOLBlueGreen(service["view"], blue_item_id=service["backing_services"][0], green_item_id=service["backing_services"][1])
        bg.promote_staging()

if __name__ == "__main__":
    swap_all()