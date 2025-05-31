# InSAR TS Dataset

Support materials to generate AlignSAR InSAR Time Series Signature Datacube (ITSSD):
- data_coverage.kml - a Google Earth KML file containing coverage polygon of the sample dataset
- input_S1_files.txt - input Sentinel-1 file names that were used to generate LiCSAR interferograms over the sample area of interest (AOI)
- prelim_*tif - preliminary outputs serving as a preview of the content of the final datacubes
- batch_LiCSBAS.sh - a shell script to be used by https://github.com/comet-licsar/licsbas that will auto-generate InSAR time series result identical to the sample InSAR time series benchmark dataset (prior to conversion to the output NetCDF file). Note for the optional reunwrapping procedure, an additional dependency is required: https://github.com/comet-licsar/licsar_extra
- run_licsalert.py - a script to be used to run LiCSAlert (since release v.3.5.1: https://github.com/matthew-gaddes/LiCSAlert/releases/tag/V3.5.1 ) on the generated datacube to perform ML-based blind source separation.  
 
The input InSAR Time Series Benchmark Datacube (ITSBD) is available from [https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/22/022D_04826_ALIGNSAR/licsbas/022D_ALIGNSAR_latest.nc](https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/22/022D_04826_ALIGNSAR/licsbas/022D_ALIGNSAR_latest.nc)


## Usage

1. Installation of prerequisites  
    1. Option 1: Use of docker image  
      Please download the [Docker file](https://github.com/AlignSAR/alignSAR/blob/main/DockerFile_LiCSAR_SNAP) to a new directory, rename it to 'Dockerfile' and perform command:
      
      >     docker build -t alignsarts .
      
      Then, use the following command to run the image:  
      >     docker run -it alignsarts
      
    2. Option 2: Install repositories  
      Please install according to instructions on the following repository websites:  
          1. [LiCSBAS](https://github.com/comet-licsar/licsbas) - **mandatory**, for generating time series and the ITSBD
          2. [LiCSAlert](https://github.com/matthew-gaddes/LiCSAlert/releases/tag/V3.5.1) - *optionally*, for machine learning application on the ITSBD
          3. [LiCSAR Extra](https://github.com/comet-licsar/licsar_extra) - *optionally*, for further advanced LiCSBAS procedure, including re-unwrapping original interferograms procedure in LiCSBAS (if enabled inside batch_LiCSBAS.sh - disabled by default)

2. Generate InSAR time series  
   Download/copy the batch_LiCSBAS.sh script to a new directory, run it in terminal using
   >     ./batch_LiCSBAS.sh
   
   This script will auto-download and process data over Campi Flegrei but this can be modified easily, identifying source data that is COMET LiCSAR open data available from [COMET LiCS Portal](https://comet.nerc.ac.uk/COMET-LiCS-portal).
4. Export to the AlignSAR ITSBD  
   Inside the same directory where you applied LiCSBAS, run following command to generate the ITSBD.nc datacube:  
   >     LiCSBAS_out2nc.py --alignsar -o ITSBD.nc -i TS*/cum.h5
   
5. Optionally apply LiCSAlert procedure  
   Download/copy the run_licsalert.py script to a new directory, edit it (update path to your input ITSBD file, path to ICASAR folder that is part of the LiCSAlert package, or optimize processing parameters) and run it using  
   >     ./run_licsalert.py
   
7. See output PNG files that are informative, or follow recommendations on LiCSBAS and LiCSAlert websites on post-processing and visualization
