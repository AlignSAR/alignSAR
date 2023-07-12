

import os,sys
#from resdata import ResData
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import numpy.ma as ma
from utils import *

def multi_temp_spk_filt(slc_arr, window_size=3):
    """
    
    Arg: slc_arr, shape: (lines * pixels * epochs)
    slc_arr is a coregistered stack of arrays
    Returns:
    speckle filtered array
    """
    #step 1: calc. sigma naught
    #sigma_0_slc_arr = 10 * np.log10(np.absolute(slc_arr))
    sigma_0_slc_arr = np.absolute(slc_arr)
    
    #step 2: calc. spatial mean
    #window_size = 3
    #shp_arr = shp_arr.shape
    #E_0 = test_convolve(sigma_0_slc_arr[...,0], kernal(window_size))
    
    #step 3: subset amplitude image
    
    sigma_0_slc_arr_crop = sigma_0_slc_arr[window_size//2:-(window_size//2), window_size//2:-(window_size//2),...]
    
    #step 4: apply formula
    image_sum = np.zeros(sigma_0_slc_arr_crop.shape[:-1])
    E_all = np.zeros(sigma_0_slc_arr_crop.shape)
    
    for i in range(slc_arr.shape[-1]):
        E_i = test_convolve(sigma_0_slc_arr[...,i], kernal(window_size))
        image_sum += sigma_0_slc_arr_crop[...,i]/E_i
        E_all[...,i] = E_i
    
    J_all = E_all.transpose(2,0,1) * image_sum /slc_arr.shape[-1]
    
    return J_all.transpose(1,2,0)


if __name__=='__main__':
    doris_stack_dir = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vv/'
    #doris_stack_dir_HH = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_33_WaddenSea_HH/stack/'
    master_date = '20220214'
    CROPPING = True
    CRP_LIST = [500, 1440, 15000, 17350] #[l0,lN,p0,pN]
    #POL = 'VV'
    MAX_IMAGES = 10
    AVG_WIN_SIZE=9
    
    #Get the dates
    dates = get_dates(doris_stack_dir, master_date)[:MAX_IMAGES]
    print(dates)
    #Extract the stack array
    vv_arr_stack = get_stack(dates, doris_stack_dir, crop_switch=CRP_LIST, crop_list=CRP_LIST)
    #hh_arr_stack = get_stack(dates, doris_stack_dir_HH, crop_switch=CRP_LIST, crop_list=CRP_LIST)
    
    mrm = make_mrm(vv_arr_stack)
    J_all = multi_temp_spk_filt(vv_arr_stack, window_size=AVG_WIN_SIZE)
    J_all_log = 10*np.log10(J_all)
    
    PLOT_IMAGES=1
    
    for i in list(range(J_all.shape[-1]))[:PLOT_IMAGES]:
        plt.subplot(PLOT_IMAGES, 3, 3*i+1)
        plt.imshow(plot_clipped(10*np.log10(np.absolute(vv_arr_stack[...,i])), 1, 99), cmap='gray')
        
        plt.subplot(PLOT_IMAGES, 3, 3*i+2)
        plt.imshow(plot_clipped(10*np.log10(mrm), 1,99), cmap='gray')
        
        plt.subplot(PLOT_IMAGES, 3, 3*i+3)
        #plt_arr = ma.masked_invalid(slc_arr_t_filt)
        #print(np.nanpercentile(plt_arr, (1, 99)))
        #plt.imshow(np.clip(plt_arr, *np.nanpercentile(plt_arr, (1, 99))), cmap='gray')
        plt.imshow(plot_clipped(J_all_log[...,i], 1,99), cmap='gray')
        #plt.colorbar()
        
    plt.show()
    
    
