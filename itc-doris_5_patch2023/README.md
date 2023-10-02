## Updated version of Doris 5

**Author: Anurag Kulshrestha, email: anurag.librian@gmail.com**

**Institute: Department of Earth Observation Science, ITC, University of Twente. The Netherlands**

# Changes:
### Changes in create_dem.py
    1. Applied patch on in the _srtm_listing() function to change the source for DEMs
    2. Uploaded missing WW15MGH.DAC file to and provieded link @ https://github.com/anurag-kulshrestha/geoinformatics/raw/master/WW15MGH.DAC
    3. Patched to correctly geo-register the downloaded EGM file

### Changes in download_sentinel_data_orbits.py
    Changed link for orbit download to https://scihub.copernicus.eu/gnss
    Streamlined the download process by updating the web-crawler.