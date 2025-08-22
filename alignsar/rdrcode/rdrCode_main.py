#!/usr/bin/env python3
'''
Author: Anurag Kulshrestha
Script for: wgs2radar
Date Created: 28-11-2022

Dependencies:
1. doris
2. gdal
3. Shapely
4. Geopandas

Requirements:
1. Doris Processing done uptil coarse orbits stage.

Steps:
1. Height to Buildings
2. Rasterization using gdal
'''
import argparse
# from utils.load_shape_unzip_paz import extract_kml_preview  ## not existing...
from alignsar.alignsar_utils import read_param_file
from alignsar.rdrCode_prep_ref_data import prepare_poly_ref_data, get_doris_process_bounds, alter_input_file, execute_rdrcode


def _to_list(str_list):
    return [i[1:-1].strip("' ") for i in str_list[1:-1].split(',')]

def main():
    parser = argparse.ArgumentParser(description='''Software to radarcode vector reference files w.r.t. a SAR image.
    Dependencies of the software and doris and gdal. Therefore please ensure that
    doris and gdal are directly callable from the shell.
    
    Estimated data space needed on disk: 2 * uncompressed SAR data size
    
    Requirements:''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--inputFile', type = str, help='Full path to the input file')
    
    #parse argument
    args = parser.parse_args()
    
    #read parse data
    input_file = args.inputFile
    
    #read input file
    params = read_param_file(input_file)
    
    #*******************************
    # 0. Extracting SAR data 
    #*******************************.
    #print(_to_list(params['layerNames']))
    #sar_file_dir, sensor, process_dir = params['SARDataDir'][1:-1], params['sensorName'], params['processDir'][1:-1]
    #extract_SAR_geom(sar_file_dir, sensor, process_dir)
    
    
    #*******************************
    # 1. Prepare reference data 
    #*******************************
    xmin, ymin, xmax, ymax = get_doris_process_bounds(params['dorisProcessDir'], params['refDataFile'])
    
    prepare_poly_ref_data(params, extent = [xmin, ymin, xmax, ymax])
    
    #*******************************
    # 2. Update input card
    #*******************************
    rdr_input_card = 'input_radarcode'
    
    rdrCode_input_fnames = alter_input_file(rdr_input_card, params)
    
    
    #*******************************
    # 3. Execute radarcoding
    #*******************************
        
    execute_rdrcode(params, rdrCode_input_fnames)
    

if __name__=='__main__':
    main()

    
