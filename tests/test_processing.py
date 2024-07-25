from pandas import DataFrame
import pytest


from bunnyhop import retrieve, bunny

def test_gnis_processing():
    folder, gdb = bunny.create_workspace()
    print(folder)
    gnis_data: DataFrame = retrieve.retrieve_gnis(output_folder=folder)
    print("retrieved")
    bunny.process_gnis(str(gnis_data['csv']))
    print("processed")
