"""
    I expect that this file will mostly be ArcGIS API for Python-based
"""

from . import config

from typing import Optional
import pathlib
import zipfile
import tempfile
import csv

import requests
import pandas
class BOERetrieve():
    pass


def retrieve_gnis(source=config.GNIS_URL, output_folder: Optional[pathlib.PurePath]=None) -> pandas.DataFrame:
    """Retrieves, decompresses, and loads the GNIS data into a pandas data frame, which it retuns to the callers

    Args:
        source (str, optional): string URL to download the GNIS data. Defaults to config.GNIS_URL.

    Returns:
        pandas.DataFrame: text version of GNIS data loaded into a pandas dataframe
    """

    with requests.get(source, stream=True) as response:
        zip_local: str = tempfile.mktemp(suffix=".zip", prefix="bunnyhop_gnis")  # we could probably do this all in memory, but lets not and avoid a class of bugs
        response.raise_for_status()
        with open(file=zip_local, mode='wb') as outf:  # write out the GNIS data into a tempfile by chunk
            for chunk in response.iter_content(chunk_size=4096):
                outf.write(chunk)

    with zipfile.ZipFile(file=zip_local) as zipf:  # now load the zipfile, get the text file from it, and read it into a CSV. Libraries doing the heavy lifting here
        with zipf.open(name=config.GNIS_ZIP_FILE_PATH) as gnis_data:
            gnis_df: pandas.DataFrame = pandas.read_csv(filepath_or_buffer=gnis_data, sep="|")

    output_csv: Optional[pathlib.PurePath] = None
    if output_folder:
        output_csv = output_folder/"gnis_raw_input_data.csv"
        print(f"OUTPUT CSV: {output_csv}")
        gnis_df.to_csv(str(output_csv))

    return {'df': gnis_df, 'csv': output_csv}  # return the data as a data frame - another function can load it into an arcgis data structure if needed

    