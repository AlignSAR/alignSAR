# AlignSAR
The AlignSAR tools are used to extract representative SAR signatures, and ultimately offer FAIR-guided open SAR benchmark dataset library designed for SAR-based artificial intelligence applications, while ensuring interoperability and consistency with existing and upcoming initiatives and technologies, facilitating wider exploitation of SAR data and its integration and combination with other datasets. This library will contain meaningful and accurate SAR signatures created by integrating and aligning multi-SAR images and other geodetic measurements in time and space. Related link: https://www.alignsar.nl

## Tool description:
Dockerfile: docker file with OS and software setup. ['Dockerfile'](https://github.com/AlignSAR/alignSAR/blob/main/Dockerfile) is to install Doris-5 and relevant software, 'DockerFile_LiCSAR_SNAP' is to install LiCSAR and SNAP.

 in 'alignsar' folder
1. MLscripts: scripts for machine learning analysis. Yolov8, ANN and Siamese are separately used for Object Detection (India), Land Use Land Cover classification (Netherlands), and Change Detection (Poland).  
2. bin: non-python scripts used within the toolbox (e.g. rdr<->geocode)
3. itc-doris_5_patch2023: an updated version of Doris-5 software developed by TUDelft.
4. rdcode: the radarcoding scripts.
5. snap_graphs: graphs for SNAP used within the toolbox (e.g. rdr<->geocode)
6. stac: python scripts to create STAC
7. Meta_info_extraction_global_local.py: script to extract global/local attributes from Sentinel-1 SAR metadata. 
8. bashrc_alignsar: install settings for the expected environment variables and paths
9. resdata.py: script needed from signature_extraction.py.
10. signature_extraction.py: SAR signature extraction script.
11. speckle_filt.py: A speckle filtering script.
12. alignsar_utils.py: various python functions used within the toolbox.

in 'examples' folder
1. jupyter_notebook_demo: a jupyter notebook to demonstrate how to extract, visualize and analyse SAR signatures.

in 'tests' folder
1. 'MLscripts/Netherlands-LULC': an ANN (artificial neural network) machine learning test for the LULC classification (land use and land cover) over the Netherlands.

in 'tutorial' folder
1. Alignsar_tutorial.pdf: a tutorial containing all the information on AlignSAR installation, methods, data used and step-by-step procedure for SAR benchmark dataset creation and machine learning demonstration.
   
Note that this is research code provided to you "as is" with no warranties of correctness. Use at your own risk.

## Installation
Either build a docker image using provided Dockerfile, or install relevant software manually. 

###	Dockerfile setup:

- To build the AlignSAR docker image, a user should install docker and download Dockerfile (that can automatically install Doris-5 and its relevant third-party software tools) provided in the github repository (https://github.com/AlignSAR/alignSAR) to a dedicated directory. Inside the directory, the user can build the image using:

     docker build -t alignsar .

and test the image by running an interactive terminal session using:

    docker run -it -v /your_local_path:/path_you_want_to_set_in_docker alignsar 

Note that one needs to run these commands in terminal, and in the same folder as the ‘docker’ file stored. Here ‘alignsar’ is to be mounted, and can be customized by the end user. Here the argument ‘-it’ is to run the docker image using interface mode in the terminal, while ‘-v’ is to mount the local disk to
docker. Afterward, the Doris-5 installation directory should be modified by editing the files
/root/DorisITCupdate/doris/doris_stack/main_code/doris_main.py (Line 5) and
/root/DorisITCupdate/doris/install/doris_config.xml (Line 2). Specifically, Line 5:
‘sys.path.append(‘/home/username/software/’)’ should be changed to
‘sys.path.append(‘/root/Doris5ITCupdate/’)’ and Line 2: change to ‘<source_path>/root/Doris5ITCupdate/doris</source_path>’.

- To unmount ’alignsar’ one can directly close the terminal.

- To check whether the Dockerfile is initiated after running the commands above, for instance, one can run ‘which doris’ and ‘doris -v’, and receive the information in the terminal:
  
     root@1f6eb227bd0d:/# which doris

     /usr/local/bin/doris

     root@1f6eb227bd0d:/# doris -v

     INFO    : @(#)Doris InSAR software, $Revision: 4.0.8 $, $Author: TUDelft $

     Software name:    Doris (Delft o-o Radar Interferometric Software)

     Software version: version  4.0.8 (04-09-2014)

                     
Note that AlignSAR provides SAR data preprocessing workflow using 1) Doris, and 2) LiCSAR and SNAP. ‘Dockerfile’ can install Doris-5 and its relevant third-party software tools, while DockerFile_LiCSAR_SNAP is another dockerfile we offered, which can install LiCSAR and SNAP software. The methods and workflow description can be found in the tutorial ‘AlignSAR_tutorial.pdf’. In case of not building and running the Dockerfile(s), one can also manually install Doris, LiCSAR and SNAP and customize preferred processing environment. 

This [Dockerfile](https://github.com/AlignSAR/alignSAR/blob/main/Dockerfile) works well with three different operating systems/docker versions: macOS  Ventura 13.7.3 (docker version: version 4.37.2), ubuntu 20.04.6 LTS (docker version: 24.0.5) and Ubuntu 20.04.1 (docker version: 24.0.7). If you encounter version-related errors or missing Python packages while running this [Dockerfile](https://github.com/AlignSAR/alignSAR/blob/main/Dockerfile) on macOS Sequoia 15.2, please use [Dockerfile1](https://github.com/AlignSAR/alignSAR/blob/main/misc/Dockerfile1) in the folder 'misc'instead.

###	SAR benchmark dataset processing procedure and demonstration 
Please refer to [Alignsar_tutorial.pdf](https://github.com/AlignSAR/alignSAR/blob/main/tutorial/AlignSAR_tutorial.pdf).



## Tutorial and sample data
A set of sample data covering the city of Groningen, the Netherlands, can be found in [/examples/data/data_links.txt]( https://github.com/AlignSAR/alignSAR/blob/main/examples/data/data_links.txt), and with STAC can be downloaded via [link-eotdl](https://www.eotdl.com/datasets/). More description is in the [/tutorial/Alignsar_tutorial.pdf](https://github.com/AlignSAR/alignSAR/blob/main/tutorial/AlignSAR_tutorial.pdf).

## Citations
[1] Ling Chang, Anurag Kulshrestha, Bin Zhang and Xu Zhang (2023). Extraction and analysis of radar scatterer attributes for PAZ SAR by combining time series InSAR, PolSAR and land use measurements. Remote Sensing 15(6), 1571 [[DOI]](https://doi.org/10.3390/rs15061571).  

[2] Anurag Kulshrestha, Ling Chang and Alfred Stein (2024). Radarcoding reference data for SAR training data creation in Radar coordinates. IEEE Geoscience and Remote Sensing Letters.[Link](https://ieeexplore.ieee.org/document/10478187).

[3] Ling Chang, Jose Manuel Delgado Blasco, Andrea Cavallini, Andy Hooper, Anurag Kulshrestha, Milan Lazecky, Wojciech Witkowski, Xu Zhang, Serkan Girgin and all other AlignSAR members (2023). AlignSAR: developing an open SAR library for machine learning applications. ESA Fringe 2023, 11-15 Sept 2023, Leeds, UK.

[4] Ling Chang, Xu Zhang, Anurag Kulshrestha, Serkan Girgin, Alfred Stein, Jose Manuel Delgado Blasco, Angie Catalina Carrillo Chappe, Andrea Cavallini, Marco Uccelli, Milan  Lazecky, Andy Hooper, Wojciech Witkowski,  Magdalena Lucka, Artur Guzy (2024). AlignSAR: An open-source package of SAR benchmark dataset creation for machine learning applications. 2024 IEEE International Geoscience and Remote Sensing Symposium, IGARSS 2024, accepted.[Link](https://surfdrive.surf.nl/files/index.php/s/yAgIc2QQ84ht3c1)

## Questions and suggestions
We welcome your questions and suggestions and contributions. Free free to contact us by sending email to alignsar.project@gmail.com

## Acknowledgment
We acknowledge ESA. 




