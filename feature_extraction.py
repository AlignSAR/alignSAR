import os,sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import numpy.ma as ma
from utils import *
import numpy.linalg as LA
import math

def get_p_value(eigen_full):
    lamb1=eigen_full[...,1]
    lamb2=eigen_full[...,0]
    #lamb3=eigen_full[:,:,0]
    lamb_sum=np.sum(eigen_full, axis=2)# axis=3 for full stack computation; axis=2 for one by one computation
    p1=lamb1/lamb_sum
    p2=lamb2/lamb_sum
    #p3=lamb3/lamb_sum
    #return np.dstack((p1,p2,p3))
    return [p1,p2]

def entropy(eigen_full):
    p=get_p_value(eigen_full)
    p0_log=np.log(p[0])/math.log(2)
    #plt.imshow(p[1], cmap='gray')
    #plt.show()
    p1_log=np.log(p[1])/math.log(2)
    #p2_log=np.log(p[2])/math.log(3)
    ent=-1*(p[0]*p0_log+p[1]*p1_log)#+p[2]*p2_log)
    return ent

def mean_alpha_angle(coh_matrix):
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
    return np.clip(arr, *np.percentile(arr, (per_min, per_max)))

def get_co_pol_phase_diff_sd(vv_arr_stack, hh_arr_stack, AVG_WIN_SIZE = 5):
    
    shp_MN = vv_arr_stack.shape[:-1]
    
    epochs = vv_arr_stack.shape[-1]
    #kern = kernal(AVG_WIN_SIZE)
    
    shp_MN = np.array(shp_MN) - AVG_WIN_SIZE +1
    
    phase_diff_mean_squared = test_convolve_3d(np.angle(vv_arr_stack) - np.angle(hh_arr_stack), AVG_WIN_SIZE, dtype=np.float32)**2
    phase_diff_squared_mean = (np.angle(vv_arr_stack) - np.angle(hh_arr_stack))**2#test_convolve_3d((np.angle(vv_arr_stack) - np.angle(hh_arr_stack))**2, AVG_WIN_SIZE, dtype=np.float32)
    return np.sqrt(phase_diff_squared_mean - phase_diff_mean_squared)

def co_pol_power_ratio_1(cov_arr):
    return cov_arr[...,0,0]/cov_arr[...,1,1]

def co_pol_cross_product(cov_arr):
    return cov_arr[...,0,1]
    
def co_pol_diff(cov_arr):
    return cov_arr[...,0,0]-cov_arr[...,1,1]

def co_pol_sum(cov_arr):
    return cov_arr[...,0,0]+cov_arr[...,1,1]

def co_pol_correlation(cov_arr):
    return cov_arr[...,0,1]/np.sqrt(cov_arr[...,0,0]*cov_arr[...,1,1])

def get_avg_cov_mat(vv_arr_stack, hh_arr_stack, AVG_WIN_SIZE = 5, PADDING=False):

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
    #return cov_arr
    
    for i in range(epochs):
        #plt.imshow(np.log10(np.absolute(cov_arr[...,i,0,0])), cmap='gray')
        #plt.show()
        
        eigen_vals = np.sort(np.absolute(LA.eigvals(cov_arr)), axis=3)
        print(eigen_vals.shape)
        ent = entropy(eigen_vals[...,i,:])
        
        plt.subplot(3,3,1)
        plt.imshow(np.absolute(co_pol_correlation(cov_arr)[...,i]), cmap='gray')
        plt.title('Co-pol corr. coeff.')
        plt.subplot(3,3,2)
        plt.imshow(plot_clipped(10*np.log10(np.absolute(co_pol_cross_product(cov_arr)[...,i])), 1, 99), cmap='gray')
        plt.title('Co-pol cross product')
        plt.subplot(3,3,3)
        plt.imshow(plot_clipped(10*np.log10(np.absolute(co_pol_diff(cov_arr)[...,i])), 1, 99), cmap='gray')
        plt.title('Co-pol diff.')
        plt.subplot(3,3,4)
        plt.imshow(plot_clipped(np.absolute(co_pol_power_ratio_1(cov_arr)[...,i]), 1, 99), cmap='gray')
        plt.title('Co-pol power ratio')
        
        plt.subplot(3,3,5)
        plt.imshow(ent, cmap='gray')
        plt.title('Entropy')
        #plt.colorbar()
        #break
        
        plt.subplot(3,3,6)
        plt.imshow(10*np.log10(np.absolute(cov_arr[...,i,0,0])), cmap='gray')
        plt.title('HH intesity')
        plt.subplot(3,3,7)
        plt.imshow(10*np.log10(np.absolute(cov_arr[...,i,1,1])), cmap='gray')
        plt.title('VV intesity')
        
        plt.show()
    
    #alpha_ang = mean_alpha_angle(coh_matrix)
    
    #alpha = mean_alpha_angle(cov_arr[:,:,0,...])
    #print(alpha)

def plot_decomposition_RGB(slc_arr, clip_extremes):
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

if __name__=='__main__':
    doris_stack_dir_VV = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vv/'
    doris_stack_dir_VH = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vh/'
    #paz_doris_stack = '/media/anurag/AK_WD/PAZ_Processing/stack'
    master_date = 20200330#'20220214'#'20170117'
    CROPPING = True
    CRP_LIST = [500, 1440, 16000, 18350]#[2000, 3500, 8500, 10000]#
    MAX_IMAGES = 30
    SP_AVG_WIN_SIYE = 3
    
    #Get the dates
    dates = get_dates(paz_doris_stack, master_date)[:MAX_IMAGES]
    print(dates)
    #Extract the stack array
    vv_arr_stack = get_stack(dates, paz_doris_stack, crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')
    vh_arr_stack = get_stack(dates, doris_stack_dir_VH, crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1')
    
    np.save('groningen_vv_cpx_amp.npy', vv_arr_stack)
    np.save('groningen_vh_cpx_amp.npy', vh_arr_stack)
    
    plot_decomposition_RGB(np.dstack((np.absolute(vv_arr_stack).mean(2), np.absolute(vh_arr_stack).mean(2))), clip_extremes=True)
    
    cov_arr = get_avg_cov_mat(vv_arr_stack, vh_arr_stack, AVG_WIN_SIZE = SP_AVG_WIN_SIYE, PADDING=False)
    
