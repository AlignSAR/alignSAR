import os,sys
from resdata import ResData
import numpy as np
from scipy import signal
import numpy.ma as ma


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
    return [datetime.datetime.strptime(l, '%Y%m%d') for l in dates]

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

if __name__=='__main__':
    doris_stack_dir_VV = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vv/'
    doris_stack_dir_VH = '/media/anurag/SSD_1/anurag/PhD_Project/Doris_Processing/Doris_Processing_36_Groningen/new_datastack/stack_vh/'
    #paz_doris_stack = '/media/anurag/AK_WD/PAZ_Processing/stack'
    master_date = 20200330#'20220214'#'20170117'
    CROPPING = True
    CRP_LIST = [500, 1440, 16000, 18350]#[2000, 3500, 8500, 10000]#
    MAX_IMAGES = 30
    SP_AVG_WIN_SIYE = 3
    map_type = 'cpx'  # 'cpx', 'ifg', 'coh'
    
    #Get the dates
    dates = get_dates(paz_doris_stack, master_date)[:MAX_IMAGES]
    print(dates)
    #Extract the stack array
    vv_arr_stack = get_stack(dates, master_date, doris_stack_dir_VV, map_type, crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1', swath_burst=False)
    vh_arr_stack = get_stack(dates, master_date, doris_stack_dir_VH, map_type, crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1', swath_burst=False)
    
    np.save('groningen_vv_cpx.npy', vv_arr_stack)
    np.save('groningen_vh_cpx.npy', vh_arr_stack)


