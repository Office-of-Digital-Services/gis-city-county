from pandas import DataFrame
import pytest

import os
import sys
sys.path.insert(0, os.getcwd())

from bunnyhop import retrieve, bunny

def test_gnis_processing():
    folder, gdb = bunny.create_workspace()
    print(folder)
    gnis_data: DataFrame = retrieve.retrieve_gnis(output_folder=folder)
    print("retrieved")
    bunny.process_gnis(str(gnis_data['csv']))
    print("processed")
