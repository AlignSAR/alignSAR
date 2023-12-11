# Milan Lazecky, 2023 - to improve quality of geocoding. Functions work for outputs of both doris (lon, lat outputs from GEOCODE) and SNAP (dim file must contain OrthorectifiedLon/Lat layers).
import os, glob, re
import xarray as xr
import numpy as np
import rioxarray
from alignsar_utils import RI2cpx
'''
# installation:
# export PATH=$PATH:.../alignSAR/bin
# export SNAPGRAPHS=.../alignSAR/snap_graphs
# export PYTHONPATH=$PYTHONPATH:.../alignSAR/rdrcode

# now run jupyterlab

# DEMO to run in jupyter notebook
from snap_rdrcode import *
dim = '/home/espi/alignsar/geocoding/SNAP_output_sample/20220214_20220109_IW1.dim'
# to geocode the elevation.img to elevation.geo.tif
! geocode_ifg_snap.sh /home/espi/alignsar/geocoding/SNAP_output_sample/20220214_20220109_IW1.dim /path/to/temp
outpath = '/path/to/temp'
grid2rdpath = os.path.join(outpath, 'elevation.geo.tif')
rdcfilepath = snap_geo2rdc(grid2rdpath, dim, outpath)
rdc = load_tif_file(rdcfilepath)
rdc.plot()
'''

def grep1(arg,filename):
  file = open(filename, "r")
  res=''
  for line in file:
    if re.search(arg, line):
      res=line
      break
  file.close()
  return res

def load_tif_file(tif):
  '''simple function to load a tif file as xarray
  '''
  if not os.path.exists(tif):
    print('ERROR: the file does not exist')
    return False
  grid = rioxarray.open_rasterio(tif)
  grid = grid.squeeze('band')
  grid = grid.drop('band')
  return grid

def geo2rdc(grid2rdpath, latfile, lonfile, samples, lines, outpath, totif = True):
  '''main function for radarcoding - can use lat, lon files directly (e.g. as GEOCODE output from doris)
  
  Args:
    grid2rdpath (str)  path to the input geotiff file (e.g. roads.tif)
    latfile  (str)  path to the latitudes per pixel file
    lonfile  (str)  path to the longitude per pixel file
    samples  (int)  number of samples for the lon/lat files
    lines  (int)  number of lines for the lon/lat files
    outpath  (str)  path to store the output tif (will be named with 'rdc.tif', e.g. roads.rdc.tif)
    totif  (boolean)  if False, it will store only to a binary instead of tif file

  Returns:
    str  path to the output rdc file (or False if that failed)
  '''
  grid2rdpath = os.path.realpath(grid2rdpath)
  if totif:
    outrdcfile = os.path.join(outpath, os.path.basename(grid2rdpath).replace('.tif','.rdc.tif')) # or different convention?
  else:
    outrdcfile = os.path.join(outpath, os.path.basename(grid2rdpath).replace('.tif','.rdc')) # or different convention?
  outtrans = os.path.join(outpath, 'trans.dat')
  outra = os.path.join(outpath, 'outra.grd.filled.grd')
  #outra = os.path.join(outpath, 'outra.grd')
  outingeo = os.path.join(outpath, 'geo2ra.grd')
  #
  
  ############# loading data
  grid2rd = rioxarray.open_rasterio(grid2rdpath)
  grid2rd = grid2rd.squeeze('band')
  grid2rd = grid2rd.drop('band')
  grid2rd = grid2rd.rename({'x': 'lon','y': 'lat'})
  
  if not os.path.exists(outtrans):
    # load lon, lat
    lat=np.fromfile(latpath, dtype=np.float32).byteswap().reshape((lines,samples))
    lon=np.fromfile(lonpath, dtype=np.float32).byteswap().reshape((lines,samples))
    
    # transform to rg,az 
    lat=xr.DataArray(lat)
    lon=xr.DataArray(lon)
    lat=lat.rename({'dim_0': 'a','dim_1': 'r'})
    lon=lon.rename({'dim_0': 'a','dim_1': 'r'})
    lat['a']=lat.a.values #+1
    lat['r']=lat.r.values #+1
    lon['a']=lon.a.values #+1
    lon['r']=lon.r.values #+1
    
    latrav = lat.values.ravel()
    lonrav = lon.values.ravel()
    rgrav=np.tile(lat.r.values, (len(lat.a.values),1)).ravel()
    asrav=np.tile(lat.a.values, (len(lat.r.values),1)).T.ravel()
    
    # SAT2lat will end up with:
    # range, azimuth, elevation(ref to radius in PRM), lon, lat # i modified this a bit
    rall = np.column_stack([rgrav, asrav, lonrav, latrav])      # 4 cols; this is the trans.dat
    rall=rall.reshape(lat.values.shape[0], lat.values.shape[1], 4)
    rall.astype(np.float32).tofile(outtrans)
  else:
    print('using existing trans.dat file')
  
  # what to radarcode
  grid2rd.to_netcdf(outingeo)
  ############# calculation itself
  # perform the radarcoding
  cmd = 'cd {0}; convert_ll2ra.sh {1} {2} 2>/dev/null'.format(outpath, str(samples), str(lines))
  rc = os.system(cmd)
  # done in 8 seconds
  
  aa=xr.open_dataarray(outra) #'/home/espi/testconv/outra.grd.filled.grd')
  # fix the dimensions (not needed anymore...)
  #aa=aa.rename({'y':'azi','x':'rg'})
  #aa['azi']=(aa.azi.values+0.5).astype(np.uint16)
  #aa['rg']=(aa.rg.values+0.5).astype(np.uint16)
  # only store:
  if not totif:
    # final export to the binary file (-> import to the datacube etc.)
    aa.values.tofile(outrdcfile)
  else:
    #aa['x']=(aa.x.values+0.5).astype(np.uint16)
    #aa['y']=(aa.y.values+0.5).astype(np.uint16)
    aa.rio.to_raster(outrdcfile)
  if os.path.exists(outrdcfile):
    # all ok, cleaning (but keeping trans.dat for future use)
    for todel in [outra, outingeo]:
      if os.path.exists(todel):
        os.remove(todel)
    print('radarcoding finished')
    return outrdcfile
  else:
    print('ERROR during radarcoding')
    return False

def snap_geo2rdc(grid2rdpath, dim, outpath, totif=True):
  ''' This will radarcode a given geotiff (in WGS-84) to a radar-coded tif file using the SNAP OrthoRectified coordinates.

  Args:
    grid2rdpath (str)  path to the input geotiff file (e.g. roads.tif)
    dim  (str)  path to the dim file (must contain the orthorectified lat/lon layers) (e.g. SNAP_output_sample/20220214_20220109_IW1.dim)
    outpath  (str)  path to store the output tif (will be named with 'rdc.tif', e.g. roads.rdc.tif)
    totif  (boolean)  if False, it will store only to a binary instead of tif file

  Returns:
    str  path to the output rdc file (or False if that failed)
  '''
  dim = os.path.realpath(dim)
  dimpath = os.path.dirname(dim)
  datapath = os.path.join(dimpath, os.path.basename(dim).replace('.dim','.data'))
  lonpath = os.path.join(datapath, 'orthorectifiedLon.img')
  latpath = os.path.join(datapath, 'orthorectifiedLat.img')
  header=glob.glob(datapath+'/*.hdr')[0]
  samples = int(grep1('samples', header).split('=')[1].split('\n')[0])
  lines = int(grep1('lines', header).split('=')[1].split('\n')[0])
  if (not os.path.exists(latpath)) and (not os.path.exists(outtrans)):
    print('this dim file does not contain lat/lon layers. please fix')
    return False
  return geo2rdc(grid2rdpath, latpath, lonpath, samples, lines, outpath, totif = totif)
  
