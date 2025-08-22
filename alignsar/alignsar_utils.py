#!/usr/bin/env python3
import argparse
import numpy as np
import os, sys
from .resdata import ResData
from scipy import signal
import numpy.ma as ma




def RI2cpx(R, I, cpxfile, intype=np.float32):
    """Convert real and imaginary binary files to a complex number binary file.
    
    Args:
        R (string or np.ndarray): path to the binary file with real values, or directly loaded as numpy ndarray
        I (string or np.ndarray): path to the binary file with imaginary values, or directly loaded as numpy ndarray
        cpxfile (string or None): path to the binary file for complex output (the output will be as complex64). if None, it will only return the cpxarray
        intype (type): data type of the binary file. np.float32 or np.float64 if needed.
    
    Returns:
        np.array: this array must be reshaped if needed
    """
    # we may either load R, I from file:
    if type(R) == type('str'):
        r = np.fromfile(R, dtype=intype)
        i = np.fromfile(I, dtype=intype)
    else:
        r = R.astype(intype).ravel()
        i = I.astype(intype).ravel()
    if cpxfile:
        cpx = np.zeros(len(r)+len(i))
        cpx[0::2] = r
        cpx[1::2] = i
        cpx.astype(np.float32).tofile(cpxfile)
    return r + 1j*i


def freadbk(path_file, line_start=1, pixel_start=1, nofLines=None, nofPixels=None, dt='float32', lines=0, pixels=0, memmap=True):
    # First use memmap to get a memory map of the full file, than extract the requested part.

    if dt == 'cpxint16':
        dtype = np.dtype([('re', np.int16), ('im', np.int16)])
        file_dat = np.memmap(path_file, dtype=dtype, mode='r', shape=(lines, pixels)).view(np.int16).astype(np.float32).view(np.complex64)
        data = file_dat[line_start - 1:line_start + nofLines - 1, pixel_start - 1:pixel_start + nofPixels - 1].astype(
            'complex64', subok=False)
    elif dt == 'cpxshort':

        file_dat = np.memmap(path_file, dtype=np.dtype(np.float16), mode='r', shape=(lines, pixels * 2))
        data = 1j * file_dat[:, 1::2].astype('float32', subok=False)
        data += file_dat[:, 0::2].astype('float32', subok=False)
        data = data[line_start - 1:line_start + nofLines - 1, pixel_start - 1:pixel_start + nofPixels - 1]

    else:
        dt = np.dtype(dt)
        file_dat = np.memmap(path_file, dtype=dt, mode='r', shape=(lines, pixels))
        data = file_dat[line_start - 1:line_start + nofLines - 1, pixel_start - 1:pixel_start + nofPixels - 1].astype(
            dt, subok=False)

    return data

def test_convolve_3d(arr, AVG_WIN_SIZE, dtype=np.complex64):
    '''
    arr has a 3rd dim and conv is done per element in the 3rd dimension
    kernal should be 2 dimensional
    '''
    kern = kernal(AVG_WIN_SIZE)
    shp = arr.shape
    ker_shp = kern.shape
    grad = np.empty((shp[0]-ker_shp[0]+1,\
        shp[1]-ker_shp[1]+1,\
            shp[-1]), dtype = dtype)
    for i in range(shp[-1]):
        grad[...,i] = signal.convolve2d(arr[...,i], kern, boundary='symm', mode='valid')
    return grad

def test_convolve(arr, kernal):
    grad = signal.convolve2d(arr, kernal, boundary='symm', mode='valid')
    return grad

def kernal(window_size):
    k=np.ones(window_size*window_size).reshape(window_size, window_size)
    normalize_k=k/(window_size**2)
    return normalize_k

def hist_stretch_all(arr, bits, clip_extremes):
    #bands=arr.shape[-1]
    
    n=arr.shape
    #new_arr=arr
    per=np.percentile(arr,[5, 95])
    per_max=per[1]
    per_min=per[0]
    min_arr=np.full(n, per_min)
    max_arr=np.full(n, per_max)
    if(clip_extremes==False):
        new_arr=arr
    else:
        new_arr=np.maximum(min_arr, np.minimum(max_arr, arr))
        
    #return new_arr
    if(bits==0):
        min_=np.amin(new_arr)
        max_=np.amax(new_arr)
        new_arr=(new_arr-min_)/(max_-min_)
    else:
        new_arr=np.floor((2**bits-1)*(new_arr-per_min)/(per_max-per_min))
    return new_arr



def get_slv_arr_shape(doris_stack_dir, date, sensor='s1', swath='1', burst='1'):
    
    if sensor =='s1':
        slv_resFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst,'slave.res')
    else:
        slv_resFilename = os.path.join(doris_stack_dir, date,'slave.res')
    
    slv_res = ResData(slv_resFilename)
    
    l0 = int(slv_res.processes['resample']['First_line (w.r.t. original_master)'])
    lN = int(slv_res.processes['resample']['Last_line (w.r.t. original_master)'])
    p0 = int(slv_res.processes['resample']['First_pixel (w.r.t. original_master)'])
    pN = int(slv_res.processes['resample']['Last_pixel (w.r.t. original_master)'])
    
    Naz_res = lN-l0+1
    Nrg_res = pN-p0+1
    
    return (Naz_res, Nrg_res)


def get_cropped_image(choice_amp_int, doris_stack_dir, date, amp_file_name='slave_rsmp.raw', ifgs_file_name = 'cint_srd.raw', coh_file_name = 'coherence.raw', crop_switch=False, crop_list=[], sensor='s1', swath_burst=False, swath='1', burst='1'):
    '''
    Function to read a subset of of slave_rsmp.raw or cint_srd.raw
    Args:
    
    
    '''
    if (sensor=='s1' & swath_burst):  #change '&' to 'and' when using python 3.8, '&' is for python 3.10
        amp_dataFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst, amp_file_name)
        ifgs_dataFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst, ifgs_file_name)
        coh_dataFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst, coh_file_name)
        
        slv_resFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst, 'slave.res')
        ifgs_resFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst, 'ifgs.res')
        coh_resFilename = os.path.join(doris_stack_dir, date, 'swath_'+swath, 'burst_'+burst, 'coherence.raw')
    else:
        amp_dataFilename = os.path.join(doris_stack_dir, date, amp_file_name)
        ifgs_dataFilename = os.path.join(doris_stack_dir, date, ifgs_file_name)
        coh_dataFilename = os.path.join(doris_stack_dir, date, coh_file_name)
        
        slv_resFilename = os.path.join(doris_stack_dir, date,'slave.res')
        ifg_resFilename = os.path.join(doris_stack_dir, date,'ifgs.res')
        coh_resFilename = os.path.join(doris_stack_dir, date,'coherence.raw')
    
    
    slv_res = ResData(slv_resFilename)
    #ifg_res = ResData(ifg_resFilename)
    
    l0 = int(slv_res.processes['resample']['First_line (w.r.t. original_master)'])
    lN = int(slv_res.processes['resample']['Last_line (w.r.t. original_master)'])
    p0 = int(slv_res.processes['resample']['First_pixel (w.r.t. original_master)'])
    pN = int(slv_res.processes['resample']['Last_pixel (w.r.t. original_master)'])
    
    # Image size
    Naz_res = lN-l0+1
    Nrg_res = pN-p0+1
    if crop_switch:
        lines = crop_list[1]-crop_list[0]
        pixels = crop_list[3]-crop_list[2]
    else:
        lines = Naz_res
        pixels = Nrg_res
        crop_list = [1, Naz_res, 1, Nrg_res]
    
    print('Reading {} data from date {}. l0, p0, lines, pixels = {}, {}, {}, {}'.format(choice_amp_int, date, crop_list[0], crop_list[2], lines, pixels))
    #print(Naz_res, Nrg_res)
    if (choice_amp_int == 'amp'):
        arr = freadbk(amp_dataFilename, 
                    crop_list[0],#+1, 
                    crop_list[2], 
                    lines,pixels,
                    'complex64', int(Naz_res), int(Nrg_res))
    if (choice_amp_int == 'ifgs'):
        arr = freadbk(ifgs_dataFilename, 
                    crop_list[0],#+1, 
                    crop_list[2], 
                    lines,pixels,
                    'complex64', int(Naz_res), int(Nrg_res))
    return arr
        
def get_dates(doris_stack_dir, master_date):
    #master_date = master_date.strftime("%Y%m%d")
    dates = sorted([l for l in [j for k,j,i in os.walk(doris_stack_dir)][0] if (len(l)==8)])
    #dates.remove(str(master_date))
    return dates

def get_stack(dates, master_date, doris_stack_dir, map_type, crop_switch=True, crop_list=[100,200,100,200], sensor='s1', swath_burst=False):
    if crop_switch:
        lines = crop_list[1]-crop_list[0]
        pixels = crop_list[3]-crop_list[2]
    else:
        lines,pixels = get_slv_arr_shape(doris_stack_dir, dates[0])
        
    res = np.zeros((lines,pixels, len(dates)), dtype = np.complex64)
    for i,date in enumerate(dates):
        if date == master_date and map_type == 'cpx':
            conitue
        elif date == master_date and map_type == 'ifg':
            conitue
        else:
            slc_arr = get_cropped_image(map_type, doris_stack_dir, date, crop_switch=crop_switch, crop_list=crop_list, sensor=sensor, swath_burst=False)
            #slc_arr = 10*np.log10(np.absolute(slc_arr))
            #plt.imshow(np.clip(slc_arr, 0, 35), cmap='gray')
            #plt.show()
        res[...,i] = slc_arr
    return res

def make_mrm(slc_arr):
    slc_arr = np.absolute(slc_arr)
    mrm = slc_arr.mean(2)
    return mrm

def plot_clipped(arr, per_min, per_max):
    print(np.nanpercentile(arr, (per_min, per_max)))
    return np.clip(arr, *np.nanpercentile(arr, (per_min, per_max)))


def read_param_file(param_file_dir):
    meta = open(param_file_dir)
    meta_dict = {}
    for i in meta.readlines():
        if (i[0]!='%'):
            j=i[:-1].split('=') # removing \n's from end of the line
            if (len(j)>1):
                if (j[1].find('%')>0):
                    j[1]=j[1][:j[1].index('%')]  #trim further after
                if (j[1][1]=="'"):
                    j[1]=j[1][2:-1]
                j=[str.strip(k) for k in j] #trimming
                meta_dict[j[0]]=j[1]
    return meta_dict

def main():
        """
    Command-line interface for processing Doris stack data.

    This script reads amplitude/interferogram/coherence data from a Doris
    stack directory, optionally crops it, and saves it as a NumPy array (.npy).
    """

    parser = argparse.ArgumentParser(description="Process Doris stack data into NumPy arrays.")
    
    # Path to Doris stack directory (VV or VH)
    parser.add_argument('--doris_stack_dir_vv', type=str, required=True,
                        help='Path to VV Doris stack directory.')
    
    # Master date in YYYYMMDD format
    parser.add_argument('--master_date', type=int, required=True,
                        help='Master date in YYYYMMDD format.')
    
    # Cropping options
    parser.add_argument('--crop_switch', action='store_true',
                        help='Enable cropping. If set, use --crop_list to specify area.')
    parser.add_argument('--crop_list', type=int, nargs=4, default=[500, 1440, 16000, 18350],
                        help='Crop region as [start_line, end_line, start_pixel, end_pixel].')
    
    # Max number of images to load
    parser.add_argument('--max_images', type=int, default=30,
                        help='Maximum number of images to load from the stack.')
    
    # Spatial averaging window size (currently unused in main)
    parser.add_argument('--sp_avg_win_size', type=int, default=3,
                        help='Spatial averaging window size.')
    
    # Map type selection: complex data, interferogram, or coherence
    parser.add_argument('--map_type', type=str, choices=['cpx', 'ifg', 'coh'], default='cpx',
                        help='Type of map to read: cpx, ifg, or coh.')
    
    # Output file name
    parser.add_argument('--output', type=str, default='output.npy',
                        help='Output NumPy file name.')

    args = parser.parse_args()

    # Get the list of dates from Doris stack
    dates = get_dates(args.doris_stack_dir_vv, args.master_date)[:args.max_images]
    print("Found dates:", dates)

    # Read the stack as a 3D NumPy array (lines, pixels, dates)
    vv_arr_stack = get_stack(
        dates, args.master_date, args.doris_stack_dir_vv,
        args.map_type, crop_switch=args.crop_switch,
        crop_list=args.crop_list, sensor='s1', swath_burst=False
    )

    # Save the stack to file
    np.save(args.output, vv_arr_stack)
    print(f"Saved stack array to {args.output}")
    
"""
Example usage from terminal:

# Process VV stack, crop to a specific region, and save as .npy
python alignsar_utils.py \
    --doris_stack_dir_vv /path/to/stack_vv \
    --master_date 20200330 \
    --crop_switch \
    --crop_list 500 1440 16000 18350 \
    --max_images 20 \
    --map_type cpx \
    --output groningen_vv_cpx.npy

# Process VH stack without cropping
python alignsar_utils.py \
    --doris_stack_dir_vv /path/to/stack_vh \
    --master_date 20200330 \
    --max_images 10 \
    --map_type ifg \
    --output groningen_vh_ifg.npy
"""
if __name__ == '__main__':
    main()




