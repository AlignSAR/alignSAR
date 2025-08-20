#!/usr/bin/env python3

# live code for parsing of XML TSX file into python data structures
# and from there into DORIS res file structure

from lxml import etree
import string, time, sys
# import xml.etree.ElementTree as ElementTree
# import types

def usage():
    print('\nUsage: python tsx_dump_header2doris.py tsx_XML_product > outputfile')
    print('  where tsx_XML_product is the input filename')
#    print('        outputfile      is the output DORIS resultfile')

try:
    inputFileName  = sys.argv[1]
#    outputFileName = sys.argv[2]
#    outStream      = open(outputFileName,'w')
except Exception:
    print('Unrecognized input')
    usage()
    sys.exit(1)

inTree = etree.parse(inputFileName)

# query syntax for every field
queryList = {\
             # mission info
             'mission'   : './/generalHeader/mission',\
             # imageData file
             'imageData'  : './/productComponents/imageData/file/location/filename',\
             'imageLines' : './/imageDataInfo/imageRaster/numberOfRows',\
             'imagePixels': './/imageDataInfo/imageRaster/numberOfColumns',\
              # volume info
             'volFile' : './/productComponents/annotation/file/location/filename',\
             'volID'   : './/generalHeader/itemName',\
             'volRef'  : './/generalHeader/referenceDocument',\
             # product info
             'productSpec'    : './/generalHeader/referenceDocument',\
             'productVolDate' : './/setup//IOCSAuxProductGenerationTimeUTC',\
             'productDate'    : './/generalHeader/generationTime',\
             'productFacility': './/productInfo/generationInfo/level1ProcessingFacility',\
             # scene info
             'scenePol'     : './/productInfo/acquisitionInfo//polLayer',\
             'sceneMode'    : './/setup/orderInfo/imagingMode',\
             'sceneCenLat'  : './/sceneInfo/sceneCenterCoord/lat',\
             'sceneCenLon'  : './/sceneInfo/sceneCenterCoord/lon',\
             'sceneRecords' : './/imageDataInfo/imageRaster/numberOfRows',\
             # orbit info
             'orbitABS' : './/productInfo/missionInfo/absOrbit',\
             'orbitDir' : './/productInfo/missionInfo/orbitDirection',\
             'orbitTime': './/stateVec/timeUTC',\
             'orbitX'   : './/stateVec/posX',\
             'orbitY'   : './/stateVec/posY',\
             'orbitZ'   : './/stateVec/posZ',\
             # range
             'rangeRSR'     :'.//productSpecific/complexImageInfo/commonRSF',\
             'rangeBW'      :'.//processingParameter/rangeLookBandwidth',\
             'rangeWind'    :'.//processingParameter/rangeWindowID',\
             'rangeTimePix' :'.//sceneInfo/rangeTime/firstPixel',\
             # azimuth
             'azimuthPRF'       :'.//productSpecific/complexImageInfo/commonPRF',\
             'azimuthBW'        :'.//processingParameter/azimuthLookBandwidth',\
             'azimuthWind'      :'.//processingParameter/azimuthWindowID',\
             'azimuthTimeStart' : './/sceneInfo/start/timeUTC',\
             'heading' : './/sceneInfo/headingAngle',\
             # doppler
             'dopplerTime'  :'.//dopplerEstimate/timeUTC',\
             'dopplerCoeff':'.//combinedDoppler/coefficient',\
             }

# temp variables and parameters
container     = {}
events        = ('end',)

def fast_iter_string(context):
    for event, elem in context:
        return elem.text

# works with lists
def fast_iter_list(context, tag=''):
    for event, elem in context:
        return next(elem.iterchildren(tag=tag)).text

def hms2sec(hmsString, convertFlag='int'):
    # input hmsString syntax: XX:XX:XX.xxxxxx
    secString = int(hmsString[0:2])*3600 + \
        int(hmsString[3:5])*60 + \
        float(hmsString[6:])
    if convertFlag == 'int' :
        return int(secString)
    elif convertFlag == 'float' :
        return float(secString)
    else:
        return int(secString)

for key in queryList.keys():
    try:
        vars()[key]
    except (KeyError, NameError):
        vars()[key] = []

    for nodes in inTree.findall(queryList[key]):

        if key == 'dopplerCoeff':
            vars()[key].append(nodes.text)

            exp = list(nodes.attrib.values())[0]  # Python3: dict_values -> list
            if exp == '0':
                keyTemp = 'dopplerCoeff0'
                try:
                    vars()[keyTemp]
                except (KeyError, NameError):
                    vars()[keyTemp] = []
                vars()[keyTemp].append(nodes.text)

            elif exp == '1':
                keyTemp = 'dopplerCoeff1'
                try:
                    vars()[keyTemp]
                except (KeyError, NameError):
                    vars()[keyTemp] = []
                vars()[keyTemp].append(nodes.text)

            elif exp == '2':
                keyTemp = 'dopplerCoeff2'
                try:
                    vars()[keyTemp]
                except (KeyError, NameError):
                    vars()[keyTemp] = []
                vars()[keyTemp].append(nodes.text)

            container[keyTemp] = vars()[keyTemp]

        else:
            vars()[key].append(nodes.text)

    container[key] = vars()[key]

# ---------------------------------------------------------------------------------------------------------

dummyVar = 'DUMMY'

print('\ntsx_dump_header2doris.py v1.0, doris software, 2009\n')
print('*******************************************************************')
print('*_Start_readfiles:')
print('*******************************************************************')
print('Volume file: \t\t\t\t\t%s' % container['volFile'][0])
print('Volume_ID: \t\t\t\t\t%s' % container['volID'][0])
print('Volume_identifier: \t\t\t\t%s' % container['volRef'][0])
print('Volume_set_identifier: \t\t\t\t%s' % dummyVar)
print('(Check)Number of records in ref. file: \t\t%s' % container['sceneRecords'][0])
print('SAR_PROCESSOR: \t\t\t\t\t%s' % str.split(container['productSpec'][0])[0])
print('Product type specifier: \t\t\t%s' % container['mission'][0])
print('Logical volume generating facility: \t\t%s' % container['productFacility'][0])
print('Logical volume creation date: \t\t\t%s' % container['productVolDate'][0])
print('Location and date/time of product creation: \t%s' % container['productDate'][0])
print('Scene identification: \t\t\t\tOrbit: %s %s Mode: %s' % (container['orbitABS'][0],container['orbitDir'][0],container['sceneMode'][0]))
print('Scene location: \t\t\t\tlat: %.4f lon: %.4f' % (float(container['sceneCenLat'][0]),float(container['sceneCenLon'][0])))
print('Leader file: \t\t\t\t\t%s' % container['volFile'][0])
print('Sensor platform mission identifer: \t\t%s' % container['mission'][0])
print('Scene_centre_latitude: \t\t\t\t%s' % container['sceneCenLat'][0])
print('Scene_centre_longitude: \t\t\t%s' % container['sceneCenLon'][0])
print('Scene_center_heading: \t\t\t%2.0f' % (float(container['heading'][0])))
print('Radar_wavelength (m): \t\t\t0.031')
print('First_pixel_azimuth_time (UTC):\t\t%s %s' % (time.strftime("%d-%b-%Y",time.strptime(container['azimuthTimeStart'][0].split('T')[0],"%Y-%m-%d")),container['azimuthTimeStart'][0].split('T')[1][:-1]))
print('Pulse_Repetition_Frequency (computed, Hz): \t%s' % container['azimuthPRF'][0])
print('Total_azimuth_band_width (Hz): \t\t\t%s' % container['azimuthBW'][0])
print('Weighting_azimuth: \t\t\t\t%s' % str.upper(container['azimuthWind'][0]))
print('Xtrack_f_DC_constant (Hz, early edge): \t\t%s' % container['dopplerCoeff0'][0])
print('Xtrack_f_DC_linear (Hz/s, early edge): \t\t%s' % container['dopplerCoeff1'][0])
print('Xtrack_f_DC_quadratic (Hz/s/s, early edge): \t%s' % container['dopplerCoeff2'][0])
print('Range_time_to_first_pixel (2way) (ms): \t\t%0.15f' % (float(container['rangeTimePix'][0])*1000))
print('Range_sampling_rate (computed, MHz): \t\t%0.6f' % (float(container['rangeRSR'][0])/1000000))
print('Total_range_band_width (MHz): \t\t\t%s' % (float(container['rangeBW'][0])/1000000))
print('Weighting_range: \t\t\t\t%s' % str.upper(container['rangeWind'][0]))
print('')
print('*******************************************************************')
print('Datafile: \t\t\t\t\t%s' % container['imageData'][0])
print('Number_of_lines_original: \t\t\t%s' % container['imageLines'][0])
print('Number_of_pixels_original: \t\t\t%s' % container['imagePixels'][0])
print('*******************************************************************')
print('* End_readfiles:_NORMAL')
print('*******************************************************************')
print('')
print('')
print('*******************************************************************')
print('*_Start_leader_datapoints')
print('*******************************************************************')
print(' t(s)\t\tX(m)\t\tY(m)\t\tZ(m)')
print('NUMBER_OF_DATAPOINTS: \t\t\t%s' % len(container['orbitTime']))
print('')

for i in range(len(container['orbitTime'])):
    print(' %s %s %s %s' % (hms2sec(container['orbitTime'][i].split('T')[1]),
                                  container['orbitX'][i],
                                  container['orbitY'][i],
                                  container['orbitZ'][i]))

print('')
print('*******************************************************************')
print('* End_leader_datapoints:_NORMAL')
print('*******************************************************************')
# EOF
