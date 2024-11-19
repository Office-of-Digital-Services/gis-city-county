METADATA = """<p>
    <span style=\"font-size:14px;\"><strong>WARNING</strong>: This is a <strong>pre-release dataset</strong> and its fields names and data structures are subject to change. It should be considered pre-release until the end of 2024. Expected changes:</span>
</p>
<ul>
    <li>
        <span style=\"font-size:14px;\">Metadata is missing or incomplete for some layers at this time and will be continuously improved.</span><br>
        &nbsp;
    </li>
    <li>
        <span style=\"font-size:14px;\">We expect to update this layer roughly in line with CDTFA at some point, but will increase the update cadence over time as we are able to automate the final pieces of the process.</span>
    </li>
</ul>
<div>
    <span style=\"font-size:14px;\">This dataset is continuously updated as </span><span style=\"font-size:14px;\">the source data from CDTFA (https://gis.data.ca.gov/datasets/CDTFA::city-and-county-boundary-line-changes/)</span><span style=\"font-size:14px;\"> is updated, as often as many times a month. If you require unchanging point-in-time data, export a copy for your own use rather than using the service directly in your applications.</span>
</div>
<div>
    &nbsp;
</div>
<div>
    &nbsp;
</div>
<p>
    <span style=\"font-size:x-large;\">Purpose</span><br>
    &nbsp;
</p>
<p>
    City boundaries boundaries along with third party identifiers used to join in external data. Boundaries are from the authoritative source the California Department of Tax and Fee Administration (CDTFA), altered to show the counties as one polygon. The GEOID attribute information is added from the US Census. GEOID is based on merged State and County FIPS codes for the Counties. Abbreviations for Counties and Cities are derived from Caltrans Division of Local Assistance (DLA) and are now managed by CDT (see table below). Place Type was populated with information extracted from the Census. Names and IDs from the US Board on Geographic Names (BGN), the authoritative source of place names as published in the Geographic Name Information System (GNIS), are attached as well. Finally, coastal buffers are split (see below), leaving the land-based portions of jurisdictions. This feature layer is for public use.
</p>
<p>
    &nbsp;
</p>
<p>
    <span style=\"font-size:24px;\">Related Layers</span>
</p>
<p>
    <span style=\"font-size:14px;\">This dataset is part of a grouping of many datasets:</span>
</p>
<ol>
    <li>
        <span style=\"font-size:14px;\"><strong>Cities</strong>: Only the city boundaries and attributes, without any unincorporated areas</span>
        <ul>
            <li>
                With Coastal Buffers: https://california.maps.arcgis.com/home/item.html?id=be8a1cd8eff242b0a25feb54e5a2f5a6
            </li>
            <li>
                Without Coastal Buffers: https://california.maps.arcgis.com/home/item.html?id=8cd5d2038c5547ba911eea7bec48e28b
            </li>
        </ul>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Counties</strong>: Full county boundaries and attributes, including all cities within as a single polygon</span>
        <ul>
            <li>
                With Coastal Buffers: https://california.maps.arcgis.com/home/item.html?id=28c9f9dd8c3d4eb5a534cb30ddb3ce39
            </li>
            <li>
                Without Coastal Buffers: https://california.maps.arcgis.com/home/item.html?id=60b7e0f3d33b4064a4b43bf14589bfe3
            </li>
        </ul>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Cities and Full Counties</strong>: A merge of the other two layers, so polygons overlap within city boundaries. Some customers require this behavior, so we provide it as a separate service<strong>.</strong></span>
        <ul>
            <li>
                With Coastal Buffers: https://california.maps.arcgis.com/home/item.html?id=14ff938d4a3045aea74fe18cbf954aa5
            </li>
            <li>
                Without Coastal Buffers: https://california.maps.arcgis.com/home/item.html?id=894e9cda46bb45c2a0c7b5534b9a6b4a
            </li>
        </ul>
    </li>
    <li>
        <strong>Place Abbreviations</strong>: https://california.maps.arcgis.com/home/item.html?id=edc05d5bf2ce44bca2f4ce0851a2fdf0
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Unincorporated Areas</strong> (Coming Soon)</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Census Designated Places</strong> (Coming Soon)</span><br>
        &nbsp;
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Cartographic Coastline</strong></span>
        <ul>
            <li>
                Polygon: https://california.maps.arcgis.com/home/item.html?id=f7c7ac7e62c645779c98f46a117cf062
            </li>
            <li>
                <span style=\"font-size:14px;\">Line source (Coming Soon)</span>
            </li>
        </ul>
    </li>
</ol>
<div>
    &nbsp;
</div>
<div>
    <span style=\"font-size:large;\"><strong>Working with Coastal Buffers</strong></span><br>
    &nbsp;
</div>
<div>
    See the information in the ArcGIS Online metadata (links above) for more information on working with coastal buffers.
</div>
<div>
    &nbsp;
</div>
<div>
    &nbsp;
</div>
<p>
    <span style=\"font-size:x-large;\">Point of Contact</span>
</p>
<p>
    <span style=\"font-size:14px;\">California Department of Technology, Office of Digital Services, odsdataservices@state.ca.gov</span>
</p>
<p>
    &nbsp;
</p>
<p>
    &nbsp;
</p>
<p>
    <span style=\"font-size:x-large;\">Field and Abbreviation Definitions</span>
</p>
<ul>
    <li>
        <span style=\"font-size:14px;\"><strong>COPRI</strong>: county number followed by the 3-digit city primary number used in the Board of Equalization\"s 6-digit tax rate area numbering system</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Place Name</strong>: CDTFA incorporated (city) or county name</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>County</strong>: CDTFA county name. For counties, this will be the name of the polygon itself. For cities, it is the name of the county the city polygon is within.</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Legal Place Name</strong>: Board on Geographic Names authorized nomenclature for area names published in the Geographic Name Information System</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>GNIS_ID: </strong>The numeric identifier from the Board on Geographic Names that can be used to join these boundaries to other datasets utilizing this identifier.</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>GEOID</strong>: numeric geographic identifiers from the US Census Bureau Place Type: Board on Geographic Names authorized nomenclature for boundary type published in the Geographic Name Information System</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Place Abbr</strong>: CalTrans Division of Local Assistance abbreviations of incorporated area names</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>CNTY Abbr</strong>: CalTrans Division of Local Assistance abbreviations of county names</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>Area_SqMi</strong>: The area of the administrative unit (city or county) in square miles, calculated in EPSG 3310 California Teale Albers.</span>
    </li>
    <li>
        <span style=\"font-size:14px;\"><strong>COASTAL</strong>: Indicates if the polygon is a coastal buffer. Null for land polygons. Additional values include \"ocean\" and \"bay\".</span>
    </li>
</ul>
<p>
    &nbsp;
</p>
<p>
    <span style=\"font-size:24px;\">Accuracy</span>
</p>
<p>
    <span style=\"font-size:14px;\">CDTFA\"s source data notes the following about accuracy:</span>
</p>
<p>
    &nbsp;
</p>
<blockquote>
    <p>
        <span style=\"font-size:14px;\">City boundary changes and county boundary line adjustments filed with the Board of Equalization per Government Code 54900. This GIS layer contains the boundaries of the unincorporated county and incorporated cities within the state of California. The initial dataset was created in March of 2015 and was based on the State Board of Equalization tax rate area boundaries. As of April 1, 2024, the maintenance of this dataset is provided by the California Department of Tax and Fee Administration for the purpose of determining sales and use tax rates. The boundaries are continuously being revised to align with aerial imagery when areas of conflict are discovered between the original boundary provided by the California State Board of Equalization and the boundary made publicly available by local, state, and federal government. Some differences may occur between actual recorded boundaries and the boundaries used for sales and use tax purposes. The boundaries in this map are representations of taxing jurisdictions for the purpose of determining sales and use tax rates and should not be used to determine precise city or county boundary line locations. COUNTY = county name; CITY = city name or unincorporated territory; COPRI = county number followed by the 3-digit city primary number used in the California State Board of Equalization\"s 6-digit tax rate area numbering system (for the purpose of this map, unincorporated areas are assigned 000 to indicate that the area is not within a city).</span>
    </p>
</blockquote>
<p>
    &nbsp;
</p>
<p>
    &nbsp;
</p>
<p>
    &nbsp;
</p>
<div>
    <span style=\"font-size:x-large;\">Boundary Processing</span>
</div>
<div>
    <span style=\"font-size:14px;\">These data make a structural change from the source data. While the full boundaries provided by CDTFA include coastal buffers of varying sizes, many users need boundaries to end at the shoreline of the ocean or a bay. As a result, after examining existing city and county boundary layers, these datasets provide a coastline cut generally along the ocean facing coastline. For county boundaries in northern California, the cut runs near the Golden Gate Bridge, while for cities, we cut along the bay shoreline and into the edge of the Delta at the boundaries of Solano, Contra Costa, and Sacramento counties.</span><br>
    <br>
    &nbsp;
</div>
<div>
    <span style=\"font-size:14px;\">In the services linked above, the versions that include the coastal buffers contain them as a second (or third) polygon for the city or county, with the value in the COASTAL field set to whether it\"s a bay or ocean polygon. These can be processed back into a single polygon by dissolving on all the fields you wish to keep, since the attributes, other than the COASTAL field and geometry attributes (like areas) remain the same between the polygons for this purpose.</span>
</div>
<div>
    &nbsp;
</div>
<div>
    &nbsp;
</div>
<div>
    <span style=\"font-size:large;\"><strong>Slivers</strong></span>
</div>
<div>
    <span style=\"font-size:14px;\">In cases where a city or county\"s boundary ends near a coastline, our coastline data may cross back and forth many times while roughly paralleling the jurisdiction\"s boundary, resulting in many polygon slivers. We post-process the data to remove these slivers using a city/county boundary priority algorithm. That is, when the data run parallel to each other, we discard the coastline cut and keep the CDTFA-provided boundary, even if it extends into the ocean a small amount. This processing supports consistent boundaries for Fort Bragg, Point Arena, San Francisco, Pacifica, Half Moon Bay, and Capitola, in addition to others. More information on this algorithm will be provided soon.</span><br>
    &nbsp;
</div>
<div>
    &nbsp;
</div>
<div>
    <span style=\"font-size:large;\"><strong>Coastline Caveats</strong></span>
</div>
<div>
    <span style=\"font-size:14px;\">Some cities have buffers extending into water bodies that we do not cut at the shoreline. These include South Lake Tahoe and Folsom, which extend into neighboring lakes, and San Diego and surrounding cities that extend into San Diego Bay, which our shoreline encloses. If you have feedback on the exclusion of these items, or others, from the shoreline cuts, please reach out using the contact information above.</span>
</div>
<div>
    &nbsp;
</div>
<div>
    &nbsp;
</div>
<div>
    <span style=\"font-size:x-large;\">Updates and Date of Processing</span>
</div>
<div>
    <span style=\"font-size:14px;\">Concurrent with CDTFA updates, approximately every two weeks. For information on when this was last updated, please see the metadata in ArcGIS Online (links above).</span>
</div>"""