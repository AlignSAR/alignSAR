# AlignSAR
The AlignSAR tools are used to extract representative SAR signatures, and ultimately offer FAIR-guided open SAR benchmark dataset library designed for SAR-based artificial intelligence applications, while ensuring interoperability and consistency with existing and upcoming initiatives and technologies, facilitating wider exploitation of SAR data and its integration and combination with other datasets. This library will contain meaningful and accurate SAR signatures created by integrating and aligning multi-SAR images and other geodetic measurements in time and space. 

Tool description:
1. MLscripts: scripts for machine learning analysis.
2. bin: scripts needed for running rdcode.
3. itc-doris_5_patch2023: an updated version of Doris-5 software developed by TUDelft.
4. jupyter_notebook_demo: a jupyter notebook to demonstrate how to extract, visualize and analyse SAR signatures.
5. python:?
6. rdcode: the radarcoding script. The input is the SNAP standard output.
7. snap_graphs: scripts to build SNAP graphs and create input for running rdcode.
8. DockerFile: docker file with OS and software setup.
9. Meta_info_extraction_global_local.py: script to extract global/local attributes from Sentinel-1 SAR metadata. 
10. barsrc_alignsar.sh: ?
11. resdata.py: script needed from signature_extraction.py.
12. signature_extraction.py: SAR signature extraction script.
13. speckle_filt.py: A speckle filtering script.
14. utils.py: script called by signature_extraction.py.
