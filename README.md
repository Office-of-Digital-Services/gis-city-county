# California Administrative Boundaries Data Pipeline
BunnyHop is ETL code for:
1. Retrieving authoritative city/county boundaries from CDTFA,
2. Processing them using Python/ArcGIS to change the spatial data structure and add attributes for CalTrans
3. Publishing the results to ArcGIS Online

It will have built in metadata-attachment and QA checks, with error handling and either ticket-filing or emails.

## Status Page and Roadmap
We have a [service status page on the state geoportal](https://gis.data.ca.gov/pages/city-and-county-boundary-data-status).

Our detailed [roadmap is being built out in this project](https://github.com/orgs/Office-of-Digital-Services/projects/14/views/3).

Please file an issue with any change requests for the code.

## Deployed Data Services
Deployed data services are feature services in ArcGIS Online - though they may also be accessed in QGIS or other GIS
systems that can read ArcGIS FeatureServer endpoints.

1. Cities: Only the city boundaries and attributes, without any unincorporated areas
   * [With Coastal Buffers](https://arcgis.com/home/item.html?id=be8a1cd8eff242b0a25feb54e5a2f5a6)
   * [Without Coastal Buffers (this dataset)](https://arcgis.com/home/item.html?id=be8a1cd8eff242b0a25feb54e5a2f5a6)
2. Counties: Full county boundaries and attributes, including all cities within as a single polygon
   * [With Coastal Buffers](https://arcgis.com/home/item.html?id=28c9f9dd8c3d4eb5a534cb30ddb3ce39)
   * [Without Coastal Buffers](https://arcgis.com/home/item.html?id=60b7e0f3d33b4064a4b43bf14589bfe3)
3. Cities and Full Counties: A merge of the other two layers, so polygons overlap within city boundaries. Some customers require this behavior, so we provide it as a separate service.
   * [With Coastal Buffers](https://arcgis.com/home/item.html?id=14ff938d4a3045aea74fe18cbf954aa5)
   * [Without Coastal Buffers](https://arcgis.com/home/item.html?id=894e9cda46bb45c2a0c7b5534b9a6b4a)
4. [City and County Abbreviations](https://arcgis.com/home/item.html?id=edc05d5bf2ce44bca2f4ce0851a2fdf0)
5. Unincorporated Areas (Coming Soon)
6. [Census Designated Places](https://arcgis.com/home/item.html?id=d1a79f9faea241ab9a3f9ef549a19fd7)
7. Cartographic Coastline
   * [Polygon](https://arcgis.com/home/item.html?id=f7c7ac7e62c645779c98f46a117cf062)
   * Line source (Coming Soon)

## Related Projects Used Here
* [gis-agolbluegreen](Office-of-Digital-Services/gis-agolbluegreen) - Python package to manage high availability by swapping views
* [arcpy_metadata](Office-of-Digital-Services/arcpy_metadata) - Python package to edit metadata

## Package Requirements
BunnyHop is designed to run in a Python environment that has both the `arcpy` and `arcgis` package installed. The `arcgis` Python
package can be installed in any python environment, but `arcpy` must be in a conda environment on the same machine as an installation
of ArcGIS Pro or ArcGIS Enterprise. One good way to work with it is to use the package manager of ArcGIS Pro to clone the base
Python environment.

## What's with the package name?
We're working with boundaries. And what animal "bounds"? Bunnies. That's it. It's a bad name, I know.

