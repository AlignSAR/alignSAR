# AlignSAR
[![pytest](https://github.com/Bingquan-InSAR/alignSAR/actions/workflows/tests.yml/badge.svg)](https://github.com/Bingquan-InSAR/alignSAR/actions/workflows/tests.yml)

The AlignSAR tools are used to extract representative SAR signatures, and ultimately offer FAIR-guided open SAR benchmark dataset library designed for SAR-based artificial intelligence applications, while ensuring interoperability and consistency with existing and upcoming initiatives and technologies, facilitating wider exploitation of SAR data and its integration and combination with other datasets. This library will contain meaningful and accurate SAR signatures created by integrating and aligning multi-SAR images and other geodetic measurements in time and space. Related link: https://www.alignsar.nl

## Installation

Python version `>=3.10` is required to install alignsar.

alignsar can be installed from PyPI:

```sh
mamba create -n alignsar python=3.10 -c conda-forge
mamba activate alignsar
mamba install -c conda-forge gdal rasterio geopandas pyproj rioxarray hdf5 netcdf4 libnetcdf
pip install alignsar
```

 
## Dockerfile Setup （Optional）

1. **Preparation**  
   Install Docker and download the [`Dockerfile`](https://github.com/AlignSAR/alignSAR) from the repository into a dedicated directory.  
   This file automatically installs Doris-5 and related third-party tools.

2. **Build the image**
   ```bash
   docker build -t alignsar .
   ```

3. **Run the container**
   ```bash
   docker run -it -v /your_local_path:/path_in_docker alignsar
   ```

   * `-it`: interactive mode  
   * `-v`: mount a local path to the container

---

###	SAR benchmark dataset processing procedure and demonstration 
Please refer to [Alignsar_tutorial.pdf](https://github.com/AlignSAR/alignSAR/blob/main/tutorial/AlignSAR_tutorial.pdf).



## Tutorial and sample data
A set of sample data covering the city of Groningen, the Netherlands, can be found in [/examples/data/data_links.txt]( https://github.com/AlignSAR/alignSAR/blob/main/examples/data/data_links.txt), and with STAC can be downloaded via [link-eotdl](https://www.eotdl.com/datasets/). More description is in the [/tutorial/Alignsar_tutorial.pdf](https://github.com/AlignSAR/alignSAR/blob/main/tutorial/AlignSAR_tutorial.pdf).

## Citations
[1] Ling Chang, Anurag Kulshrestha, Bin Zhang and Xu Zhang (2023). Extraction and analysis of radar scatterer attributes for PAZ SAR by combining time series InSAR, PolSAR and land use measurements. Remote Sensing 15(6), 1571. [Link](https://doi.org/10.3390/rs15061571)

[2] Anurag Kulshrestha, Ling Chang and Alfred Stein (2024). Radarcoding reference data for SAR training data creation in Radar coordinates. IEEE Geoscience and Remote Sensing Letters. [Link](https://ieeexplore.ieee.org/document/10478187)

[3] Ling Chang, Jose Manuel Delgado Blasco, Andrea Cavallini, Andy Hooper, Anurag Kulshrestha, Milan Lazecky, Wojciech Witkowski, Xu Zhang, Serkan Girgin and all other AlignSAR members (2023). AlignSAR: developing an open SAR library for machine learning applications. ESA Fringe 2023, 11-15 Sept 2023, Leeds, UK.

[4] Ling Chang, Xu Zhang, Anurag Kulshrestha, Serkan Girgin, Alfred Stein, Jose Manuel Delgado Blasco, Angie Catalina Carrillo Chappe, Andrea Cavallini, Marco Uccelli, Milan  Lazecky, Andy Hooper, Wojciech Witkowski,  Magdalena Lucka, Artur Guzy (2024). AlignSAR: An open-source package of SAR benchmark dataset creation for machine learning applications. 2024 IEEE International Geoscience and Remote Sensing Symposium, IGARSS 2024, accepted. [Link](https://surfdrive.surf.nl/files/index.php/s/yAgIc2QQ84ht3c1)

[5] Xu Zhang, Ling Chang and Alfred Stein (2025). Creating and leveraging SAR benchmark datasets to facilitate machine learning application. International Journal of Applied Earth Observation and Geoinformation, vol 142, 2025. [Link](https://doi.org/10.1016/j.jag.2025.104722)

## Questions and suggestions
We welcome your questions and suggestions and contributions. Free free to contact us by sending email to alignsar.project@gmail.com

## Acknowledgment
We acknowledge ESA and all members in this project. 
