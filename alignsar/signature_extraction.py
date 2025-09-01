#!/usr/bin/env python3
import os,sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import numpy.ma as ma
from .alignsar_utils import *
import numpy.linalg as LA
import math
import xarray as xr
from .Meta_info_extraction_global_local import *
import netCDF4 as nc
import argparse


def get_p_value(eigen_full):
    lamb1 = eigen_full[..., 1]
    lamb2 = eigen_full[..., 0]
    lamb_sum = np.sum(eigen_full, axis=3)  # axis=3 for full stack computation
    p1 = lamb1 / lamb_sum
    p2 = lamb2 / lamb_sum
    return [p1, p2]

def entropy_cal(eigen_full):
    p = get_p_value(eigen_full)
    p0_log = np.log(p[0]) / math.log(2)
    p1_log = np.log(p[1]) / math.log(2)
    ent = -1 * (p[0] * p0_log + p[1] * p1_log)
    return ent

def mean_alpha_angle(coh_matrix):
    p, v = np.linalg.eig(coh_matrix)
    alpha_0 = np.arccos(np.absolute(np.mean(v[..., 0, :], axis=2)))
    alpha_1 = np.arccos(np.absolute(np.mean(v[..., 1, :], axis=2)))
    mean_alpha = (p[0] * alpha_0 + p[1] * alpha_1) * 180 / np.pi
    return mean_alpha

def plot_clipped(arr, per_min, per_max):
    return np.clip(arr, *np.percentile(arr, (per_min, per_max)))

def get_co_pol_phase_diff_sd(vv_arr_stack, hh_arr_stack, AVG_WIN_SIZE=5):
    shp_MN = vv_arr_stack.shape[:-1]
    epochs = vv_arr_stack.shape[-1]
    shp_MN = np.array(shp_MN) - AVG_WIN_SIZE + 1
    phase_diff_mean_squared = test_convolve_3d(
        np.angle(vv_arr_stack) - np.angle(hh_arr_stack),
        AVG_WIN_SIZE, dtype=np.float32
    ) ** 2
    phase_diff_squared_mean = (np.angle(vv_arr_stack) - np.angle(hh_arr_stack)) ** 2
    return np.sqrt(phase_diff_squared_mean - phase_diff_mean_squared)

def co_pol_power_ratio_1(cov_arr):
    return cov_arr[..., 0, 0] / cov_arr[..., 1, 1]

def co_pol_cross_product(cov_arr):
    return cov_arr[..., 0, 1]

def co_pol_diff(cov_arr):
    return cov_arr[..., 0, 0] - cov_arr[..., 1, 1]

def co_pol_sum(cov_arr):
    return cov_arr[..., 0, 0] + cov_arr[..., 1, 1]

def co_pol_correlation(cov_arr):
    return cov_arr[..., 0, 1] / np.sqrt(cov_arr[..., 0, 0] * cov_arr[..., 1, 1])

def get_avg_cov_mat(vv_arr_stack, hh_arr_stack, AVG_WIN_SIZE=5, PADDING=True):
    shp_MN = vv_arr_stack.shape[:-1]
    epochs = vv_arr_stack.shape[-1]
    shp_MN = np.array(shp_MN) - AVG_WIN_SIZE + 1

    cov_arr = np.dstack((
        test_convolve_3d(np.absolute(hh_arr_stack) ** 2, AVG_WIN_SIZE),
        test_convolve_3d(hh_arr_stack * np.conj(vv_arr_stack), AVG_WIN_SIZE),
        test_convolve_3d(vv_arr_stack * np.conj(hh_arr_stack), AVG_WIN_SIZE),
        test_convolve_3d(np.absolute(vv_arr_stack) ** 2, AVG_WIN_SIZE)
    )).reshape(shp_MN[0], shp_MN[1], 4, epochs).transpose(0, 1, 3, 2).reshape(shp_MN[0], shp_MN[1], epochs, 2, 2)

    if (PADDING & (AVG_WIN_SIZE % 2 != 0)):
        cov_arr = np.pad(
            cov_arr,
            pad_width=((AVG_WIN_SIZE // 2, AVG_WIN_SIZE // 2),
                       (AVG_WIN_SIZE // 2, AVG_WIN_SIZE // 2),
                       (0, 0), (0, 0), (0, 0))
        )

    print('cov_arr.shape', cov_arr.shape)
    return cov_arr

def plot_decomposition_RGB(slc_arr, clip_extremes):
    b = hist_stretch_all(((slc_arr[..., 0] + slc_arr[..., 1]) ** 2) / 2, 0, clip_extremes)
    r = hist_stretch_all(slc_arr[..., 0] ** 2, 0, clip_extremes)
    g = hist_stretch_all(slc_arr[..., 1] ** 2, 0, clip_extremes)
    plot_arr = np.dstack((r, g, b))
    plt.imshow(plot_arr)
    plt.show()

def read_rdr_coded_file(filename, lines, pixels, dtype=np.float32,
                        CROPPING=False, CRP_LIST=[10, 20, 10, 20],
                        OFFSET=True, OFFST_lp=[1, 37], MASKING=False):
    rdr_coded_arr_orig = np.fromfile(filename, dtype=dtype).reshape(lines, pixels)
    rdr_coded_arr = np.zeros((lines, pixels))
    if OFFSET:
        rdr_coded_arr[:-OFFST_lp[0], :-OFFST_lp[1]] = rdr_coded_arr_orig[OFFST_lp[0]:, OFFST_lp[1]:]
    else:
        rdr_coded_arr = rdr_coded_arr_orig
    if CROPPING:
        rdr_coded_arr = rdr_coded_arr[CRP_LIST[0]:CRP_LIST[1], CRP_LIST[2]:CRP_LIST[3]]
    if MASKING:
        rdr_coded_arr = ma.masked_where(rdr_coded_arr == 0, rdr_coded_arr)
    return rdr_coded_arr

def parse_args():
    p = argparse.ArgumentParser(description="Signature extraction to NetCDF")
    p.add_argument("--doris_stack_dir_vv", required=True, type=str)
    p.add_argument("--doris_stack_dir_vh", required=True, type=str)
    p.add_argument("--master_date", required=True, type=str)
    p.add_argument("--crop_first_line", required=True, type=int)
    p.add_argument("--crop_last_line", required=True, type=int)
    p.add_argument("--crop_first_pixel", required=True, type=int)
    p.add_argument("--crop_last_pixel", required=True, type=int)
    p.add_argument("--lines_full", required=True, type=int, help="Full image lines for lam/phi/raw shapes")
    p.add_argument("--pixels_full", required=True, type=int, help="Full image pixels for lam/phi/raw shapes")
    p.add_argument("--netcdf_lines", required=True, type=int, help="NetCDF 'lines (azimuth)' dimension")
    p.add_argument("--netcdf_pixels", required=True, type=int, help="NetCDF 'pixels (range)' dimension")
    p.add_argument("--lam_file", required=True, type=str)
    p.add_argument("--phi_file", required=True, type=str)
    p.add_argument("--sar_folder_path", required=True, type=str)
    p.add_argument("--max_images", required=True, type=int)
    return p.parse_args()
    
def main():
    args = parse_args()
    doris_stack_dir_VV = os.path.abspath(args.doris_stack_dir_vv)
    doris_stack_dir_VH = os.path.abspath(args.doris_stack_dir_vh)
    master_date = str(args.master_date)

    CROPPING = True
    CRP_LIST = [args.crop_first_line, args.crop_last_line,
                args.crop_first_pixel, args.crop_last_pixel]
    MAX_IMAGES = int(args.max_images)
    map_type = 'cpx'  # 'cpx', 'ifg', 'coh'

    # dates list (limit to MAX_IMAGES)
    dates = get_dates(doris_stack_dir_VV, master_date)[:MAX_IMAGES]
    print("DATES:", dates)

    # stacks (cropped)
    vv_arr_stack = get_stack(dates, master_date, doris_stack_dir_VV, map_type,
                             crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')
    vh_arr_stack = get_stack(dates, master_date, doris_stack_dir_VH, map_type,
                             crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')

    # Top10NL radar-coded layers (found in master folder under VV stack)
    top10_path = os.path.join(doris_stack_dir_VV, str(master_date))
    top10_building_file_name = os.path.join(top10_path, 'top10nl_gebouw_vlak_radarcoded.raw')
    top10_railway_file_name = os.path.join(top10_path, 'top10nl_spoorbaandeel_lijn_radarcoded.raw')
    top10_water_file_name   = os.path.join(top10_path, 'top10nl_waterdeel_vlak_radarcoded.raw')
    top10_road_file_name    = os.path.join(top10_path, 'top10nl_wegdeel_vlak_radarcoded.raw')

    building_arr = read_rdr_coded_file(top10_building_file_name, args.lines_full, args.pixels_full,
                                       dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST,
                                       MASKING=False, OFFSET=True, OFFST_lp=[1, 12])
    railway_arr  = read_rdr_coded_file(top10_railway_file_name,  args.lines_full, args.pixels_full,
                                       dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST,
                                       MASKING=False, OFFSET=True, OFFST_lp=[1, 12])
    water_arr    = read_rdr_coded_file(top10_water_file_name,    args.lines_full, args.pixels_full,
                                       dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST,
                                       MASKING=False, OFFSET=True, OFFST_lp=[1, 12])
    road_arr     = read_rdr_coded_file(top10_road_file_name,     args.lines_full, args.pixels_full,
                                       dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST,
                                       MASKING=False, OFFSET=True, OFFST_lp=[1, 12])

    # geo lon/lat
    lam_dataFilename = os.path.abspath(args.lam_file)
    phi_dataFilename = os.path.abspath(args.phi_file)
    lam_merge_arr = freadbk(lam_dataFilename, 1, 1, args.lines_full, args.pixels_full,
                            'float32', int(args.lines_full), int(args.pixels_full))
    phi_merge_arr = freadbk(phi_dataFilename, 1, 1, args.lines_full, args.pixels_full,
                            'float32', int(args.lines_full), int(args.pixels_full))

    # covariance matrix for pol features
    cov_arr = get_avg_cov_mat(vv_arr_stack, vh_arr_stack, AVG_WIN_SIZE=3, PADDING=True)

    # features
    vv_amp = np.abs(vv_arr_stack)
    vh_amp = np.abs(vh_arr_stack)
    vv_ifg = np.angle(get_stack(dates, master_date, doris_stack_dir_VV, 'ifg',
                                crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1'))
    vv_coh = get_stack(dates, master_date, doris_stack_dir_VV, 'coh',
                       crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1').real
    intensity_sum = np.square(vv_amp) + np.square(vh_amp)
    intensity_diff = np.square(vv_amp) - np.square(vh_amp)
    intensity_ratio = np.square(vv_amp) / np.square(vh_amp)
    cross_pol_corr_coeff = np.absolute(co_pol_correlation(cov_arr))
    cross_pol_cross_product = np.absolute(co_pol_diff(cov_arr))
    entropy = entropy_cal(np.sort(np.absolute(LA.eigvals(cov_arr)), axis=3))

    # lon/lat crop
    lon = lam_merge_arr[args.crop_first_line:args.crop_last_line,
                        args.crop_first_pixel:args.crop_last_pixel]
    lat = phi_merge_arr[args.crop_first_line:args.crop_last_line,
                        args.crop_first_pixel:args.crop_last_pixel]

    # signature / attribute lists
    signature_list = [
        'VV amplitude (linear)', 'VH amplitude (linear)', 'VV interferometric phase (radians)', 'VV coherence',
        'Intensity summation', 'Intensity difference (dual-pol difference)', 'Intensity ratio (dual-pol power ratio)',
        'Cross-pol correlation coefficient', 'Cross-pol cross product', 'Entropy',
        'Buildings', 'Railways', 'Water', 'Roads', 'Lon', 'Lat'
    ]
    
    local_attributes_list = [
        VV_amplitude_attr, VH_amplitude_attr, VV_interferometric_phase_attr, VV_coherence_attr, Intensity_summation_attr,
        Intensity_difference_attr, Intensity_ratio_attr, Cross_pol_correlation_coefficient_attr,
        Cross_pol_cross_product_attr, Entropy_attr, Buildings_attr, Railways_attr, Water_attr, Roads_attr, Lon_attr, Lat_attr
    ]

    sar_folder_path = os.path.abspath(args.sar_folder_path)

    epochs = min(len(dates), MAX_IMAGES)
    for ei in range(epochs):
        data_cube = np.transpose(np.stack((
            vv_amp[:, :, ei], vh_amp[:, :, ei], vv_ifg[:, :, ei], vv_coh[:, :, ei],
            intensity_sum[:, :, ei], intensity_diff[:, :, ei], intensity_ratio[:, :, ei],
            cross_pol_corr_coeff[:, :, ei], cross_pol_cross_product[:, :, ei], entropy[:, :, ei],
            building_arr, railway_arr, water_arr, road_arr, lon, lat
        )))

        nc_name = f'netcdf_{dates[ei]}_full_attributes.nc'
        ds = nc.Dataset(nc_name, 'w', format='NETCDF4')

        global_attributes = get_global_attribute(sar_folder_path + '/', ei, 0, lon.max(),lon.min(),lat.max(),lat.min(),master_date,CRP_LIST)
        #print(sar_folder_path + '/', ei, 0, lon.max(),lon.min(),lat.max(),lat.min(),master_date,CRP_LIST)
        for attr_name, attr_value in global_attributes.items():
            setattr(ds, attr_name, attr_value)

        ds.createDimension('lines (azimuth)', args.netcdf_lines)
        ds.createDimension('pixels (range)', args.netcdf_pixels)

        layer_num = 16
        for li in range(layer_num):
            vtype = 'f8' if signature_list[li] in ('Buildings', 'Railways', 'Water', 'Roads') else 'f4'
            var = ds.createVariable(signature_list[li], vtype, ('lines (azimuth)', 'pixels (range)'))
            for loc_attr_name, loc_attr_value in local_attributes_list[li].items():
                setattr(var, loc_attr_name, loc_attr_value)
            var[:] = data_cube[:, :, li]

        ds.close()
        
if __name__ == "__main__":
    main()
   
