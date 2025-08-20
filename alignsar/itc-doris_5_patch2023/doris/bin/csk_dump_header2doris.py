#!/usr/bin/env python3

#-----------------------------------------------------------------#
# A python3 code for parsing CSK HDF5 file into python data structures
# and from there into DORIS res file structure
#
# Author: TUDelft - 2010
# Maintainer: Prabu Dheenathayalan
# Updated for Python3 compatibility
#-----------------------------------------------------------------#

import numpy, h5py, sys, math, time

codeRevision = 1.0   # this code revision number

def usage():
    print('INFO    : @(#)Doris InSAR software, $Revision: %s $, $Author: TUDelft $' % codeRevision)
    print()
    print('Usage   : python csk_dump_header2doris.py csk_HDF5_product > OutputFileName')
    print('                               where csk_HDF5_product is the input filename')
    print()
    print('          This software is part of Doris InSAR software package.\n')
    print('(c) 1999-2010 Delft University of Technology, the Netherlands.\n')

try:
    inputFileName  = sys.argv[1]
except IndexError:
    print('\nError   : Unrecognized input or missing arguments\n\n')
    usage()
    sys.exit(1)

# accessing the HDF5 product file
f = h5py.File(inputFileName, 'r')
s01 = f['/S01']
sbi = s01['SBI']
b001 = s01['B001']
qlk = s01['QLK']

# reading the attributes  
VolumeFile = f.attrs['Product Filename']
Volume_ID = f.attrs['Programmed Image ID'] 
Volume_identifier = f.attrs['Product Specification Document'] 
Volume_set_identifier = 'dummy'
NumberOfRecordsInRefFile = 'dummy'

SAR_PROCESSOR = f.attrs['L1A Software Version']
ProductTypeSpecifier = f.attrs['Product Type']
LogicalVolumeGeneratingFacility = f.attrs['Processing Centre']
LogicalVolumeCreationDate = 'dummy'
LocationAndDateTimeOfProductCreation = f.attrs['Product Generation UTC'] 

SceneIdentification = f.attrs['Orbit Number']
orbitDir = f.attrs['Orbit Direction']
sceneMode = f.attrs['Acquisition Mode']
SceneLocation = 'dummy'
LeaderFile = f.attrs['Product Filename']
SAT_ID = f.attrs['Satellite ID']
SensorPlatformMissionIdentifier = f.attrs['Mission ID']
SceneCentreGeodeticCoordinates = f.attrs['Scene Centre Geodetic Coordinates']

Scene_centre_latitude = SceneCentreGeodeticCoordinates[0]
Scene_centre_longitude = SceneCentreGeodeticCoordinates[1]
Scene_centre_heading = f.attrs['Scene Orientation']
Radar_wavelength = f.attrs['Radar Wavelength']
Radar_frequency = f.attrs['Radar Frequency']
Swath_no = f.attrs['Subswaths Number']
Polarisation = s01.attrs['Polarisation']
ReferenceUTC = f.attrs['Reference UTC']
relZDAFTime = sbi.attrs['Zero Doppler Azimuth First Time']

if int(ReferenceUTC[20:]) * 10 != 0:
    ZDAFTime_msecsOfDay = round((int(ReferenceUTC[11:13])*3600 +
                                 int(ReferenceUTC[14:16])*60 +
                                 int(ReferenceUTC[17:19]) +
                                 pow(int(ReferenceUTC[20:])*10, (-(len(ReferenceUTC)-20))) +
                                 relZDAFTime) * 1000)
else:
    ZDAFTime_msecsOfDay = round((int(ReferenceUTC[11:13])*3600 +
                                 int(ReferenceUTC[14:16])*60 +
                                 int(ReferenceUTC[17:19]) +
                                 relZDAFTime) * 1000)

ZDAFTime_HH = math.floor(ZDAFTime_msecsOfDay/(60*60*1000))
ZDAFTime_MM = math.flo_
