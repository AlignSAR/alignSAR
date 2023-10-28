# Milan Lazecky, 2023 - to avoid use of doris. Works neatly!
import os
import xarray as xr
import numpy as np
import rioxarray

dimpath = '/home/espi/alignsar/geocoding/SNAP_output_sample'
datapath = os.path.join(dimpath, '20220214_20220109_IW1.data')
lonpath = os.path.join(datapath, 'orthorectifiedLon.img')
latpath = os.path.join(datapath, 'orthorectifiedLat.img')

grid2rdpath = os.path.join(dimpath, 'elevation.tif') # what to radarcode
samples = 3045  # should read automatically from the dimpath
lines = 1072

outpath='/home/espi/testconv'
outtrans = os.path.join(outpath, 'trans.dat')
outra = os.path.join(outpath, 'outra.grd.filled.grd')
outingeo = os.path.join(outpath, 'demgeo.grd')
outrdcfile = os.path.join(outpath, 'outinrdc.img')


############# loading data
grid2rd = rioxarray.open_rasterio(grid2rdpath)
grid2rd = grid2rd.squeeze('band')
grid2rd = grid2rd.drop('band')
grid2rd = grid2rd.rename({'x': 'lon','y': 'lat'})

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

# what to radarcode
grid2rd.to_netcdf(outingeo)

############# calculation itself
# perform the radarcoding
cmd = 'cd {0}; convert_ll2ra.sh {1} {2}'.format(outpath, str(samples), str(lines))
os.system(cmd)
# done in 8 seconds

# fix the dimensions (not needed anymore...)
aa=xr.open_dataarray(outra) #'/home/espi/testconv/outra.grd.filled.grd')
#aa=aa.rename({'y':'azi','x':'rg'})
#aa['azi']=(aa.azi.values+0.5).astype(np.uint16)
#aa['rg']=(aa.rg.values+0.5).astype(np.uint16)
# only store:
# final export to the binary file (-> import to the datacube etc.)
aa.values.tofile(outrdcfile)
