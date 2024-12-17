from agol_bluegreen import AGOLBlueGreen
from _services import BLUEGREEN_SERVICES

def print_report(services=BLUEGREEN_SERVICES):
    for service in services:
        bg = AGOLBlueGreen(service["view"], blue_item_id=service["backing_services"][0], green_item_id=service["backing_services"][1])
        print(str(bg))

if __name__ == "__main__":
    print_report()