from . import config

from typing import Optional
import pathlib
import zipfile
import tempfile
import datetime
import logging
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

    log = logging.getLogger("bunnyhop.retrieve")

    log.debug("Downloading GNIS data")
    zip_local = download_file(source, extension="zip")

    # this is maybe an odd patter - why load the CSV in Python from the zip and then write it ourself?
    # I was hoping we could load the data straight from the DF into ArcGIS. There's probably a way, but it's not that nice
    # so we write it to a CSV. This code may be able to be simplified.
    log.debug("Extracting GNIS Data")
    with zipfile.ZipFile(file=zip_local) as zipf:  # now load the zipfile, get the text file from it, and read it into a CSV. Libraries doing the heavy lifting here
        
        # return the data as a data frame - another function can load it into an arcgis data structure if needed
        with zipf.open(name=config.GNIS_ZIP_FILE_PATH) as gnis_data:
            gnis_df: pandas.DataFrame = pandas.read_csv(filepath_or_buffer=gnis_data, sep="|")

    log.debug("Writing GNIS CSV")
    output_csv: Optional[pathlib.PurePath] = None
    if output_folder:
        output_csv = output_folder/"gnis_raw_input_data.csv"
        print(f"OUTPUT CSV: {output_csv}")
        gnis_df.to_csv(str(output_csv), index=False)

    log.info("GNIS retrieval complete")
    return {'df': gnis_df, 'csv': output_csv} 


def download_file(source, extension):
    
    file_local: str = tempfile.mktemp(suffix=f".{extension}", prefix="bunnyhop_gnis")  # we could probably do this all in memory, but lets not and avoid a class of bugs
    with requests.get(source, stream=True) as response:
        response.raise_for_status()
        with open(file=file_local, mode='wb') as outf:  # write out the file's data into a tempfile by chunk
            for chunk in response.iter_content(chunk_size=4096):
                outf.write(chunk)
    return file_local 

    
def retrieve_census(output_folder):
    """
        The census retrieval may be a bit funky. We need to find the most recent year of data that has a particular file, then ensure that the file
        has the needed columns existing (and maybe even populated? Check with Liana)
    """
    log = logging.getLogger("bunnyhop")

    output_csv = output_folder / "census_FIPS.csv"

    current_year = datetime.datetime.now(tz=datetime.UTC).year
    check_year = current_year
    while check_year >= config.CENSUS_EARLIEST_YEAR:
        log.debug(f"Checking for Census data for year {check_year}")
        found = _check_for_year_census_file(check_year, filepath_on_success=output_csv)
        if found:
            log.debug(f"Census data found for year {check_year}")
            break
        log.debug("Data not found or missing required information. Trying next")
        check_year -= 1
    else:  # if we don't break, the else block runs, in which case, we couldn't retrieve data
        log.error(f"Couldn't retrieve correct Census data. Tried years from {config.CENSUS_EARLIEST_YEAR} - {current_year}. Check that their URL structure hasn't changed")
        raise RuntimeError(f"Couldn't retrieve correct Census data. Tried years from {config.CENSUS_EARLIEST_YEAR} - {current_year}. Check that their URL structure hasn't changed")

    log.info(f"Census data written out to {str(output_csv)}")
    # if we make it here, we've downloaded the census data into this file
    return output_csv


def _check_for_year_census_file(year, filepath_on_success):

    # census_folder = config.CENSUS_FOLDER_URL.substitute(year=year)
    census_file = config.CENSUS_FILE_URL.substitute(year=year)

    # check for the year's file
    if requests.head(census_file).status_code != 404:
        census_local = download_file(census_file, "xlsx")
        df = pandas.read_excel(census_local,
                                skiprows=4,
                                dtype={
                                    "State FIPS Code": str,
                                    "County FIPS Code": str,
                                    "County Subdivision FIPS Code": str,
                                    "Place FIPS Code": str,
                                    "Consolidated City FIPS Code": str,
                                    "Area Name": str,
                               })
        
        # replace all the spaces in the column names with underscores using a dictionary comprehension
        df.rename(columns={value: value.replace(" ", "_") for value in df.columns}, inplace=True)

        california = df.loc[df["State_FIPS_Code"] == "06",].reset_index(drop=True)
        california["has_data"] = california.loc[:,["County_FIPS_Code", "County_Subdivision_FIPS_Code", "Place_FIPS_Code", "Consolidated_City_FIPS_Code"]].any(axis=1) 
        # we'd expect a certain number of missing records. 2022's has 53 missing, but there could be more
        missing_count = california["has_data"].count() - california["has_data"].sum()
        if missing_count > 5: # we expect 1, but error out if there are more than a few in case we're missing some for new places.
            return False

        # if we're successful, write the filtered DF to the provided path and return True
        del california["has_data"] # we don't need that column - it was just a check
        california.reset_index(drop=True, inplace=True)
        california.to_csv(str(filepath_on_success), index=False)
        return True
    else:
        return False