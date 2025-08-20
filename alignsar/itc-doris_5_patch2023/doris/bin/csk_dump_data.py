#!/usr/bin/env python3

#-----------------------------------------------------------------#
# A python3 code for cropping Cosmo-skymed HDF5 file for Doris.
#
# Author: TUDelft - 2010
# Maintainer: Prabu Dheenathayalan
# Updated for Python3 compatibility
#-----------------------------------------------------------------#

import os, sys, time
import numpy, h5py  # for hdf5 python support
from array import array

codeRevision = 1.0   # this code revision number

def usage():
    print('INFO    : @(#)Doris InSAR software, $Revision: %s $, $Author: TUDelft $' % codeRevision)
    print()
    print('Usage   : csk_dump_data.py <inputfile> <outputfile> [l0 lN p0 pN] [-res RESFILE]')
    print()
    print('          inputfile         is the input Cosmo-skymed HDF5 filename : master.hd5')
    print('          outputfile        is the output filename                  : master.slc')
    print('          l0                is the first azimuth line (starting at 1)')
    print('          lN                is the last azimuth line')
    print('          p0                is the first range pixel (starting at 1)')
    print('          pN                is the last range pixel')
    print('          RESFILE           DORIS result file that is to be updated for crop metadata (optional)')
    print()
    print('          This software is part of Doris InSAR software package.\n')
    print('(c) 1999-2010 Delft University of Technology, the Netherlands.\n')

try:
    inputFileName  = sys.argv[1]
    outputFileName = sys.argv[2]
except Exception:
    print('\nError   : Unrecognized input or missing arguments\n\n')
    usage()
    sys.exit(1)

# accessing the HDF5 product file
f = h5py.File(inputFileName, 'r')
if '/S01/SBI' not in f:
    print('ERROR: Wrong HDF5 format!')
    sys.exit(1)

sbi = f['/S01/SBI']
data = array('h')
data = sbi[:,:,:]
Number_of_lines_original = sbi.shape[0]
Number_of_pixels_original = sbi.shape[1]
sbi = None

resFile = None
for element in range(len(sys.argv)):
    option = sys.argv[element]
    if option == '-res':
        resFile = str(sys.argv[element+1])
        del sys.argv[element+1]
        del sys.argv[element]
        break

if len(sys.argv) == 3:
    outputWinFirstLine = None
    outputWinLastLine  = None
    outputWinFirstPix  = None
    outputWinLastPix   = None
elif len(sys.argv) > 3 and len(sys.argv) < 9:
    outputWinFirstLine = int(sys.argv[3]) - 1
    outputWinLastLine  = int(sys.argv[4])
    outputWinFirstPix  = int(sys.argv[5]) - 1
    outputWinLastPix   = int(sys.argv[6])
elif len(sys.argv) > 3 and len(sys.argv) < 7:
    print('Unrecognized input')
    usage()
    sys.exit(1)
else:
    outputWinFirstLine = None
    outputWinLastLine  = None
    outputWinFirstPix  = None
    outputWinLastPix   = None

if outputWinFirstLine is None or outputWinLastLine is None or outputWinFirstPix is None or outputWinLastPix is None:
    print('%s: running failed: crop size unknown !' % (sys.argv[0]))
    sys.exit(1)

if outputWinLastLine-outputWinFirstLine+1 < 0 or outputWinLastPix-outputWinFirstPix+1 <= 0:
    print('%s running failed: crop dimensions are not valid !' % (sys.argv[0]))
    sys.exit(1)

# compute crop dimensions
if outputWinFirstLine == 0:
    NLinesCrop = outputWinLastLine
elif outputWinFirstLine+1 == outputWinLastLine:
    NLinesCrop = 1
else:
    NLinesCrop = outputWinLastLine-outputWinFirstLine

if outputWinFirstPix == 0:
    NPixelsCrop = outputWinLastPix
elif outputWinFirstPix+1 == outputWinLastPix:
    NPixelsCrop = 1
else:
    NPixelsCrop = outputWinLastPix-outputWinFirstPix

# write the data in Complex Short format (CInt16)
temp = 0
fid = open(outputFileName, "wb")
for n in range(outputWinFirstLine, outputWinLastLine):
    if int((outputWinLastLine-outputWinFirstLine)/10) <= 0 and temp < 10:
        sys.stdout.write("0...10...20...30...40...50...60...70...80...90...")
        temp = 10
    elif (outputWinLastLine-outputWinFirstLine) > 0 and n % int((outputWinLastLine-outputWinFirstLine)/10) == 0 and temp < 10:
        sys.stdout.write('%s...' % (temp*10))
        temp = temp+1
    data_line = data[n, list(range(outputWinFirstPix, outputWinLastPix)), :]
    data_line.tofile(fid)
    data_line = None
sys.stdout.write("100% - done.\n")
fid.close()

# explicitly writing the hdr file
headerFileStream = open(os.path.splitext(outputFileName)[0]+'.hdr','w')
headerFileStream.write('IMAGE_FILE_FORMAT = MFF\n')
headerFileStream.write('FILE_TYPE = IMAGE\n')
headerFileStream.write('IMAGE_LINES = %s\n' % (NLinesCrop))
headerFileStream.write('LINE_SAMPLES = %s\n' % (NPixelsCrop))
headerFileStream.write('FILE_TYPE = IMAGE\n')
headerFileStream.write('BYTE_ORDER = LSB\n')
headerFileStream.write('END\n')

# check whether the resfile exist
if resFile is not None:
    print(resFile)
    headerFileStream = open(os.path.splitext(outputFileName)[0]+'.hdr','r')
    for line in headerFileStream:
        pair = line.split()
        if len(pair) > 1:
            vars()[pair[0]] = pair[2]

    outStream = open(resFile,'a')
    outStream.write('\n')
    outStream.write('*******************************************************************\n')
    outStream.write('*_Start_crop:                          HDF5 \n')
    outStream.write('*******************************************************************\n')
    outStream.write('Data_output_file:                      %s\n' % outputFileName)
    outStream.write('Data_output_format:                    complex_short\n')

    if outputWinFirstPix is not None:
        outStream.write('First_line (w.r.t. original_image):    %s\n' % (outputWinFirstLine+1))
        outStream.write('Last_line (w.r.t. original_image):     %s\n' % outputWinLastLine)
        outStream.write('First_pixel (w.r.t. original_image):   %s\n' % (outputWinFirstPix+1))
        outStream.write('Last_pixel (w.r.t. original_image):    %s\n' % outputWinLastPix)
    else:
        outStream.write('First_line (w.r.t. original_image):    1\n')
        outStream.write('Last_line (w.r.t. original_image):     %s\n' % IMAGE_LINES)
        outStream.write('First_pixel (w.r.t. original_image):   1\n')
        outStream.write('Last_pixel (w.r.t. original_image):    %s\n' % LINE_SAMPLES)

    outStream.write('*******************************************************************\n')
    outStream.write('* End_crop:_NORMAL\n')
    outStream.write('*******************************************************************\n')
    outStream.write('\n')
    outStream.write('    Current time: %s\n' % time.asctime())
    outStream.write('\n')
    outStream.close()

    # replace crop tag in result file
    sourceText   = "crop:                       0"
    replaceText  = "crop:                       1"
    inputStream  = open(resFile,'r')
    textStream   = inputStream.read()
    inputStream.close()
    outputStream = open(resFile, "w")
    outputStream.write(textStream.replace(sourceText, replaceText))
    outputStream.close()

#EOF

