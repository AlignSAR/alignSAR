#!/usr/bin/env python3
import os
import numpy as np
import warnings
from shutil import copyfile
from doris.doris_stack.main_code.resdata import ResData
import datetime
import subprocess
import matplotlib.pyplot as plt


def baselines(dir_in, inputfile, start_date='2014-01-01', end_date='2018-01-01', doris=''):
    """
    Calculate perpendicular baselines and create a baseline plot (PDF).
    
    Parameters:
    ----------
    dir_in : str
        Path to the main data directory (contains YYYYMMDD subdirectories).
    inputfile : str
        Path to the DORIS input file (relative or absolute).
    start_date : str, optional
        Start date in format 'YYYY-MM-DD'. Default is '2014-01-01'.
    end_date : str, optional
        End date in format 'YYYY-MM-DD'. Default is '2018-01-01'.
    doris : str, optional
        Path to the DORIS executable. Must be provided or set via environment variable.
    """

    # Ensure doris path is provided
    if not doris:
        raise ValueError('Please specify the DORIS executable path, e.g., doris="/path/to/doris"')

    # Check if input directory exists
    if not os.path.exists(dir_in):
        warnings.warn('The input directory does not exist!')
        return

    # Create a processing folder for intermediate results
    process_folder = os.path.join(dir_in, 'baseline_process')
    os.makedirs(process_folder, exist_ok=True)

    # Convert start and end dates to numpy datetime64 objects
    try:
        first = np.datetime64(start_date)
        last = np.datetime64(end_date)
    except Exception:
        warnings.warn('Invalid date format, please use "YYYY-MM-DD"')
        return

    # Find subdirectories with names like YYYYMMDD within the date range
    folders = sorted(next(os.walk(dir_in))[1])
    res = []
    dates = []

    for fold in folders:
        if len(fold) != 8 or not fold.isdigit():
            continue
        date_prod = np.datetime64(f'{fold[:4]}-{fold[4:6]}-{fold[6:]}')
        if not (first <= date_prod <= last):
            continue

        date_fold = os.path.join(dir_in, fold)
        swaths = next(os.walk(date_fold))[1] if os.path.isdir(date_fold) else []
        if not swaths:
            continue
        swath_fold = os.path.join(date_fold, swaths[0])

        if not os.path.isdir(swath_fold):
            continue
        prod_files = next(os.walk(swath_fold))[2]

        # Pick the first file ending with "1.res"
        picked = False
        for file in prod_files:
            if file.endswith('1.res'):
                res.append(os.path.join(swath_fold, file))
                dates.append(date_prod)
                picked = True
                break
        if not picked:
            continue

    if not res:
        warnings.warn('No "*1.res" files found in the given date range.')
        return

    # Copy the first res file as the master.res in the process folder
    master = res[0]
    copyfile(master, os.path.join(process_folder, 'master.res'))

    # Array to store Bperp values
    baselines_arr = np.zeros((len(res), 1), dtype=float)
    resfiles = {}

    # Loop over all res files to create ifgs.res and extract Bperp
    for idx, (resultfile, dat) in enumerate(zip(res, dates)):
        # Copy to slave.res
        copyfile(resultfile, os.path.join(process_folder, 'slave.res'))

        # Run DORIS
        ret = subprocess.call([f'{doris} {inputfile}'], shell=True, cwd=process_folder)
        if ret != 0:
            warnings.warn(f'DORIS execution failed (return code {ret}), skipping {resultfile}')
            if os.path.exists(os.path.join(process_folder, 'ifgs.res')):
                os.remove(os.path.join(process_folder, 'ifgs.res'))
            continue

        dat_str = dat.astype(datetime.datetime).strftime('%Y-%m-%d')

        ifg_path = os.path.join(process_folder, 'ifgs.res')
        if not os.path.exists(ifg_path):
            warnings.warn(f'ifgs.res not generated, skipping {dat_str}')
            continue

        # Read ifgs.res using ResData
        rd = ResData(type='interferogram', filename=ifg_path)
        rd.read()
        resfiles[dat_str] = rd

        # Extract perpendicular baseline (Bperp) from coarse_orbits section
        try:
            baselines_arr[idx, 0] = rd.processes['coarse_orbits']['Bperp'][1]
        except Exception:
            warnings.warn(f'Cannot extract Bperp from ifgs.res ({dat_str})')
            baselines_arr[idx, 0] = np.nan

        # Remove ifgs.res to avoid conflicts
        os.remove(ifg_path)

    # Compute days relative to the first acquisition
    dates_np = np.array(dates)
    days = (dates_np[0] - dates_np).astype(float)

    # Plot baseline graph
    plt.figure(figsize=(6, 4))
    plt.plot(baselines_arr[:, 0], days, marker='o', linestyle='-')
    plt.xlabel('Bperp (m)')
    plt.ylabel('Days relative to first acquisition')
    plt.title('Baseline plot')

    # Annotate with acquisition dates
    for dat, x, y in zip(dates, baselines_arr[:, 0], days):
        dat_str = dat.astype(datetime.datetime).strftime('%Y-%m-%d')
        plt.annotate(dat_str, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8)

    # Save plot to PDF
    out_pdf = os.path.join(process_folder, 'baseline_plot.pdf')
    plt.tight_layout()
    plt.savefig(out_pdf)
    print(f'Baseline plot saved to: {out_pdf}')
