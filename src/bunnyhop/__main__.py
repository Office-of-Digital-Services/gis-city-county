import sys
import logging

from . import config
from . import bunny


def main():
    config.startup()
    log = logging.getLogger("bunnyhop")

    output_folder = config.FOLDER_WORKSPACE
    bunny.flow(output_folder)


sys.exit(main())