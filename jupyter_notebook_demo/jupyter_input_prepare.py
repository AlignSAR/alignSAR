import os,sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import numpy.ma as ma
import numpy.linalg as LA
import math
import warnings
import os
import collections


def freadbk(path_file, line_start=1, pixel_start=1, nofLines=None, nofPixels=None, dt='float32', lines=0, pixels=0, memmap=True):
    # First use memmap to get a memory map of the full file, than extract the requested part.
    '''

    :param path_file:
    :param line_start:
    :param pixel_start:
    :param nofLines:
    :param nofPixels:
    :param dt:
    :param lines:
    :param pixels:
    :param memmap:
    :return:
    '''

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


class ResData(object):
    # This class hold metadata of a doris datafile and processing chain and is capable of reading from and writing to a
    # .res file used by the doris software.

    def __init__(self,filename='',type=''):
        # Initialize variables

        # Filename of resfile and type (single, interferogram)
        self.res_path = []
        self.res_type = ''

        # Processes, process_control and header of resfile
        self.processes = collections.OrderedDict()
        self.process_control = {}
        self.process_timestamp = {}
        self.process_time = {}
        self.header = {}

        #####################################################

        # Create a ResData object (single/interferogram)
        if type not in ['single','interferogram'] and not filename:
            warnings.warn('Define if results data is slave, master or interferogram')
            return
        else:
            self.res_type = type
        if filename:
            if not os.path.exists(filename):
                warnings.warn('This filename does not exist: ' + filename)
            else:
                self.res_path = filename
                self.res_read()
        else:
            if type == 'single':
                self.process_control = collections.OrderedDict([('readfiles', '0'),('leader_datapoints', '0'), ('precise_orbits', '0'), ('crop', '0'), ('sim_amplitude', '0'), ('master_timing' , '0'),
                                       ('oversample', '0'), ('resample', '0') , ('filt_azi', '0'), ('filt_range', '0'), ('NOT_USED' , '0')])
            elif type == 'interferogram':
                self.process_control = collections.OrderedDict([('coarse_orbits','0'),('coarse_correl','0'),('fine_coreg','0'),('timing_error','0'),('dem_assist','0'),
                                   ('comp_coregpm','0'),('interfero','0'),('coherence','0'),('comp_refphase','0'),('subtr_refphase','0'),
                                   ('comp_refdem','0'),('subtr_refdem','0'),('filtphase','0'),('unwrap','0'),('est_orbits','0'),('slant2h','0'),
                                   ('geocoding','0'),('dinsar','0'),('NOT_USED2','0')])

    def res_read(self):
        self.meta_reader()
        self.process_reader()

    def meta_reader(self):
        # This function
        with open(self.res_path) as resfile:
            splitter = ':'
            temp = collections.OrderedDict()
            row = 0
            for line in resfile:
                try:
                    ## Filter out rubbish
                    if line == '\n':
                        continue
                    elif 'Start_process_control' in line:
                        self.header = temp
                        temp = collections.OrderedDict()
                    elif 'End_process_control' in line:
                        self.process_control = temp
                        break
                    elif splitter in line and line[0] is not '|' and line[0] is not '\t' :
                        # Split line if possible and add to dictionary
                        l_split = line.split(splitter)
                        temp[l_split[0].strip()] = l_split[1].strip()
                    else:
                        name = 'row_' + str(row)
                        row += 1
                        temp[name] = [line]

                except:
                    print('Error occurred at line: ' + line)

    def process_reader(self,processes = ''):
        # This function reads random processes based on standard buildup of processes in res files.
        # leader_datapoints can be one of the processes, although it will not appear in the process_control in a .res file
        # If loc is true, it will only return the locations where different processes start.

        if not processes:
            processes = list(self.process_control.keys())

        processes.append('leader_datapoints')
        process = ''

        with open(self.res_path) as resfile:
            # Start at row zero and with empty list
            temp = collections.OrderedDict()
            row = 0
            line_no = -1
            timestamp = False
            timestamp_line = 0
            for line in resfile:
                try:
                    line_no += 1
                    # Filter out rubbish
                    if '|'in line[0]:
                        continue
                    elif '**' in line:
                        continue
                    elif line == '\n':
                        continue

                    # Check if timestamp
                    if ' *===========' in line:
                        # First line of time stamp
                        temp = collections.OrderedDict()
                        timestamp = True
                        row = 0
                        continue
                    elif ' *-----------' in line:
                        timestamp = False
                        timestamp_data = temp
                        timestamp_line = line_no + 5
                        continue

                    # Check if process
                    if '*' in line[0]:
                        if line.replace('*_Start_', '').split(':')[0].strip() in processes:
                            process = line.replace('*_Start_', '').split(':')[0].strip()
                            temp = collections.OrderedDict()
                            row = 0; space = [0]; space_r = [0,0,0,0,0,0,0,0]

                            # Finally save the timestamp if it exists
                            if line_no == timestamp_line:
                                self.process_timestamp[process] = timestamp_data
                            else:
                                self.process_timestamp[process] = ''

                        elif line.replace('* End_', '').split(':')[0] == process:
                            self.processes[process] = temp
                            temp = collections.OrderedDict()
                            process = ''
                        continue

                    # Save line
                    if timestamp is True:
                        # Save rows in timestamp
                        row_name = 'row_' + str(row)
                        temp[row_name] = line
                        if row == 1:
                            self.process_time[process] = line.split(':', 1)[1].strip()
                        row += 1
                    elif process:
                        # If we are in a process output line
                        # Split line using ':' , '=' or spaces (tables)
                        # variable space and space row define the future spacing in every processing step in a res file.

                        if process == 'coarse_orbits':
                            # Add some code for a strange exception in coarse_orbits
                            if '//' in line:
                                temp[line.split()[0]] = line.split()[1:]
                            else:
                                l_split = line.replace('=',':').split(':')
                                temp[l_split[0].strip()] = l_split[1].strip()

                        elif ':' in line:
                            l_split = line.split(':',1)
                            temp[l_split[0].strip()] = l_split[1].strip()
                        else:
                            # If the line does not contain a : it is likely a table.
                            l_split = line.replace('\t',' ').split()
                            row_name = 'row_' + str(row)
                            temp[row_name] = [l_split[i].strip() for i in range(len(l_split))]
                            row += 1

                except:
                    print('Error occurred at line: ' + line)

    def process_spacing(self,process=''):
        spacing = 0
        table_spacing = [0,0,0,0,0,0,0]

        dat = self.processes[process]

        for key in dat.keys():
            spacing = max(len(key) + 8, spacing)

            if key.startswith('row'):
                n=0
                for val in self.processes[process][key]:
                    table_spacing[n] = max(len(val) + 3, table_spacing[n])
                    n += 1
        spacing = [spacing]

        return spacing, table_spacing

    def del_process(self,process=''):
        # function deletes one or multiple processes from the corresponding res file

        if isinstance(process, basestring): # one process
            if not process in self.process_control.keys():
                warnings.warn('The requested process does not exist! (or processes are not read jet, use self.process_reader): ' + str(process))
                return
        elif isinstance(process, list): # If we use a list
            for proc in process:
                if not proc in self.process_control.keys():
                    warnings.warn('The requested process does not exist! (or processes are not read jet, use self.process_reader): ' + str(proc))
                    return
        else:
            warnings.warn('process should contain either a string of one process or a list of multiple processes: ' + str(process))

        # Now remove the process and write the file again.
        if isinstance(process, basestring): # Only one process should be removed
            self.process_control[process] = '0'
            del self.processes[process]
        else:
            for proc in process:
                self.process_control[proc] = '0'
                del self.processes[proc]

    def write(self,new_filename=''):
        # Here all the available information acquired is written to a new resfile. Generally if information is manually
        # added or removed and the file should be created or created again. (For example the readfiles for Sentinel 1
        # which are not added yet..)

        if not new_filename and not self.res_path:
            warnings.warn('Please specify filename: ' + str(new_filename))
            return
        elif not new_filename:
            new_filename = self.res_path
        if not self.process_control or not self.processes:
            warnings.warn('Every result file needs at least a process control and one process to make any sense: ' + str(new_filename))

        # Open file and write header, process control and processes
        self.res_path = new_filename
        f = open(new_filename,"w")

        # Write the header:
        if self.header:
            spacing = [40]
            for key in self.header.keys():
                if 'row' in key:       # If it is just a string
                    f.write(self.header[key][0])
                else:                   # If the key should included
                    f.write((key + ':').ljust(spacing[0]) + self.header[key] + '\n')

        # Write the process control
        for i in range(3):
            f.write('\n')
        f.write('Start_process_control\n')
        for process in self.process_control.keys():
            if process != 'leader_datapoints':  # leader_datapoints is left out in process control
                f.write((process + ':\t\t') + str(self.process_control[process]) + '\n')
        f.write('End_process_control\n')

        # Then loop through all the processes
        for process in [p for p in self.processes.keys()]:
            # First check for a timestamp and add it if needed.
            if self.process_timestamp[process]:
                for i in range(2):
                    f.write('\n')
                f.write('   *====================================================================* \n')
                for key in self.process_timestamp[process].keys():
                    f.write(self.process_timestamp[process][key])
                f.write('   *--------------------------------------------------------------------* \n')

            # Then write the process itself
            if process == 'coarse_orbits':
                spacing = [45]
                spacing_row = [15,10,15]
            else:
                spacing, spacing_row = self.process_spacing(process)
            data = self.processes[process]

            for i in range(3):
                f.write('\n')
            f.write('******************************************************************* \n')
            f.write('*_Start_' + process + ':\n')
            f.write('******************************************************************* \n')

            for line_key in self.processes[process].keys():
                if 'row' in line_key:  # If it is a table of consists of several different parts
                    line = ''.join([(' ' + data[line_key][i]).replace(' -','-').ljust(spacing_row[i]) for i in range(len(data[line_key]))])
                    f.write(line + '\n')
                elif process == 'coarse_orbits':  # the coarse orbits output is different from the others.
                    if 'Control point' in line_key: # Special case coarse orbits...
                        f.write((line_key + ' =').ljust(spacing[0]) + str(self.processes[process][line_key]) + '\n')
                    elif not isinstance(data[line_key], str): # Another special case
                        f.write(line_key.ljust(spacing_row[0]) + (data[line_key][0]).ljust(spacing_row[1]) +
                                data[line_key][1].ljust(spacing_row[2]) + ' '.join(data[line_key][2:]) + '\n')
                    elif isinstance(data[line_key], str): # Handle as in normal cases
                        f.write((line_key + ':').ljust(spacing[0]) + str(self.processes[process][line_key]) + '\n')
                else: # If it consists out of two parts
                    f.write((line_key + ':').ljust(spacing[0]) + str(self.processes[process][line_key]) + '\n')

            f.write('******************************************************************* \n')
            f.write('* End_' + process + ':_NORMAL\n')
            f.write('******************************************************************* \n')
        f.close()

        # Read the locations in the new file
        self.process_reader()

    def insert(self,data,process,variable=''):
        # This function inserts a variable or a process which does not exist at the moment
        processes = list(self.process_control.keys())
        processes.extend(['header','leader_datapoints'])

        if process not in processes:
            warnings.warn('This process does not exist for this datatype: ' + str(process))
            return

        # If a full process is added
        if not variable:
            if self.process_control[process] == '1':
                warnings.warn('This process already exists! Use the update function: ' + str(process))
                return
            elif self.process_control[process] == '0':
                self.process_control[process] = '1'
                self.processes[process] = data
                self.process_timestamp[process] = ''

        # A variable is added
        if variable:
            if variable in self.processes[process].keys():
                warnings.warn('This variable already exists! Use the update function: ' + str(variable))
                return
            elif not self.processes[process][variable]:
                self.processes[process][variable] = data

    def delete(self,process,variable=''):
        # This function deletes a variable or a process which does exist at the moment
        processes = self.process_control.keys()
        processes.extend(['header','leader_datapoints'])

        if process not in processes:
            warnings.warn('This process does not exist for this datatype: ' + str(process))
            return

        # If a full process is deleted
        if not variable:
            if self.process_control[process] == '0':
                warnings.warn('This process does not exist: ' + str(process))
                return
            elif self.process_control[process] == '1':
                self.process_control[process] = '0'
                del self.processes[process]
                del self.process_timestamp[process]

        # A variable is deleted
        if variable:
            if not variable in self.processes[process].keys():
                warnings.warn('This variable does not exist: ' + str(variable))
                return
            else:
                del self.processes[process][variable]

    def update(self,data,process,variable=''):
        # This function updates a variable or a process which does exist at the moment
        processes = self.process_control.keys()
        processes.extend(['header','leader_datapoints'])

        if not process in processes:
            warnings.warn('This process does not exist for this datatype: ' + str(process))
            return

        # If a full process is added
        if not variable:
            if self.process_control[process] == '1':
                self.processes[process] = data
            elif self.process_control[process] == '0':
                warnings.warn('This process does not exist. Use the insert function: ' + str(process))
                return
        # A variable is added
        if variable:
            if variable in self.processes[process].keys():
                self.processes[process][variable] = data
            elif not self.processes[process][variable]:
                warnings.warn('This variable does not exist. Use the insert function: ' + str(variable))
                return

    def request(self,process,variable=''):
        # This function updates a variable or a process which does exist at the moment
        processes = self.process_control.keys()
        processes.extend(['header','leader_datapoints'])

        if not process in processes:
            warnings.warn('This process does not exist for this datatype: ' + str(process))
            return

        # If a full process is added
        if not variable:
            if self.process_control[process] == '1':
                data = self.processes[process]
            elif self.process_control[process] == '0':
                warnings.warn('This process does not exist: ' + str(process))
                return
        # A variable is added
        if variable:
            if variable in self.processes[process].keys():
                data = self.processes[process][variable]
            elif not self.processes[process][variable]:
                warnings.warn('This variable does not exist: ' + str(variable))
                return

        return data

def get_dates(doris_stack_dir, master_date):
    '''

    :param doris_stack_dir:
    :param master_date:
    :return:
    '''
    #master_date = master_date.strftime("%Y%m%d")
    dates = sorted([l for l in [j for k,j,i in os.walk(doris_stack_dir)][0] if (len(l)==8)])
    #dates.remove(str(master_date))
    return dates
    return [datetime.datetime.strptime(l, '%Y%m%d') for l in dates]

def get_slv_arr_shape(doris_stack_dir, date, sensor='s1', swath='1', burst='1'):
    '''

    :param doris_stack_dir:
    :param date:
    :param sensor:
    :param swath:
    :param burst:
    :return:
    '''

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
    :param choice_amp_int:
    :param doris_stack_dir:
    :param date:
    :param amp_file_name:
    :param ifgs_file_name:
    :param crop_switch:
    :param crop_list:
    :param sensor:
    :param swath_burst:
    :param swath:
    :param burst:
    :return:
    '''

    if (sensor=='s1' and swath_burst):
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
    if (choice_amp_int == 'cpx'):
        arr = freadbk(amp_dataFilename,
                    crop_list[0],#+1,
                    crop_list[2],
                    lines,pixels,
                    'complex64', int(Naz_res), int(Nrg_res))
    if (choice_amp_int == 'ifg'):
        arr = freadbk(ifgs_dataFilename,
                    crop_list[0],#+1,
                    crop_list[2],
                    lines,pixels,
                    'complex64', int(Naz_res), int(Nrg_res))
    if (choice_amp_int == 'coh'):
        arr = freadbk(coh_dataFilename,
                    crop_list[0],#+1,
                    crop_list[2],
                    lines,pixels,
                    'float32', int(Naz_res), int(Nrg_res))
    return arr



def get_stack(dates, master_date, doris_stack_dir, map_type, crop_switch=True, crop_list=[100,200,100,200], sensor='s1', swath_burst=False):
    '''

    :param dates:
    :param doris_stack_dir:
    :param crop_switch:
    :param crop_list:
    :param sensor:
    :param swath_burst:
    :return:
    '''
    if crop_switch:
        lines = crop_list[1]-crop_list[0]
        pixels = crop_list[3]-crop_list[2]
    else:
        lines,pixels = get_slv_arr_shape(doris_stack_dir, dates[0])

    res = np.zeros((lines,pixels, len(dates)), dtype = np.complex64)
    master_date = str(master_date)
    for i,date in enumerate(dates):
        if date == master_date and map_type == 'coh':
            continue
        elif date == master_date and map_type == 'ifg':
            continue
        else:
            slc_arr = get_cropped_image(map_type, doris_stack_dir, date, crop_switch=crop_switch, crop_list=crop_list, sensor=sensor, swath_burst=False)
            res[...,i] = slc_arr
    return res


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

    # VV ifg (radians)
    vv_ifg = np.angle(get_stack(dates, master_date, doris_stack_dir_VV, 'ifg', crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1'))
    # VV coh
    vv_coh = get_stack(dates, master_date, doris_stack_dir_VV, 'coh', crop_switch=CRP_LIST, crop_list=CRP_LIST, sensor='s1').real  # imaginary part is 0

    # save the signitures into a np file
    np.save('Jupyter_input_vv_cpx_stack.npy',vv_arr_stack)
    np.save('Jupyter_input_vh_cpx_stack.npy',vh_arr_stack)
    np.save('Jupyter_input_vv_ifg_stack.npy',vv_ifg)
    np.save('Jupyter_input_vv_coh_stack.npy',vv_coh)

