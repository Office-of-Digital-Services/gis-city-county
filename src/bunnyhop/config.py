GNIS_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/FederalCodes/FedCodes_CA_Text.zip"
GNIS_ZIP_FILE_PATH = "Text/FederalCodes_CA.txt"  # where is the file we want to extract from the zip file?

### CENSUS CONFIGS ###

# we do an iterative check for the census data (described in the code itself), starting with the current year, then going back
# to earlier years until we find a good one. What's the earliest year we should use? Set this to a year you know has good
# data with all the variables filled in.
CENSUS_EARLIEST_YEAR = 2023  # don't check any years earlier (e.g. 2022) than this. If 2023 fails for some reason, just STOP.