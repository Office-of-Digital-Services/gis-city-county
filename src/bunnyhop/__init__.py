__version__ = "2024.07.30"

import os
import sys

from . import bunny, config, publish, quality_check, retrieve

__all__ = ["bunny", "config", "publish", "quality_check", "retrieve"]

def locked_down_path_fix():
    """
        On CDT computers, conda environments can't be activated normally, which seems to interfere
        with the search path when calling the python executable from the conda clone itself without
        activating it first. This hack inserts the parent directory of this package into the
        beginning of the search path so that anything in this directory can be found.
    """
    if "USERDOMAIN" in os.environ and os.environ["USERDOMAIN"] == "TDC":
        print("performing locked down path fix")
        insert_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, insert_path)

# locked_down_path_fix()