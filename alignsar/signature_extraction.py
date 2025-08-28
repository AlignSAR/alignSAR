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


# Several paths should be specified before using this script. 
# 'doris_stack_dir_VV' and 'doris_stack_dir_VH' are pre-processed path of Doris results.
# 'top10_path' is the path of TOP10NL data.
# 'lam_dataFilename' and 'phi_dataFilename' are longitude and latitude.
# 'sar_folder_path' is unzipped raw SAR SLC file path for extracting global and local attributes.

def get_p_value(eigen_full):
    '''

    :param eigen_full:
    :return:
    '''
    lamb1=eigen_full[...,1]
    lamb2=eigen_full[...,0]
    #lamb3=eigen_full[:,:,0]
    lamb_sum=np.sum(eigen_full, axis=3)# axis=3 for full stack computation; axis=2 for one by one computation
    p1=lamb1/lamb_sum
    p2=lamb2/lamb_sum
    #p3=lamb3/lamb_sum
    #return np.dstack((p1,p2,p3))
    return [p1,p2]

def entropy_cal(eigen_full):
    '''

    :param eigen_full:
    :return:
    '''
    p=get_p_value(eigen_full)
    p0_log=np.log(p[0])/math.log(2)
    #plt.imshow(p[1], cmap='gray')
    #plt.show()
    p1_log=np.log(p[1])/math.log(2)
    #p2_log=np.log(p[2])/math.log(3)
    ent=-1*(p[0]*p0_log+p[1]*p1_log)#+p[2]*p2_log)
    return ent

def mean_alpha_angle(coh_matrix):
    '''

    :param coh_matrix:
    :return:
    '''
    #p = get_p_value(eigen_full)
    p,v = np.linalg.eig(coh_matrix)
    #print(v[100,100])
    #return 0
    alpha_0 = np.arccos(np.absolute(np.mean(v[...,0,:], axis = 2)))
    alpha_1 = np.arccos(np.absolute(np.mean(v[...,1,:], axis = 2)))
    #alpha_2 = np.arccos(np.absolute(np.mean(v[...,2,:], axis = 2)))
    mean_alpha = (p[0]*alpha_0 + p[1]*alpha_1) * 180/np.pi #+ p[2]*alpha_2
    return mean_alpha

def plot_clipped(arr, per_min, per_max):
    '''

    :param arr:
    :param per_min:
    :param per_max:
    :return:
    '''
    return np.clip(arr, *np.percentile(arr, (per_min, per_max)))

def get_co_pol_phase_diff_sd(vv_arr_stack, hh_arr_stack, AVG_WIN_SIZE = 5):
    '''

    :param vv_arr_stack:
    :param hh_arr_stack:
    :param AVG_WIN_SIZE:
    :return:
    '''
    
    shp_MN = vv_arr_stack.shape[:-1]
    
    epochs = vv_arr_stack.shape[-1]
    #kern = kernal(AVG_WIN_SIZE)
    
    shp_MN = np.array(shp_MN) - AVG_WIN_SIZE +1
    
    phase_diff_mean_squared = test_convolve_3d(np.angle(vv_arr_stack) - np.angle(hh_arr_stack), AVG_WIN_SIZE, dtype=np.float32)**2
    phase_diff_squared_mean = (np.angle(vv_arr_stack) - np.angle(hh_arr_stack))**2#test_convolve_3d((np.angle(vv_arr_stack) - np.angle(hh_arr_stack))**2, AVG_WIN_SIZE, dtype=np.float32)
    return np.sqrt(phase_diff_squared_mean - phase_diff_mean_squared)

def co_pol_power_ratio_1(cov_arr):
    '''

    :param cov_arr:
    :return:
    '''
    return cov_arr[...,0,0]/cov_arr[...,1,1]

def co_pol_cross_product(cov_arr):
    '''

    :param cov_arr:
    :return:
    '''
    return cov_arr[...,0,1]
    
def co_pol_diff(cov_arr):
    '''

    :param cov_arr:
    :return:
    '''
    return cov_arr[...,0,0]-cov_arr[...,1,1]

def co_pol_sum(cov_arr):
    '''

    :param cov_arr:
    :return:
    '''
    return cov_arr[...,0,0]+cov_arr[...,1,1]

def co_pol_correlation(cov_arr):
    '''

    :param cov_arr:
    :return:
    '''
    return cov_arr[...,0,1]/np.sqrt(cov_arr[...,0,0]*cov_arr[...,1,1])

def get_avg_cov_mat(vv_arr_stack, hh_arr_stack, AVG_WIN_SIZE = 5, PADDING=True):
    '''

    :param vv_arr_stack:
    :param hh_arr_stack:
    :param AVG_WIN_SIZE:
    :param PADDING:
    :return:
    '''

    shp_MN = vv_arr_stack.shape[:-1]
    
    epochs = vv_arr_stack.shape[-1]
    
    shp_MN = np.array(shp_MN) - AVG_WIN_SIZE +1
    cov_arr = np.dstack((\
        test_convolve_3d(np.absolute(hh_arr_stack)**2, AVG_WIN_SIZE),\
            test_convolve_3d(hh_arr_stack* np.conj(vv_arr_stack), AVG_WIN_SIZE),\
                test_convolve_3d(vv_arr_stack* np.conj(hh_arr_stack), AVG_WIN_SIZE),\
                    test_convolve_3d(np.absolute(vv_arr_stack)**2, AVG_WIN_SIZE)))\
                        .reshape(shp_MN[0], shp_MN[1],4,epochs).transpose(0,1,3,2)\
                            .reshape(shp_MN[0], shp_MN[1],epochs,2,2)
                        
    #cov_arr = np.dstack((\
        #np.absolute(vv_arr_stack)**2,\
            #vv_arr_stack* np.conj(hh_arr_stack), \
                #hh_arr_stack* np.conj(vv_arr_stack), \
                    #np.absolute(hh_arr_stack)**2, ))\
                        #.reshape(shp_MN[0], shp_MN[1],4,epochs).transpose(0,1,3,2)\
                            #.reshape(shp_MN[0], shp_MN[1],epochs,2,2)
                        
    if (PADDING & (AVG_WIN_SIZE%2 !=0)):
        cov_arr = np.pad(cov_arr, pad_width = ((AVG_WIN_SIZE//2, AVG_WIN_SIZE//2), (AVG_WIN_SIZE//2, AVG_WIN_SIZE//2), \
            (0,0),(0,0),(0,0)))
    
    print('cov_arr.shape', cov_arr.shape)
    return cov_arr
    
    # for i in range(epochs):
    #     #plt.imshow(np.log10(np.absolute(cov_arr[...,i,0,0])), cmap='gray')
    #     #plt.show()
    #
    #     eigen_vals = np.sort(np.absolute(LA.eigvals(cov_arr)), axis=3)
    #     print(eigen_vals.shape)
    #     ent = entropy_cal(eigen_vals[...,i,:])
    #
    #     plt.subplot(3,3,1)
    #     plt.imshow(np.absolute(co_pol_correlation(cov_arr)[...,i]), cmap='gray')
    #     plt.title('Co-pol corr. coeff.')
    #     plt.subplot(3,3,2)
    #     plt.imshow(plot_clipped(10*np.log10(np.absolute(co_pol_cross_product(cov_arr)[...,i])), 1, 99), cmap='gray')
    #     plt.title('Co-pol cross product')
    #     plt.subplot(3,3,3)
    #     plt.imshow(plot_clipped(10*np.log10(np.absolute(co_pol_diff(cov_arr)[...,i])), 1, 99), cmap='gray')
    #     plt.title('Co-pol diff.')
    #     plt.subplot(3,3,4)
    #     plt.imshow(plot_clipped(np.absolute(co_pol_power_ratio_1(cov_arr)[...,i]), 1, 99), cmap='gray')
    #     plt.title('Co-pol power ratio')
    #
    #     plt.subplot(3,3,5)
    #     plt.imshow(ent, cmap='gray')
    #     plt.title('Entropy')
    #     #plt.colorbar()
    #     #break
    #
    #     plt.subplot(3,3,6)
    #     plt.imshow(10*np.log10(np.absolute(cov_arr[...,i,0,0])), cmap='gray')
    #     plt.title('HH intesity')
    #     plt.subplot(3,3,7)
    #     plt.imshow(10*np.log10(np.absolute(cov_arr[...,i,1,1])), cmap='gray')
    #     plt.title('VV intesity')
    #
    #     plt.show()
    
    #alpha_ang = mean_alpha_angle(coh_matrix)
    
    #alpha = mean_alpha_angle(cov_arr[:,:,0,...])
    #print(alpha)

def plot_decomposition_RGB(slc_arr, clip_extremes):
    '''

    :param slc_arr:
    :param clip_extremes:
    :return:
    '''
    #clip_extremes=True
    #r=hist_stretch_all(slc_arr[...,0], 0, clip_extremes)
    #b=hist_stretch_all(slc_arr[...,0]/slc_arr[...,1], 0, clip_extremes)
    #g=hist_stretch_all(slc_arr[...,1], 0, clip_extremes)
    #adugna's color profile
    b=hist_stretch_all(((slc_arr[...,0]+slc_arr[...,1])**2)/2, 0, clip_extremes)
    r=hist_stretch_all(slc_arr[...,0]**2, 0, clip_extremes)
    g=hist_stretch_all(slc_arr[...,1]**2, 0, clip_extremes)
    plot_arr =  np.dstack((r,g,b))
    
    plt.imshow(plot_arr)
    plt.show()

def read_rdr_coded_file(filename, lines, pixels, dtype=np.float32, CROPPING=False, CRP_LIST=[10,20,10,20], OFFSET=True, OFFST_lp=[1,37], MASKING=False):
    rdr_coded_arr_orig = np.fromfile(filename, dtype=dtype).reshape(lines, pixels)
    rdr_coded_arr = np.zeros((lines, pixels))
    if OFFSET:
        #CRP_LIST = [CRP_LIST[0]+OFFST_lp[0],\
            #CRP_LIST[1]+OFFST_lp[0],\
                #CRP_LIST[2]+OFFST_lp[1],\
                    #CRP_LIST[3]+OFFST_lp[1]]
        rdr_coded_arr[:-OFFST_lp[0], :-OFFST_lp[1]] = rdr_coded_arr_orig[OFFST_lp[0]:, OFFST_lp[1]:]
    else:
        rdr_coded_arr = rdr_coded_arr_orig
    #apply crop
    if CROPPING:
        rdr_coded_arr = rdr_coded_arr[CRP_LIST[0]:CRP_LIST[1],CRP_LIST[2]:CRP_LIST[3]]

    if MASKING:
        rdr_coded_arr = ma.masked_where(rdr_coded_arr==0, rdr_coded_arr)
    return rdr_coded_arr

def main():
    parser = argparse.ArgumentParser(description="Generate NetCDF with SAR attributes (AlignSAR workflow)")
    parser.add_argument('--doris_stack_dir_VV', required=True, help='Path to Doris VV stack directory')
    parser.add_argument('--doris_stack_dir_VH', required=True, help='Path to Doris VH stack directory')
    parser.add_argument('--master_date', type=str, required=True, help='Master date (YYYYMMDD)')
    parser.add_argument('--crop_first_line', type=int, default=500, help='Crop start line index (azimuth)')
    parser.add_argument('--crop_last_line', type=int, default=1440, help='Crop end line index (azimuth)')
    parser.add_argument('--crop_first_pixel', type=int, default=16000, help='Crop start pixel index (range)')
    parser.add_argument('--crop_last_pixel', type=int, default=18350, help='Crop end pixel index (range)')
    parser.add_argument('--lines_full', type=int, default=2842, help='Total number of lines in raw file')
    parser.add_argument('--pixels_full', type=int, default=22551, help='Total number of pixels in raw file')
    parser.add_argument('--netcdf_lines', type=int, default=2350, help='Number of lines in NetCDF output')
    parser.add_argument('--netcdf_pixels', type=int, default=940, help='Number of pixels in NetCDF output')
    parser.add_argument('--lam_file', required=True, help='Path to lam.raw (longitude)')
    parser.add_argument('--phi_file', required=True, help='Path to phi.raw (latitude)')
    parser.add_argument('--sar_folder_path', required=True, help='Path to SAR folder')
    parser.add_argument('--max_images', type=int, default=30, help='Maximum number of images to process')
    args = parser.parse_args()

    CROPPING = True
    CRP_LIST = [args.crop_first_line, args.crop_last_line, args.crop_first_pixel, args.crop_last_pixel]

    # Get acquisition dates
    dates = get_dates(args.doris_stack_dir_VV, args.master_date)[:args.max_images]

    # Extract VV/VH stacks
    vv_arr_stack = get_stack(dates, args.master_date, args.doris_stack_dir_VV, 'cpx',
                             crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')
    vh_arr_stack = get_stack(dates, args.master_date, args.doris_stack_dir_VH, 'cpx',
                             crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')

    # Read longitude/latitude arrays
    lam_merge_arr = freadbk(args.lam_file, 1, 1, args.lines_full, args.pixels_full,
                            'float32', args.lines_full, args.pixels_full)
    phi_merge_arr = freadbk(args.phi_file, 1, 1, args.lines_full, args.pixels_full,
                            'float32', args.lines_full, args.pixels_full)

    # Crop longitude/latitude arrays
    lon = lam_merge_arr[args.crop_first_line:args.crop_last_line,
                        args.crop_first_pixel:args.crop_last_pixel]
    lat = phi_merge_arr[args.crop_first_line:args.crop_last_line,
                        args.crop_first_pixel:args.crop_last_pixel]

    # Example: create an empty NetCDF file with specified dimensions
    netcdf_name = nc.Dataset('example_output.nc', 'w', format='NETCDF4')
    netcdf_name.createDimension('lines (azimuth)', args.netcdf_lines)
    netcdf_name.createDimension('pixels (range)', args.netcdf_pixels)
    netcdf_name.close()

"""
Example command to run this script:

python signature_extraction.py \
    --doris_stack_dir_VV /data/stack_vv/ \
    --doris_stack_dir_VH /data/stack_vh/ \
    --master_date 20220214 \
    --crop_first_line 500 --crop_last_line 1440 \
    --crop_first_pixel 16000 --crop_last_pixel 18350 \
    --lines_full 2842 --pixels_full 22551 \
    --netcdf_lines 2350 --netcdf_pixels 940 \
    --lam_file /data/geo/lam.raw \
    --phi_file /data/geo/phi.raw \
    --sar_folder_path /data/sar/ \
    --max_images 30
"""
if __name__ == '__main__':
    main()
