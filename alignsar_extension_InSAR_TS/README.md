# InSAR TS Dataset
Milan Lazecky, University of Leeds

Support materials to generate AlignSAR InSAR Time Series Signature Datacube (ITSSD):
- data_coverage.kml - a Google Earth KML file containing coverage polygon of the sample dataset
- input_S1_files.txt - input Sentinel-1 file names that were used to generate LiCSAR interferograms over the sample area of interest (AOI)
- prelim_*tif - preliminary outputs serving as a preview of the content of the final datacubes
- batch_LiCSBAS.sh - a shell script to be used by https://github.com/comet-licsar/licsbas that will auto-generate InSAR time series result identical to the sample InSAR time series benchmark dataset (prior to conversion to the output NetCDF file). Note for the optional reunwrapping procedure, an additional dependency is required: https://github.com/comet-licsar/licsar_extra

The input InSAR Time Series Benchmark Datacube (ITSBD) is available from https://gws-access.jasmin.ac.uk/public/nceo_geohazards/LiCSAR_products/22/022D_04826_ALIGNSAR/licsbas/022D_ALIGNSAR_v2.nc

The datacube can be used as input for the ML processor LiCSAlert (since release v.3.5.1: https://github.com/matthew-gaddes/LiCSAlert/releases/tag/V3.5.1 ) by running provided run_licsalert.py script.
