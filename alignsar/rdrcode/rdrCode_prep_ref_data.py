#!/usr/bin/env python3
import os
import geopandas as gpd
from pyproj import Transformer
from osgeo import gdal

def get_doris_process_bounds(process_Dir, ref_data_file):
    #Get the projection system of the ref data file
    ref_gpd = gpd.read_file(ref_data_file)
    ref_srs = ref_gpd.crs.srs.upper() 
    
    #Get the bounds of te SAR data
    datastack_dir = os.path.dirname(process_Dir)
    stack_burst_shp = os.path.join(datastack_dir, 'stackburst_coverage.shp')
    a=gpd.read_file(stack_burst_shp)
    xmin, ymin, xmax, ymax = a.geometry.total_bounds
    print(xmin, ymin, xmax, ymax)
    print(ref_srs)
    #Check the srs, convert if needed
    if(ref_srs=='EPSG:4326'):
        return xmin, ymin, xmax, ymax
    else:
        transformer = Transformer.from_crs("EPSG:4326", ref_srs)
        xmin, ymin = transformer.transform(ymin, xmin)
        xmax, ymax = transformer.transform(ymax, xmax)
    
    return xmin, ymin, xmax, ymax
    
def _to_list(str_list):
    return [i[1:-1].strip("' ") for i in str_list[1:-1].split(',')]


def prepare_poly_ref_data(params, extent):
    '''Function to prepare and export the reference polygon data for radarcoding
    Args: 
    :process_dir (str): Doris process directory.
    :data_date (str):   Date of SAR data to which reference data is radarcoded
    :sensor (str):      Sensor name.
    :ref_data_file (str): Name of the reference data file
    :layernames (list): List of layers that need to be prepared.
    :burn_value (int): Value to be filled in the rasterized files 
    
    :returns : None
    '''
    #assign parameter values
    process_dir, sensor, ref_data_file, layernames, extent, burn_value, res_x , res_y =\
    params['dorisProcessDir'], params['sensorName'], params['refDataFile'], _to_list(params['layerNames']), extent, params['burn_val'], params['resolution'], params['resolution']
    
    
    #1. Rasterize the polygon file
    for layer in layernames:
        #out_filename = os.path.join(os.path.dirname(ref_data_file), layer+'.tif')
        out_filename = os.path.join(params['int_process_dir'], layer+'.tif')
        print(out_filename)
        cmd = 'gdal_rasterize -l {} -burn {} -tr {} {} -a_nodata 0.0 -te {} -ot Float32 -of GTiff {} {}'.format(layer, burn_value, 10, 10, extent, ref_data_file, out_filename)
        
        if not os.path.exists(out_filename):
            os.system(cmd)
    
    #2. Reproject the resterized files
    for layer in layernames:
        #in_filename = os.path.join(os.path.dirname(ref_data_file), layer+'.tif')
        #out_filename = os.path.join(os.path.dirname(ref_data_file), layer+'_reproj_'+str(res_x)+'.tif')
        in_filename = os.path.join(params['int_process_dir'], layer+'.tif')
        out_filename = os.path.join(params['int_process_dir'], layer+'_reproj_'+str(res_x)+'.tif')
        
        cmd = 'gdalwarp -s_srs EPSG:28992 -t_srs EPSG:4326 -dstnodata 0.0 -tr {} {} -r bilinear -of GTiff {} {}'.format(res_x, res_y, in_filename, out_filename)
        
        if not os.path.exists(out_filename):
            os.system(cmd)
    
    #3. Convert the files to MFF raw file format
    for layer in layernames:
        #in_filename = os.path.join(os.path.dirname(ref_data_file), layer+'_reproj_'+str(res_x)+'.tif')
        in_filename = os.path.join(params['int_process_dir'], layer+'_reproj_'+str(res_x)+'.tif')
        temp_raw_output_file = in_filename[:-4]+'.r00'
        raw_output_file = in_filename[:-4]+'.raw'
        
        if not os.path.exists(raw_output_file):
            command = 'gdal_translate -of MFF ' +in_filename+' '+ raw_output_file
            os.system(command)
            mv_cmd = 'mv '+temp_raw_output_file+' '+raw_output_file
            os.system(mv_cmd)

def alter_input_file(input_file, params):
    ref_data_file, resolution, layernames =  params['refDataFile'], params['resolution'], _to_list(params['layerNames'])
    process_Dir = params['dorisProcessDir']
    data_date = params['masterDate']
    sar_dir = os.path.join(process_Dir, data_date)
    input_file_dir = os.path.dirname(process_Dir)+'/input_files/'
    input_template = os.path.join(os.getcwd(), input_file)
    code_dir = os.getcwd()
    rdrCode_input_fnames = []
    
    for layer in layernames:
        #tif_filename = os.path.join(os.path.dirname(ref_data_file), layer+'_reproj_'+str(resolution)+'.tif')
        #raw_filename = os.path.join(os.path.dirname(ref_data_file), layer+'_reproj_'+str(resolution)+'.raw')
        tif_filename = os.path.join(params['int_process_dir'], layer+'_reproj_'+str(resolution)+'.tif')
        raw_filename = os.path.join(params['int_process_dir'], layer+'_reproj_'+str(resolution)+'.raw')
        a=gdal.Open(tif_filename)
        a_gt = a.GetGeoTransform()
        
        with open(input_template, 'r+') as f:
            lines = [line for line in f.readlines()]
            
            
            #Update output filename
            out_file_raw = layer+'_radarcoded.raw'
            out_file_line = '\t'.join([lines[23].split('\t')[0], out_file_raw, '\n'])
            lines[23] = out_file_line
            
            #Update input filename
            new_file_line = '\t'.join([lines[25].split('\t')[0], raw_filename, '\n'])
            lines[25] = new_file_line
            
            #Update file shape
            
            x_extent, y_extent = a.RasterXSize, a.RasterYSize
            new_extent = '\t'.join([lines[27].split('\t')[0], (str(y_extent)+ ' '+ str(x_extent)), '\n'])
            lines[27] = new_extent
            
            #Update delta
            x_delta, y_delta = abs(a_gt[1]), abs(a_gt[5])
            new_delta = '\t'.join([lines[28].split('\t')[0], (str(y_delta)+ ' '+ str(x_delta)), '\n'])
            lines[28] = new_delta
            
            #Update UL
            x_UL, y_UL = a_gt[0], a_gt[3]
            new_UL = '\t'.join([lines[29].split('\t')[0], (str(y_UL)+ ' '+ str(x_UL)), '\n'])
            lines[29] = new_UL
            
            #print(lines)
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)
            f.close()
        
        #break
        #input file changed
        input_fname = 'input.'+layer+'_radarcode'
        os.system('cp input_radarcode {}'.format(input_file_dir+input_fname))
        rdrCode_input_fnames.append(input_file_dir+input_fname)
    
    return rdrCode_input_fnames
        
def execute_rdrcode(params, rdrCode_input_fnames):
    process_Dir = params['dorisProcessDir']
    data_date = params['masterDate']
    sar_dir = os.path.join(process_Dir, data_date)
    
    for inp_name in rdrCode_input_fnames:
        
        os.chdir(sar_dir)
        os.system('doris.rmstep.sh comp_refdem ifgs.res')
        cmd = 'doris '+ inp_name
        os.system(cmd)
        #os.chdir(code_dir)

def conv_raw(dates, master_date, doris_stack_dir):
    for date in dates:
        subt_output_file = os.path.join(doris_stack_dir, date, 'swath_1', 'burst_1', date+'.ztd_m_subt.tif')
        temp_raw_output_file = os.path.join(doris_stack_dir, date, 'swath_1', 'burst_1', date+'.ztd_m_subt.r00')
        raw_output_file = os.path.join(doris_stack_dir, date, 'swath_1', 'burst_1', date+'.ztd_m_subt.raw')
        
        command = 'gdal_translate -of MFF ' +subt_output_file+' '+ raw_output_file
        os.system(command)
        mv_cmd = 'mv '+temp_raw_output_file+' '+raw_output_file
        os.system(mv_cmd)
        #create copy of ifgs
        cp_cmd = 'cp '+os.path.join(doris_stack_dir, date, 'swath_1', 'burst_1', 'ifgs.res')+' '+os.path.join(doris_stack_dir, date, 'swath_1', 'burst_1', 'ifgs_copy.res')
        os.system(cp_cmd)
        #alter ifgs file
        os.system('doris.rmstep.sh comp_refdem '+os.path.join(doris_stack_dir, date, 'swath_1', 'burst_1', 'ifgs.res'))
        #alter input filek

def _to_list(str_list):
    return [i[1:-1].strip("' ") for i in str_list[1:-1].split(',')]


if __name__=='__main__':
    pass
    
