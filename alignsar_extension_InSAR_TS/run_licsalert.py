#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 10:55:48 2020

@author: matthew

"""
'''
ML: Note - this is example on how to run LiCSAlert v3.5.1 from
https://github.com/matthew-gaddes/LiCSAlert/releases/tag/V3.5.1
working on the AlignSAR datacube - just change the param inputfile
'''
import sys
import pickle
from pathlib import Path
import copy
import numpy as np
import matplotlib.pyplot as plt
import pdb

inputfile = Path("./022D_ALIGNSAR_v4.nc")

licsalert_pkg_dir  = Path(
    "/home/matthew/university_work/03_automatic_detection_algorithm/"
    "06_LiCSAlert/00_LiCSAlert_GitHub"
    )


sys.path.append(str(licsalert_pkg_dir))

import licsalert
from licsalert.monitoring_functions import LiCSAlert_monitoring_mode
from licsalert.plotting import licsalert_results_explorer
from licsalert.licsalert import reconstruct_ts_from_dir





#%% Example 01: Campi Flegrei, only the final figure.  




licsalert_settings = {"baseline_end"        : "20210101",                               # end baseline stage at YYYYMMDD, need to be before the last acquisition of LiCSAlert will never monitoring anyhting.  
                      "figure_intermediate" : False,                             # if set to True, a figure is produced for all time steps in the monitoring data, which can be time consuming.  
                      "figure_type"         : 'both',                             # either 'window' or 'png' (to save as pngs), or 'both'
                      "downsample_run"      : 0.5,                                     # data can be downsampled to speed things up
                      "downsample_plot"     : 0.5,                               # and a 2nd time for fast plotting.  Note this is applied to the restuls of the first downsampling, so is compound
                      "residual_type"       : 'cumulative',                      # controls the type of residual used in the lower plot.  Either cumulative or window   
                      "t_recalculate"       : 40,                               # Number of acquisitions that the lines of best fit are calcualted over.  Larger value makes the algorithm more sensitive
                      'inset_ifgs_scaling'  : 15}                               # scales the size of the incremental and cumulative ifgs in the top row of the figure.  Smaller values gives a bigger figures.  


icasar_settings = {"n_pca_comp_start"       : 6,                                                  
                   "n_pca_comp_stop"        : 7,                                                  
                   "bootstrapping_param"    : (200, 0),                              # (number of runs with bootstrapping, number of runs without bootstrapping)                    "hdbscan_param" : (35, 10),                        # (min_cluster_size, min_samples)
                    "tsne_param"             : (30, 12),                                       # (perplexity, early_exaggeration)
                    "ica_param"              : (1e-2, 150),                                     # (tolerance, max iterations)
                    "hdbscan_param"          : (100,10),                                    # (min_cluster_size, min_samples) Discussed in more detail in Mcinnes et al. (2017). min_cluster_size sets the smallest collection of points that can be considered a cluster. min_samples sets how conservative the clustering is. With larger values, more points will be considered noise. 
                    "ifgs_format"            : 'cum',                                  # can be 'all', 'inc' (incremental - short temporal baselines), or 'cum' (cumulative - relative to first acquisition)
                    "sica_tica"              : 'sica',
                    "load_fastICA_results"   : True}

licsbas_settings = {"filtered"               : False,
                    "date_start"            : None,
                    "date_end"              : None,
                    'mask_type'             : 'licsbas',                        # "dem" or "licsbas"
                    'crop_pixels'           : None}


outdir = Path("./")
volcano = 'alignsar_campi_flegrei'                                                 



LiCSAlert_monitoring_mode(outdir = outdir, region = None, volcano = volcano,
                          alignsar_dc = inputfile,
                          licsalert_settings = licsalert_settings, 
                          icasar_settings = icasar_settings,
                          licsbas_settings = licsbas_settings)

licsalert_out_dir = outdir / volcano

licsalert_results_explorer(outdir / volcano, fig_width = 18)                                                 # use this function to explore the results


#ics_one_hot = [1, 1, 1, 1]                                                                   # One hot encoding of which sources to use in the reconstruction.  1 means used, 0 means not.  list must be the same length as the number of ICs.  
#X_inc_r3, X_cum_r3 = reconstruct_ts_from_dir(ics_one_hot, outdir / volcano)                               # return the cumualtive interferograms reconstrutced using the ICs selected above.  All mean centering has been removed.  

