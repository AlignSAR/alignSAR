import os,sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import numpy.ma as ma
from alignsar_utils import *
import numpy.linalg as LA
import math
import xarray as xr
from Meta_info_extraction_global_local import *
import netCDF4 as nc

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

if __name__=='__main__':
    doris_stack_dir_VV = '/media/xu/Elements2/AlignSAR/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vv/'
    doris_stack_dir_VH = '/media/xu/Elements2/AlignSAR/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vh/'
    #paz_doris_stack = '/media/anurag/AK_WD/PAZ_Processing/stack'
    master_date = 20220214 #'20220214'#'20170117'
    CROPPING = True
    CRP_LIST = [500, 1440, 16000, 18350]#[2000, 3500, 8500, 10000]# [first line, last line, first pixel, last pixel]
    MAX_IMAGES = 30
    # SP_AVG_WIN_SIYE = 3
    map_type = 'cpx' # 'cpx', 'ifg', 'coh'
    
    #Get the dates
    dates = get_dates(doris_stack_dir_VV, master_date)[:MAX_IMAGES]
    print(dates)
    #Extract the stack array
    vv_arr_stack = get_stack(dates, master_date, doris_stack_dir_VV, map_type, crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')
    vh_arr_stack = get_stack(dates, master_date, doris_stack_dir_VH, map_type, crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')

    top10_path = '/media/xu/Elements2/AlignSAR/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vv/20220214/'
    # top10NL layers' file name
    top10_building_file_name = top10_path + 'top10nl_gebouw_vlak_radarcoded.raw'
    top10_railway_file_name = top10_path + 'top10nl_spoorbaandeel_lijn_radarcoded.raw'
    top10_water_file_name = top10_path + 'top10nl_waterdeel_vlak_radarcoded.raw'
    top10_road_file_name = top10_path + 'top10nl_wegdeel_vlak_radarcoded.raw'
    # read rdr-coded top10nl data into array
    building_arr = read_rdr_coded_file(top10_building_file_name, 2842,22551,dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST, MASKING=False, OFFSET=True, OFFST_lp=[1,12])
    railway_arr = read_rdr_coded_file(top10_railway_file_name, 2842,22551,dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST, MASKING=False, OFFSET=True, OFFST_lp=[1,12])
    water_arr = read_rdr_coded_file(top10_water_file_name, 2842,22551,dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST, MASKING=False, OFFSET=True, OFFST_lp=[1,12])
    road_arr = read_rdr_coded_file(top10_road_file_name, 2842,22551,dtype=np.float32, CROPPING=CROPPING, CRP_LIST=CRP_LIST, MASKING=False, OFFSET=True, OFFST_lp=[1,12])

    # read geo lon lat
    lam_dataFilename = '/media/xu/Elements2/AlignSAR/Doris_Processing/Groningen_Ling/geo_lonlat/merged_lan_phi/lam.raw'
    phi_dataFilename = '/media/xu/Elements2/AlignSAR/Doris_Processing/Groningen_Ling/geo_lonlat/merged_lan_phi/phi.raw'
    lam_merge_arr = freadbk(lam_dataFilename,1,1,2842,22551,'float32', int(2842), int(22551))
    phi_merge_arr = freadbk(phi_dataFilename,1,1,2842,22551,'float32', int(2842), int(22551))

    # calculate the covariance matirx for intensity and pol information calcualtion
    cov_arr = get_avg_cov_mat(vv_arr_stack, vh_arr_stack,AVG_WIN_SIZE = 3, PADDING=True)

    # VV amplitude (linear)
    vv_amp = np.abs(vv_arr_stack)
    # VH amplitude (linear)
    vh_amp = np.abs(vh_arr_stack)
    # VV ifg (radians)
    vv_ifg = np.angle(get_stack(dates, master_date, doris_stack_dir_VV, 'ifg', crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1'))
    # VV coh
    vv_coh = get_stack(dates, master_date, doris_stack_dir_VV, 'coh', crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1').real  # imaginary part is 0
    # Intensity summation |S_vv|^2 + |S_vh|^2
    intensity_sum = np.square(vv_amp) + np.square(vh_amp)
    # Intensity difference (cross-pol difference) |S_vv|^2 - |S_vh|^2
    intensity_diff = np.square(vv_amp) - np.square(vh_amp)
    # Intensity ratio (cross-pol power ratio) |S_vv|^2 / |S_vh|^2
    intensity_ratio = np.square(vv_amp) / np.square(vh_amp)
    # cross-pol correlation coefficient
    cross_pol_corr_coeff = np.absolute(co_pol_correlation(cov_arr))
    # cross-pol cross product
    cross_pol_cross_product = np.absolute(co_pol_diff(cov_arr))
    # entropy
    entropy = entropy_cal(np.sort(np.absolute(LA.eigvals(cov_arr)), axis = 3))  # change axis = 3 in line 19 in 'get_p_value' function for whole stack
    # lon
    lon = lam_merge_arr[500:1440, 16000:18350]
    # lat
    lat = phi_merge_arr[500:1440, 16000:18350]

    # create signature and attribute list
    signature_list = ['VV amplitude (linear)', 'VH amplitude (linear)', 'VV interferometric phase (radians)', 'VV coherence', 'Intensity summation',
                             'Intensity difference (dual-pol difference)', 'Intensity ratio (dual-pol power ratio)', 'Cross-pol correlation coefficient',
                             'Cross-pol cross product', 'Entropy', 'Buildings', 'Railways', 'Water', 'Roads', 'Lon', 'Lat']
    local_attributes_list = [VV_amplitude_attr, VH_amplitude_attr, VV_interferometric_phase_attr, VV_coherence_attr, Intensity_summation_attr,
                             Intensity_difference_attr, Intensity_ratio_attr, Cross_pol_correlation_coefficient_attr, Cross_pol_cross_product_attr,
                             Entropy_attr, Buildings_attr, Railways_attr, Water_attr, Roads_attr, Lon_attr, Lat_attr]

    sar_folder_path = '/media/xu/Elements2/AlignSAR/Doris_Processing/Doris_Processing_36_Groningen/sar_data_2022/'

    epochs=7
    for i in range(epochs):
        data_name = 'Groningen_netcdf_data_'+dates[i]
        netcdf_name = 'Groningen_netcdf_'+dates[i]
        data_name = np.transpose(np.stack((vv_amp[:,:,i], vh_amp[:,:,i], vv_ifg[:,:,i], vv_coh[:,:,i], intensity_sum[:,:,i], intensity_diff[:,:,i],
                                                          intensity_ratio[:,:,i],cross_pol_corr_coeff[:,:,i], cross_pol_cross_product[:,:,i], entropy[:,:,i],
                                                          building_arr, railway_arr, water_arr, road_arr, lon, lat)))

        # create netcdf file
        netcdf_name = nc.Dataset(netcdf_name+'_full_attributes.nc', 'w', format='NETCDF4')
        # assign global attributes
        global_attributes = get_global_attribute(sar_folder_path,i,0)
        # set layer size
        netcdf_name.createDimension('lines (azimuth)', 2350)
        netcdf_name.createDimension('pixels (range)', 940)
        # set global attributes
        for attr_name, attr_value in global_attributes.items():
            setattr(netcdf_name, attr_name, attr_value)
        # for 14 layers, assign each layer's data and local attribute to the netcdf
        layer_num = 16
        for i in range(layer_num):
            # when define the data format and data frame. the top10nl layers should be float 64, the others are float 32
            if signature_list[i] == 'Buildings' or signature_list[i] == 'Railways' or signature_list[i] == 'Water' or signature_list[i] == 'Roads':
                layer = netcdf_name.createVariable(signature_list[i],'f8',('lines (azimuth)', 'pixels (range)'))
            else:
                layer = netcdf_name.createVariable(signature_list[i],'f4',('lines (azimuth)', 'pixels (range)'))
            # assign the local attribute for each layer
            for loc_attr_name, loc_attr_value in local_attributes_list[i].items():
                setattr(layer, loc_attr_name, loc_attr_value)
            # assign the layer data to the netcdf
            layer[:] = data_name[:,:,i]
        netcdf_name.close()


# test = nc.Dataset('Groningen_netcdf_20220109_full_attributes.nc')
# test.close()
