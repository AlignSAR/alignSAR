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
1. Doris Processing done up to coarse orbits stage.

Steps:
1. Height to Buildings
2. Rasterization using gdal
'''
import argparse
from alignsar.alignsar_utils import read_param_file
from alignsar.rdrcode.rdrCode_prep_ref_data import (
    prepare_poly_ref_data,
    get_doris_process_bounds,
    alter_input_file,
    execute_rdrcode
)

def _to_list(str_list):
    return [i[1:-1].strip("' ") for i in str_list[1:-1].split(',')]

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Software to radar-code vector reference files with respect to a SAR image.\n\n"
            "Dependencies: doris, gdal, shapely, geopandas\n"
            "Make sure doris and gdal are callable from the shell.\n\n"
            "Estimated disk space needed: ~2 × uncompressed SAR data size\n"
            "Requirement: Doris processing completed up to coarse orbits stage."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        usage=(
            "\n  rdrCode_main.py --inputFile input_card.txt\n\n"
            "Example:\n"
            "  python rdrCode_main.py --inputFile input_card.txt\n"
        )
    )
    parser.add_argument(
        '--inputFile',
        type=str,
        required=True,
        help='Full path to the Doris/AlignSAR parameter card file.'
    )

    args = parser.parse_args()

    # Read parameters from input card
    input_file = args.inputFile
    params = read_param_file(input_file)

    # 1. Prepare reference data
    xmin, ymin, xmax, ymax = get_doris_process_bounds(
        params['dorisProcessDir'], params['refDataFile']
    )
    prepare_poly_ref_data(params, extent=[xmin, ymin, xmax, ymax])

    # 2. Update input card
    rdr_input_card = 'input_radarcode'
    rdrCode_input_fnames = alter_input_file(rdr_input_card, params)

    # 3. Execute radar-coding
    execute_rdrcode(params, rdrCode_input_fnames)

if __name__ == '__main__':
    main()
