# AlignSAR
The AlignSAR tools are used to extract representative SAR signatures, and ultimately offer FAIR-guided open SAR benchmark dataset library designed for SAR-based artificial intelligence applications, while ensuring interoperability and consistency with existing and upcoming initiatives and technologies, facilitating wider exploitation of SAR data and its integration and combination with other datasets. This library will contain meaningful and accurate SAR signatures created by integrating and aligning multi-SAR images and other geodetic measurements in time and space. Related link: https://www.alignsar.nl

## Tool description:
1. MLscripts: scripts for machine learning analysis. Yolov8, ANN and Siamese is seperately used for Object Detection (India), Land Use Land Cover classification (Netherlands), and Change Detection (Polands).  
2. bin: non-python scripts used within the toolbox (e.g. rdr<->geocode)
3. itc-doris_5_patch2023: an updated version of Doris-5 software developed by TUDelft.
4. jupyter_notebook_demo: a jupyter notebook to demonstrate how to extract, visualize and analyse SAR signatures.
6. rdcode: the radarcoding scripts.
7. snap_graphs: graphs for SNAP used within the toolbox (e.g. rdr<->geocode)
8. DockerFile: docker file with OS and software setup.
9. Meta_info_extraction_global_local.py: script to extract global/local attributes from Sentinel-1 SAR metadata. 
10. bashrc_alignsar: install settings for the expected environment variables and paths
11. resdata.py: script needed from signature_extraction.py.
12. signature_extraction.py: SAR signature extraction script.
13. speckle_filt.py: A speckle filtering script.
14. alignsar_utils.py: various python functions used within the toolbox.

## Installation
Either build a docker image using provided Dockerfile, or run following command to set additional environment variables:
`source bashrc_alignsar`
