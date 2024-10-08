# BunnyHop
BunnyHop is ETL code for:
1. Retrieving authoritative city/county boundaries from CDTFA,
2. Processing them using Python/ArcGIS to change the spatial data structure and add attributes for CalTrans
3. Publishing the results to ArcGIS Online

It will have built in metadata-attachment and QA checks, with error handling and either ticket-filing or emails.

## Requirements
BunnyHop is designed to run in a Python environment that has both the `arcpy` and `arcgis` package installed. The `arcgis` Python
package can be installed in any python environment, but `arcpy` must be in a conda environment on the same machine as an installation
of ArcGIS Pro or ArcGIS Enterprise. One good way to work with it is to use the package manager of ArcGIS Pro to clone the base
Python environment.

## What's with the name?
We're working with boundaries. And what animal "bounds"? Bunnies. That's it. It's a bad name, I know.

